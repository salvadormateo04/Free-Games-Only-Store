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


def main(page: ft.Page):
    page.title = "Free Games"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO

    output = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

    def SearchForGames(e: ft.ControlEvent):
        message.value = e.control.value
        page.update()

    search_field = ft.TextField(
        label="Search for games",
        on_change=SearchForGames,
    )

    message = ft.Text()

    # CLICK HANDLER (fixed)
    def handle_game_click(e):
        g = e.control.data
        showGameDetails(g)

    def showGameDetails(g):
        page.controls.clear()

        page.add(
            ft.Column([
                ft.Image(src=g[4], width=400, height=200),
                ft.Text(g[1], size=25, weight="bold"),
                ft.Text(f"Genre: {g[2]}"),
                ft.Text(f"Platform: {g[3]}"),
                ft.Text(g[5]),
                ft.ElevatedButton(
                    "Back",
                    on_click=goBack
                )
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True)
        )

        page.update()

    def goBack(e):
        page.controls.clear()
        page.add(main_layout)
        page.update()

    # GAME CARD (fixed)
    def gameCard(g):
        detector = ft.GestureDetector(
            content=ft.Image(src=g[4], width=200, height=120),
            on_tap=handle_game_click,
            data=g
        )

        return ft.Container(
            content=ft.Column([
                detector,
                ft.Text(g[1], weight="bold"),
                ft.Text(g[2]),
                ft.Text(g[3]),
            ]),
            padding=10
        )

    def showGames(e):
        output.controls.clear()
        output.controls.append(ft.Text("Free Games Store", size=25))

        games = cursor.execute("SELECT * FROM Game").fetchall()

        if not games:
            output.controls.append(ft.Text("No games loaded"))
        else:
            output.controls.append(ft.Text("Random Picks", size=20))

            for g in random.sample(games, min(6, len(games))):
                output.controls.append(gameCard(g))

        page.update()

    def load(e):
        games = requests.get("https://www.freetogame.com/api/games").json()

        cursor.execute("DELETE FROM Game")

        for g in games:
            cursor.execute(
                "INSERT INTO Game (id, title, genre, platform, image, description, url) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    g["id"],
                    g["title"],
                    g["genre"],
                    g["platform"],
                    g["thumbnail"],
                    g["short_description"],
                    g["game_url"]
                )
            )

        conn.commit()
        showGames(e)

    main_layout = ft.Column(
        [
            ft.Text("Only Free Games Store", size=30, weight="bold"),
            search_field,
            message,
            ft.ElevatedButton("Load/refresh Games", on_click=load),
            output
        ],
        expand=True
    )

    page.add(main_layout)


ft.app(target=main)