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
    message = ft.Text()

    genreFilter = ft.Dropdown(
        label="Filter by genre",
        options=[ft.dropdown.Option("All")],
        value="All"
    )

    def showGames(e=None):
        output.controls.clear()
        output.controls.append(ft.Text("Games Store", size=25))

        query = searchField.value.lower() if searchField.value else ""

        games = cursor.execute("SELECT * FROM Game").fetchall()

        filtered = [
            g for g in games
            if (query in g[1].lower())
            and (genreFilter.value == "All" or g[2] == genreFilter.value)
        ]

        if not filtered:
            output.controls.append(ft.Text("No games found"))
        else:
            for g in random.sample(filtered, min(6, len(filtered))):
                output.controls.append(gameCard(g))

        page.update()

    def searchForGames(e):
        showGames()

    searchField = ft.TextField(
        label="Search for games",
        on_change=searchForGames,
    )

    def clearSearch(e):
        searchField.value = ""
        output.controls.clear()
        page.update()

    clearBtn = ft.ElevatedButton("Clear", on_click=clearSearch)

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
                    ft.Text(f"worth: {g[7]}"),
                    ft.ElevatedButton(
                        "Visit Website",  # ← changed here
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

    def load(e):
        games = requests.get("https://www.gamerpower.com/api/giveaways").json()

        cursor.execute("DELETE FROM Game")

        genres = set()

        for g in games:
            cursor.execute(
                "INSERT INTO Game (id, title, genre, platform, image, description, url, worth) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    g["id"],
                    g["title"],
                    g["type"],
                    g["platforms"],
                    g["thumbnail"],
                    g["description"],
                    g["open_giveaway_url"],
                    g["worth"],
                ),
            )
            genres.add(g["type"])

        conn.commit()

        genreFilter.options = [ft.dropdown.Option("All")] + [
            ft.dropdown.Option(x) for x in sorted(genres)
        ]

        showGames()

    mainLayout = ft.Column(
        [
            ft.Text("Games Store", size=30, weight="bold"),
            searchField,
            clearBtn,
            genreFilter,
            message,
            ft.ElevatedButton("Load/refresh Games", on_click=load),
            output,
        ],
        expand=True,
    )

    page.add(mainLayout)

ft.app(target=main)