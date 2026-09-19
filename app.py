import threading
from pathlib import Path

import customtkinter as ctk
import pandas as pd
from tkinter import messagebox

from scraper import refresh_leaderboard, get_csv_path


# =========================================================
# GUI settings
# =========================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


REGIONS = {
    "Americas (US)": "US",
    "Europe (EU)": "EU",
    "Asia-Pacific (AP)": "AP"
}


MODES = {
    "Battlegrounds": "battlegrounds",
    "Battlegrounds Duos": "battlegroundsduo"
}


# =========================================================
# Main Application
# =========================================================

class HearthstoneTracker(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title("Hearthstone Rating Finder")
        self.geometry("620x650")
        self.resizable(False, False)

        self.create_widgets()

        # Load information for default leaderboard
        self.load_leaderboard_info()


    # =====================================================
    # Build GUI
    # =====================================================

    def create_widgets(self):

        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="Hearthstone Rating Finder",
            font=("Arial", 28, "bold")
        )

        self.title_label.pack(
            pady=(30, 20)
        )


        # -------------------------
        # Server
        # -------------------------

        self.server_label = ctk.CTkLabel(
            self,
            text="Server",
            font=("Arial", 15)
        )

        self.server_label.pack()

        self.server_menu = ctk.CTkOptionMenu(
            self,
            values=list(REGIONS.keys()),
            command=self.on_leaderboard_change,
            width=300
        )

        self.server_menu.set(
            "Americas (US)"
        )

        self.server_menu.pack(
            pady=(5, 15)
        )


        # -------------------------
        # Mode
        # -------------------------

        self.mode_label = ctk.CTkLabel(
            self,
            text="Game Mode",
            font=("Arial", 15)
        )

        self.mode_label.pack()

        self.mode_menu = ctk.CTkOptionMenu(
            self,
            values=list(MODES.keys()),
            command=self.on_leaderboard_change,
            width=300
        )

        self.mode_menu.set(
            "Battlegrounds Duos"
        )

        self.mode_menu.pack(
            pady=(5, 20)
        )


        # -------------------------
        # Player name
        # -------------------------

        self.player_label = ctk.CTkLabel(
            self,
            text="Player Name",
            font=("Arial", 15)
        )

        self.player_label.pack()

        self.player_entry = ctk.CTkEntry(
            self,
            width=300,
            height=38,
            placeholder_text="Enter exact Hearthstone ID"
        )

        self.player_entry.pack(
            pady=(5, 15)
        )

        # Press Enter = search
        self.player_entry.bind(
            "<Return>",
            lambda event: self.search_player()
        )


        # -------------------------
        # Search button
        # -------------------------

        self.search_button = ctk.CTkButton(
            self,
            text="Search Player",
            width=200,
            height=40,
            command=self.search_player
        )

        self.search_button.pack(
            pady=5
        )


        # -------------------------
        # Result
        # -------------------------

        self.result_name = ctk.CTkLabel(
            self,
            text="",
            font=("Arial", 21, "bold")
        )

        self.result_name.pack(
            pady=(25, 5)
        )


        self.result_rating = ctk.CTkLabel(
            self,
            text="",
            font=("Arial", 26, "bold")
        )

        self.result_rating.pack(
            pady=2
        )


        self.result_rank = ctk.CTkLabel(
            self,
            text="",
            font=("Arial", 18)
        )

        self.result_rank.pack(
            pady=2
        )


        # -------------------------
        # Last updated
        # -------------------------

        self.updated_label = ctk.CTkLabel(
            self,
            text="",
            font=("Arial", 12)
        )

        self.updated_label.pack(
            pady=(20, 10)
        )


        # -------------------------
        # Refresh button
        # -------------------------

        self.refresh_button = ctk.CTkButton(
            self,
            text="Refresh Leaderboard",
            width=200,
            height=38,
            command=self.start_refresh
        )

        self.refresh_button.pack(
            pady=5
        )


        # -------------------------
        # Progress bar
        # -------------------------

        self.progress_bar = ctk.CTkProgressBar(
            self,
            width=350
        )

        self.progress_bar.set(0)

        self.progress_bar.pack(
            pady=(15, 5)
        )


        self.status_label = ctk.CTkLabel(
            self,
            text="",
            font=("Arial", 12)
        )

        self.status_label.pack()


    # =====================================================
    # Get current selection
    # =====================================================

    def get_selection(self):

        region_name = (
            self.server_menu.get()
        )

        mode_name = (
            self.mode_menu.get()
        )

        region = (
            REGIONS[region_name]
        )

        leaderboard_id = (
            MODES[mode_name]
        )

        return region, leaderboard_id


    # =====================================================
    # Load leaderboard CSV
    # =====================================================

    def load_dataframe(self):

        region, leaderboard_id = (
            self.get_selection()
        )

        csv_file = get_csv_path(
            region,
            leaderboard_id
        )

        if not csv_file.exists():
            return None

        df = pd.read_csv(
            csv_file,
            dtype={
                "accountid": str
            }
        )

        return df


    # =====================================================
    # Search player
    # =====================================================

    def search_player(self):

        player_name = (
            self.player_entry
            .get()
            .strip()
        )

        if not player_name:

            self.result_name.configure(
                text="Enter a player name."
            )

            self.result_rating.configure(
                text=""
            )

            self.result_rank.configure(
                text=""
            )

            return


        df = self.load_dataframe()

        if df is None:

            self.result_name.configure(
                text="Leaderboard not available"
            )

            self.result_rating.configure(
                text=""
            )

            self.result_rank.configure(
                text="Please refresh the leaderboard first."
            )

            messagebox.showwarning(
                "Leaderboard Not Downloaded",
                "No local leaderboard data was found for the selected server and game mode.\n\n"
                "Please click 'Refresh Leaderboard' first."
            )

            return


        # Exact, case-sensitive matching
        result = df[
            df["accountid"] == player_name
        ]


        if result.empty:

            self.result_name.configure(
                text=player_name
            )

            self.result_rating.configure(
                text="Rating < 8000"
            )

            self.result_rank.configure(
                text="Not on leaderboard"
            )

        else:

            player = result.iloc[0]

            rating = int(
                player["rating"]
            )

            rank = int(
                player["rank"]
            )

            self.result_name.configure(
                text=player["accountid"]
            )

            self.result_rating.configure(
                text=f"Rating: {rating:,}"
            )

            self.result_rank.configure(
                text=f"Rank: #{rank:,}"
            )


    # =====================================================
    # Load last-updated information
    # =====================================================

    def load_leaderboard_info(self):

        df = self.load_dataframe()

        if df is None:

            self.updated_label.configure(
                text="Leaderboard not downloaded — click Refresh Leaderboard"
            )

            return

        season_id = df["season_id"].iloc[0]
        updated_at = df["scraped_at"].iloc[0]

        self.updated_label.configure(
            text=(
                f"Season {season_id}  |  "
                f"Last updated: {updated_at}"
            )
        )


    # =====================================================
    # Selection changed
    # =====================================================

    def on_leaderboard_change(
        self,
        _=None
    ):

        self.result_name.configure(
            text=""
        )

        self.result_rating.configure(
            text=""
        )

        self.result_rank.configure(
            text=""
        )

        self.progress_bar.set(0)

        self.status_label.configure(
            text=""
        )

        self.load_leaderboard_info()


    # =====================================================
    # Start refresh in background thread
    # =====================================================

    def start_refresh(self):

        self.refresh_button.configure(
            state="disabled"
        )

        self.search_button.configure(
            state="disabled"
        )

        self.progress_bar.set(0)

        self.status_label.configure(
            text="Connecting to Blizzard..."
        )
        
        self.result_name.configure(
            text=""
        )

        self.result_rating.configure(
            text=""
        )

        self.result_rank.configure(
            text=""
        )

        thread = threading.Thread(
            target=self.refresh_worker,
            daemon=True
        )

        thread.start()


    # =====================================================
    # Background refresh
    # =====================================================

    def refresh_worker(self):

        region, leaderboard_id = (
            self.get_selection()
        )

        try:

            result = refresh_leaderboard(
                region=region,
                leaderboard_id=leaderboard_id,
                progress_callback=self.update_progress
            )

            self.after(
                0,
                self.refresh_complete,
                result
            )

        except Exception as error:

            self.after(
                0,
                self.refresh_failed,
                str(error)
            )


    # =====================================================
    # Update progress
    # =====================================================

    def update_progress(
        self,
        current_page,
        total_pages,
        player_count
    ):

        progress = (
            current_page
            / total_pages
        )

        def update():

            self.progress_bar.set(
                progress
            )

            self.status_label.configure(
                text=(
                    f"Page {current_page}/{total_pages} "
                    f"— {player_count} players"
                )
            )

        self.after(
            0,
            update
        )


    # =====================================================
    # Refresh complete
    # =====================================================

    def refresh_complete(
        self,
        result
    ):

        self.progress_bar.set(1)

        self.status_label.configure(
            text=(
                f"Update complete — "
                f"{result['players']} players"
            )
        )

        self.updated_label.configure(
            text=(
                f"Season {result['season_id']}  |  "
                f"Last updated: {result['updated_at']}"
            )
        )

        self.refresh_button.configure(
            state="normal"
        )

        self.search_button.configure(
            state="normal"
        )


    # =====================================================
    # Refresh failed
    # =====================================================

    def refresh_failed(
        self,
        error_message
    ):

        # Reset progress bar
        self.progress_bar.set(0)

        # Update status
        self.status_label.configure(
            text="Leaderboard refresh failed."
        )

        # Clear old player result
        self.result_name.configure(
            text=""
        )

        self.result_rating.configure(
            text=""
        )

        self.result_rank.configure(
            text=""
        )

        # Re-enable buttons
        self.refresh_button.configure(
            state="normal"
        )

        self.search_button.configure(
            state="normal"
        )

        # Show error popup
        messagebox.showerror(
            "Network Error",
            "Unable to download the leaderboard from Blizzard.\n\n"
            "Please check your internet connection and try again.\n\n"
            f"Technical details:\n{error_message}"
        )


# =========================================================
# Start application
# =========================================================

if __name__ == "__main__":

    app = HearthstoneTracker()

    app.mainloop()