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
    image TEXT
)
""")
conn.commit()

def main(page: ft.Page):
    page.title = "Free Games"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    def SearchForGames(e: [ft.TextField]):
        message.value = e.control.value
        page.update()

    page.add(
        ft.TextField(
            label="Search for games",
            on_change=SearchForGames,
        ),
        message := ft.Text(),
    )

    output = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

    def gameCard(g):
        return ft.Container(
            content=ft.Column([
                ft.Image(src=g[4], width=200, height=120),
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
            output.controls.append(ft.Text("Recommended", size=20))
            genres = {}

        output.controls.append(ft.Text("Random Picks", size=20))

        for g in random.sample(games, min(6, len(games))):
            output.controls.append(gameCard(g))

        page.update()

    def load(e):
        games = requests.get("https://www.freetogame.com/api/games").json()

        cursor.execute("DELETE FROM Game")

        for g in games:
            cursor.execute(
                "INSERT INTO Game (id, title, genre, platform, image) VALUES (?, ?, ?, ?, ?)",
                (g["id"], g["title"], g["genre"], g["platform"], g["thumbnail"])
            )

        conn.commit()
        showGames(e)

    page.add(
        ft.Column(
            [
                ft.Text("Only Free Games Store", size=30, weight="bold"),
                ft.ElevatedButton("Load/refresh Games", on_click=load),
                output
            ],
            expand=True
        )
    )

ft.app(target=main)