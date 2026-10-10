# HearthstoneTracker 使用说明

HearthstoneTracker 是一个用于查询《炉石传说》酒馆战棋公开排行榜分数的小工具。

## 支持内容

### 服务器
- Americas（US）
- Europe（EU）
- Asia-Pacific（AP）

### 游戏模式
- Battlegrounds
- Battlegrounds Duos

程序会自动识别当前赛季。

---

## Windows 使用方法

如果你收到的是：

`HearthstoneTracker.exe`

无需安装 Python、VS Code 或其他依赖。

直接双击：

`HearthstoneTracker.exe`

即可打开软件。

---

## 第一次使用

1. 打开 HearthstoneTracker
2. 选择服务器
3. 选择游戏模式
4. 点击 `Refresh Leaderboard`
5. 等待排行榜更新完成
6. 输入玩家名称
7. 点击 `Search Player`

刷新完成后，程序会把排行榜数据保存在本地。

之后查询玩家时会直接读取本地数据，因此速度很快。

---

## 查询玩家

玩家名称采用**精确匹配**。

例如：

`Epicman`

与下面这些名称会被视为不同：

- `epicman`
- `EPICMAN`
- `Epic man`

请按照游戏中显示的名称准确输入。

如果找到玩家，程序会显示：

- Player Name
- Rank
- Rating

如果排行榜已经成功刷新，但没有找到该玩家，程序会显示：

`Rating < 8000`

这表示该玩家没有出现在当前公开的 8000+ 排行榜中。

---

## 更新排行榜

建议每次开始游戏前点击一次：

`Refresh Leaderboard`

程序会自动：

1. 识别当前赛季
2. 下载当前服务器和模式的公开排行榜
3. 更新本地排行榜数据
4. 更新 Last Updated 时间

界面中会显示类似：

`Season 19 | Last updated: 2026-09-19 18:00:00`

---

## 如果提示排行榜没有下载

如果看到类似：

`Please refresh the leaderboard first.`

说明当前选择的服务器和游戏模式还没有本地数据。

点击：

`Refresh Leaderboard`

等待更新完成后再进行查询。

---

## 网络错误

如果刷新过程中出现 `Network Error`：

1. 检查网络连接
2. 确认 Blizzard 排行榜可以正常访问
3. 稍后重新点击 `Refresh Leaderboard`

---


## 数据说明

本工具使用 Blizzard 官方 Hearthstone Leaderboards 的公开排行榜数据。

排行榜会随着玩家分数和排名变化，因此查询结果取决于最后一次刷新时间。
