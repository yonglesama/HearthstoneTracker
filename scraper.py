import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
import sys


# ==========================================
# Basic settings
# ==========================================

BASE_URL = (
    "https://hearthstone.blizzard.com/"
    "en-us/api/community/leaderboardsData"
)

REQUEST_TIMEOUT = 15
REQUEST_DELAY = 0.2


# ==========================================
# Project folders
# ==========================================

def get_app_folder():
    """
    Return the folder containing the application.

    When running as .py:
        use the project folder.

    When running as .exe:
        use the folder containing the .exe.
    """

    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parent


PROJECT_FOLDER = get_app_folder()
DATA_FOLDER = PROJECT_FOLDER / "data"


# ==========================================
# CSV path
# ==========================================

def get_csv_path(region, leaderboard_id):
    """
    Return CSV path for a specific
    region and leaderboard.
    """

    filename = f"{region}_{leaderboard_id}.csv"

    return DATA_FOLDER / filename


# ==========================================
# Create HTTP session
# ==========================================

def create_session():
    """
    Create reusable HTTP session.
    """

    session = requests.Session()

    session.headers.update({
        "User-Agent": "HearthstoneTracker/1.0",
        "Accept": "application/json"
    })

    return session


# ==========================================
# Download one page
# ==========================================

def fetch_page(
    session,
    region,
    leaderboard_id,
    page_number,
    season_id=None
):
    """
    Download one leaderboard page.

    If season_id is None, Blizzard will
    return the current season.
    """

    params = {
        "region": region,
        "leaderboardId": leaderboard_id,
        "page": page_number
    }

    # Only add seasonId after we know it
    if season_id is not None:
        params["seasonId"] = season_id

    response = session.get(
        BASE_URL,
        params=params,
        timeout=REQUEST_TIMEOUT
    )

    response.raise_for_status()

    return response.json()


# ==========================================
# Detect current season
# ==========================================

def detect_current_season(
    session,
    region,
    leaderboard_id
):
    """
    Request page 1 without seasonId.

    Blizzard returns the current seasonId
    in the JSON response.

    Returns:
        season_id
        first_page_data
    """

    data = fetch_page(
        session=session,
        region=region,
        leaderboard_id=leaderboard_id,
        page_number=1,
        season_id=None
    )

    season_id = data.get("seasonId")

    if season_id is None:
        raise ValueError(
            "Could not detect the current season."
        )

    season_id = int(season_id)

    return season_id, data


# ==========================================
# Download complete leaderboard
# ==========================================

def fetch_all_players(
    region,
    leaderboard_id,
    progress_callback=None
):
    """
    Detect the current season and download
    all leaderboard pages.
    """

    session = create_session()

    try:

        # ----------------------------------
        # Step 1: Detect current season
        # ----------------------------------

        season_id, first_page = (
            detect_current_season(
                session=session,
                region=region,
                leaderboard_id=leaderboard_id
            )
        )

        leaderboard = first_page["leaderboard"]

        total_pages = (
            leaderboard["pagination"]["totalPages"]
        )

        players = list(
            leaderboard["rows"]
        )

        # ----------------------------------
        # Progress: page 1
        # ----------------------------------

        if progress_callback:

            progress_callback(
                1,
                total_pages,
                len(players)
            )

        # ----------------------------------
        # Step 2: Remaining pages
        # ----------------------------------

        for page_number in range(
            2,
            total_pages + 1
        ):

            time.sleep(
                REQUEST_DELAY
            )

            # IMPORTANT:
            # Lock all remaining requests
            # to the detected season.
            data = fetch_page(
                session=session,
                region=region,
                leaderboard_id=leaderboard_id,
                page_number=page_number,
                season_id=season_id
            )

            rows = (
                data["leaderboard"]["rows"]
            )

            players.extend(
                rows
            )

            if progress_callback:

                progress_callback(
                    page_number,
                    total_pages,
                    len(players)
                )

        return (
            players,
            total_pages,
            season_id
        )

    finally:

        session.close()


# ==========================================
# Convert to DataFrame
# ==========================================

def create_dataframe(
    players,
    region,
    leaderboard_id,
    season_id
):
    """
    Convert raw leaderboard records into
    a clean DataFrame.
    """

    df = pd.DataFrame(
        players
    )

    required_columns = {
        "rank",
        "accountid",
        "rating"
    }

    missing_columns = (
        required_columns
        - set(df.columns)
    )

    if missing_columns:

        raise ValueError(
            f"Missing expected columns: "
            f"{missing_columns}"
        )

    # Keep useful fields
    df = df[
        [
            "rank",
            "accountid",
            "rating"
        ]
    ].copy()

    # Metadata
    df["region"] = region

    df["leaderboard_id"] = (
        leaderboard_id
    )

    df["season_id"] = (
        season_id
    )

    updated_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    df["scraped_at"] = (
        updated_at
    )

    # Sort
    df = (
        df
        .sort_values("rank")
        .reset_index(drop=True)
    )

    return df, updated_at


# ==========================================
# Save CSV
# ==========================================

def save_csv(
    df,
    region,
    leaderboard_id
):
    """
    Save leaderboard DataFrame to CSV.
    """

    DATA_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )

    csv_file = get_csv_path(
        region,
        leaderboard_id
    )

    df.to_csv(
        csv_file,
        index=False,
        encoding="utf-8-sig"
    )

    return csv_file


# ==========================================
# Main function used by GUI
# ==========================================

def refresh_leaderboard(
    region,
    leaderboard_id,
    progress_callback=None
):
    """
    Automatically detect current season,
    download leaderboard and save CSV.
    """

    (
        players,
        total_pages,
        season_id
    ) = fetch_all_players(
        region=region,
        leaderboard_id=leaderboard_id,
        progress_callback=progress_callback
    )

    df, updated_at = create_dataframe(
        players=players,
        region=region,
        leaderboard_id=leaderboard_id,
        season_id=season_id
    )

    csv_file = save_csv(
        df=df,
        region=region,
        leaderboard_id=leaderboard_id
    )

    return {
        "players": len(df),
        "total_pages": total_pages,
        "season_id": season_id,
        "updated_at": updated_at,
        "csv_file": csv_file
    }


# ==========================================
# Standalone test
# ==========================================

if __name__ == "__main__":

    def print_progress(
        current_page,
        total_pages,
        player_count
    ):

        print(
            f"Page {current_page}/{total_pages} "
            f"- {player_count} players"
        )


    result = refresh_leaderboard(
        region="US",
        leaderboard_id="battlegroundsduo",
        progress_callback=print_progress
    )

    print()
    print("Update complete!")
    print(
        f"Season: {result['season_id']}"
    )
    print(
        f"Players: {result['players']}"
    )
    print(
        f"Pages: {result['total_pages']}"
    )
    print(
        f"Updated: {result['updated_at']}"
    )
    print(
        f"File: {result['csv_file']}"
    )