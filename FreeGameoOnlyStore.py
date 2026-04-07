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
    url TEXT
)
""")
conn.commit()


def ensureColumns():
    columns = [
        ("description", "TEXT"),
        ("url", "TEXT")
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

    # 🔒 anti-spam lock
    is_loading = {"value": False}

    def goBack(e=None):
        page.controls.clear()
        page.add(mainLayout)
        page.update()

    def openGameUrl(e: ft.ControlEvent):
        page.launch_url(e.control.data)

    def showGameDetails(e: ft.ControlEvent):
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
                    ft.ElevatedButton(
                        "Play Game",
                        data=g[6],
                        on_click=openGameUrl
                    ),
                    ft.ElevatedButton(
                        "Back",
                        on_click=goBack
                    ),
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

    # 🔍 FIXED SEARCH
    def searchForGames(e: ft.ControlEvent):
        query = e.control.value.lower()

        output.controls.clear()
        output.controls.append(ft.Text("Search Results", size=25))

        if query == "":
            showGames()
            return

        games = cursor.execute(
            """
            SELECT * FROM Game 
            WHERE LOWER(title) LIKE ? 
            OR LOWER(genre) LIKE ? 
            OR LOWER(platform) LIKE ?
            """,
            (f"%{query}%", f"%{query}%", f"%{query}%")
        ).fetchall()

        if not games:
            output.controls.append(ft.Text("No matching games found"))
        else:
            for g in games:
                output.controls.append(gameCard(g))

        page.update()

    searchField = ft.TextField(
        label="Search for games",
        on_change=searchForGames,
    )

    # 🚀 OPTIMIZED LOAD FUNCTION
    def load(e):
        if is_loading["value"]:
            return  # ignore spam clicks

        is_loading["value"] = True

        btn = e.control
        btn.text = "Loading..."
        btn.disabled = True
        page.update()

        try:
            response = requests.get("https://www.gamerpower.com/api/giveaways", timeout=10)
            games = response.json()

            for g in games:
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO Game 
                    (id, title, genre, platform, image, description, url) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        g["id"],
                        g["title"],
                        g["type"],
                        g["platforms"],
                        g["thumbnail"],
                        g["description"],
                        g["open_giveaway_url"],
                    ),
                )

            conn.commit()

            showGames()

        except Exception as err:
            output.controls.clear()
            output.controls.append(ft.Text(f"Error loading games: {err}"))

        finally:
            btn.text = "Refresh Games"
            btn.disabled = False
            is_loading["value"] = False
            page.update()

    mainLayout = ft.Column(
        [
            ft.Text("Games Store", size=30, weight="bold"),
            searchField,
            ft.ElevatedButton("Refresh Games", on_click=load),
            output,
        ],
        expand=True,
    )

    page.add(mainLayout)


ft.app(target=main)