import flet as ft
import sqlite3
import requests
import random
 
conn = sqlite3.connect("games.db", check_same_thread=False)
cursor = conn.cursor()
 
cursor.execute("""
CREATE TABLE IF NOT EXISTS Game (
    id INTEGER PRIMARY KEY,
    title TEXT,
    genre TEXT,
    platform TEXT,
    image TEXT,
    description TEXT,
    url TEXT,
    worth TEXT
)
""")
conn.commit()
 
 
def ensureColumns():
    columns = [
        ("description", "TEXT"),
        ("url", "TEXT"),
        ("users", "TEXT"),
        ("status", "TEXT"),
        ("published_date", "TEXT"),
        ("instructions", "TEXT"),
        ("favorite", "INTEGER DEFAULT 0"),
    ]
 
    for colName, colType in columns:
        try:
            cursor.execute(f"ALTER TABLE Game ADD COLUMN {colName} {colType}")
            conn.commit()
        except:
            pass
 
 
ensureColumns()
 
 
def main(page: ft.Page):
    page.title = "Free Games"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
 
    output = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
 
    def filterPlatformPC(e):
        output.controls.clear()
        games = cursor.execute("SELECT * FROM Game").fetchall()
 
        for g in games:
            if "PC" in g[3]:
                output.controls.append(gameCard(g))
 
        page.update()
 
    def filterGenreDLC(e):
        output.controls.clear()
        games = cursor.execute("SELECT * FROM Game").fetchall()
 
        for g in games:
            if "DLC" in g[2]:
                output.controls.append(gameCard(g))
 
        page.update()
 
    def filterWorthFree(e):
        output.controls.clear()
        games = cursor.execute("SELECT * FROM Game").fetchall()
 
        for g in games:
            if g[7] == "N/A":
                output.controls.append(gameCard(g))
 
        page.update()
 
    def filterWorthPaid(e):
        output.controls.clear()
        games = cursor.execute("SELECT * FROM Game").fetchall()
 
        for g in games:
            if g[7] != "N/A":
                output.controls.append(gameCard(g))
 
        page.update()
 
    def addToFavorites(e):
        game_id = e.control.data
        cursor.execute("UPDATE Game SET favorite=1 WHERE id=?", (game_id,))
        conn.commit()
 
    def showFavorites(e=None):
        output.controls.clear()
        output.controls.append(ft.Text("⭐ Favorites", size=25))
 
        games = cursor.execute("SELECT * FROM Game WHERE favorite=1").fetchall()
 
        if not games:
            output.controls.append(ft.Text("No favorite games yet"))
        else:
            for g in games:
                output.controls.append(gameCard(g))
 
        page.update()
 
    def goBack(e=None):
        page.controls.clear()
        page.add(mainLayout)
        page.update()
 
    def openGameUrl(e):
        page.launch_url(e.control.data)
 
    def showGameDetails(e):
        g = e.control.data
        page.controls.clear()
 
        page.add(
            ft.Column(
                [
                    ft.Image(src=g[4], width=400, height=200),
                    ft.Text(g[1], size=25, weight="bold"),
                    ft.Text(f"Genre: {g[2]}"),
                    ft.Text(f"Platform: {g[3]}"),
                    ft.Text(g[5]),
                    ft.Text(f"Worth: {g[7]}"),
                    ft.Text(f"Users: {g[8]}"),
                    ft.Text(f"Status: {g[9]}"),
                    ft.Text(f"Published Date: {g[10]}"),
                    ft.Text("Instructions:", weight="bold"),
                    ft.Text(g[11]),
                    ft.ElevatedButton("⭐ Add to Favorites", data=g[0], on_click=addToFavorites),
                    ft.ElevatedButton("Play Game", data=g[6], on_click=openGameUrl),
                    ft.ElevatedButton("Back", on_click=goBack),
                ],
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            )
        )
 
        page.update()
 
    def gameCard(g):
        return ft.Container(
            content=ft.Column(
                [
                    ft.GestureDetector(
                        data=g,
                        on_tap=showGameDetails,
                        content=ft.Image(src=g[4], width=200, height=120),
                    ),
                    ft.Text(g[1], weight="bold"),
                    ft.Text(g[2]),
                    ft.Text(g[3]),
                ]
            ),
            padding=10,
        )
 
    def showGames(e=None):
        output.controls.clear()
        output.controls.append(ft.Text("Games Store", size=25))
 
        games = cursor.execute("SELECT * FROM Game").fetchall()
 
        if not games:
            output.controls.append(ft.Text("No games loaded"))
        else:
            output.controls.append(ft.Text("Random Picks", size=20))
 
            for g in random.sample(games, min(6, len(games))):
                output.controls.append(gameCard(g))
 
        page.update()
 
    def showFilterTab(e=None):
        output.controls.clear()
 
        output.controls.append(ft.Text("Filter Games", size=25))
 
        output.controls.append(ft.Text("Platform"))
        output.controls.append(ft.ElevatedButton("PC", on_click=filterPlatformPC))
 
        output.controls.append(ft.Text("Genre"))
        output.controls.append(ft.ElevatedButton("DLC", on_click=filterGenreDLC))
 
        output.controls.append(ft.Text("Worth"))
        output.controls.append(
            ft.Row(
                [
                    ft.ElevatedButton("Free", on_click=filterWorthFree),
                    ft.ElevatedButton("Paid", on_click=filterWorthPaid),
                ]
            )
        )
 
        page.update()
 
    def searchForGames(e):
        query = e.control.value.lower()
        output.controls.clear()
 
        games = cursor.execute("SELECT * FROM Game").fetchall()
 
        for g in games:
            if query in g[1].lower():
                output.controls.append(gameCard(g))
 
        page.update()
 
    searchField = ft.TextField(label="Search for games", on_change=searchForGames)
 
    def load(e):
        games = requests.get("https://www.gamerpower.com/api/giveaways").json()
 
        cursor.execute("DELETE FROM Game")
 
        for g in games:
            cursor.execute(
                """INSERT INTO Game
                (id, title, genre, platform, image, description, url, worth, users, status, published_date, instructions)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    g["id"],
                    g["title"],
                    g["type"],
                    g["platforms"],
                    g["thumbnail"],
                    g["description"],
                    g["open_giveaway_url"],
                    g["worth"],
                    g.get("users", "N/A"),
                    g.get("status", "N/A"),
                    g.get("published_date", "N/A"),
                    g.get("instructions", "No instructions available"),
                ),
            )
 
        conn.commit()
        showGames()
 
    mainLayout = ft.Column(
        [
            ft.Text("Games Store", size=30, weight="bold"),
            ft.Row(
                [
                    ft.ElevatedButton("Home", on_click=showGames),
                    ft.ElevatedButton("Favorites", on_click=showFavorites),
                    ft.ElevatedButton("Filter", on_click=showFilterTab),
                ]
            ),
            searchField,
            ft.ElevatedButton("Load/refresh Games", on_click=load),
            output,
        ],
        expand=True,
    )
 
    page.add(mainLayout)
 
 
ft.app(target=main)