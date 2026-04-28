import flet as ft
import sqlite3
import requests
import random
import webbrowser
import pygame
 
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
    worth TEXT,
    users TEXT,
    status TEXT,
    published_date TEXT,
    instructions TEXT,
    rating REAL,
    rating_top INTEGER,
    owners INTEGER,
    beaten INTEGER,
    favorite INTEGER DEFAULT 0
)
""")
conn.commit()
 
 
def main(page: ft.Page):
    page.title = "Games Store"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0f0a1f"
    page.scroll = ft.ScrollMode.AUTO
 
    PURPLE = "#7c3aed"
    LIGHT_PURPLE = "#a78bfa"
 
    output = ft.Column(spacing=15, expand=True)
 
    pygame.mixer.init()
    pygame.mixer.music.load("/Users/salvadormateo/Music/Music/Media.localized/Music/Unknown Artist/Unknown Album/Choose Your Seeds - Neon Mixtape Tour - Plants vs. Zombies 2.mp3")
 
    def styled_button(text, on_click, data=None):
        return ft.ElevatedButton(
            text,
            data=data,
            on_click=on_click,
            style=ft.ButtonStyle(
                bgcolor=PURPLE,
                color="white",
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
        )
 
    def gameCard(g):
        return ft.Container(
            content=ft.Column(
                [
                    ft.GestureDetector(
                        data=g,
                        on_tap=showGameDetails,
                        content=ft.Image(src=g[4], width=350, height=180, border_radius=10),
                    ),
                    ft.Text(g[1], weight="bold", size=16),
                    ft.Text(f"{g[2]} | {g[3]}", size=12, color="gray"),
                ],
                spacing=5,
            ),
            padding=10,
            bgcolor="#1a1333",
            border_radius=15,
        )
 
    def toggleMusic(e):
        if e.control.playing:
            pygame.mixer.music.stop()
            e.control.text = "Music Off/On"
            e.control.playing = False
        else:
            pygame.mixer.music.play(-1)
            e.control.text = "Music On"
            e.control.playing = True
        page.update()
 
    def addToFavorites(e):
        cursor.execute("UPDATE Game SET favorite=1 WHERE id=?", (e.control.data,))
        conn.commit()
 
    def showFavorites(e=None):
        output.controls.clear()
        output.controls.append(ft.Text("Favorites", size=24, weight="bold"))
        games = cursor.execute("SELECT * FROM Game WHERE favorite=1").fetchall()
        for g in games:
            output.controls.append(gameCard(g))
        page.update()
 
    def goBack(e=None):
        page.controls.clear()
        page.add(mainLayout)
        page.update()
 
    def openGameUrl(e):
        webbrowser.open(e.control.data)
 
    def showGameDetails(e):
        g = e.control.data
        page.controls.clear()
        page.add(
            ft.Column(
                [
                    ft.Image(src=g[4], width=400, height=220),
                    ft.Text(g[1], size=26, weight="bold"),
                    ft.Text(f"⭐ {g[12]} / {g[13]}"),
                    ft.Text(f"Owners: {g[14]}"),
                    ft.Text(f"Beaten: {g[15]}"),
                    ft.Text(f"{g[2]} | {g[3]}"),
                    ft.Text(f"Release: {g[10]}"),
                    styled_button("Add to Favorites", addToFavorites, g[0]),
                    styled_button("Open Game Page", openGameUrl, g[6]),
                    styled_button("Back", goBack),
                ],
                spacing=10,
                scroll=ft.ScrollMode.AUTO,
            )
        )
        page.update()
 
    def showGames(e=None):
        output.controls.clear()
        output.controls.append(ft.Text("Games", size=24, weight="bold"))
        games = cursor.execute("SELECT * FROM Game").fetchall()
        for g in random.sample(games, min(8, len(games))):
            output.controls.append(gameCard(g))
        page.update()
 
    def showFilterTab(e=None):
        output.controls.clear()
        output.controls.append(ft.Text("Filter", size=24, weight="bold"))
 
        games = cursor.execute("SELECT * FROM Game").fetchall()
 
        platforms = sorted({p.strip() for g in games for p in g[3].split(",")})
        genres = sorted({x.strip() for g in games for x in g[2].split(",")})
 
        for p in platforms:
            if p:
                output.controls.append(styled_button(p, filterPlatform, p))
 
        for g in genres:
            if g:
                output.controls.append(styled_button(g, filterGenre, g))
 
        page.update()
 
    def filterPlatform(e):
        output.controls.clear()
        games = cursor.execute("SELECT * FROM Game").fetchall()
        for g in games:
            if e.control.data in g[3]:
                output.controls.append(gameCard(g))
        page.update()
 
    def filterGenre(e):
        output.controls.clear()
        games = cursor.execute("SELECT * FROM Game").fetchall()
        for g in games:
            if e.control.data in g[2]:
                output.controls.append(gameCard(g))
        page.update()
 
    def searchForGames(e):
        query = e.control.value.lower()
        output.controls.clear()
        games = cursor.execute("SELECT * FROM Game").fetchall()
        for g in games:
            if query in g[1].lower():
                output.controls.append(gameCard(g))
        page.update()
 
    def showTrending(e=None):
        output.controls.clear()
        output.controls.append(ft.Text("Trending", size=24, weight="bold"))
 
        games = cursor.execute("SELECT * FROM Game").fetchall()
 
        worst = sorted(games, key=lambda g: g[12] or 0)[:5]
        most_pop = sorted(games, key=lambda g: g[14] or 0, reverse=True)[:5]
        least_pop = sorted(games, key=lambda g: g[14] or 0)[:5]
        most_beaten = sorted(games, key=lambda g: g[15] or 0, reverse=True)[:5]
        least_beaten = sorted(games, key=lambda g: g[15] or 0)[:5]
 
        sections = [
            ("Worst Rated", worst),
            ("Most Popular", most_pop),
            ("Least Popular", least_pop),
            ("Most Beaten", most_beaten),
            ("Least Beaten", least_beaten),
        ]
 
        for title, group in sections:
            output.controls.append(ft.Text(title, size=20))
            for g in group:
                output.controls.append(gameCard(g))
 
        page.update()
 
    def load(e):
        data = requests.get("https://api.rawg.io/api/games?key=c99edda7d3484b318c2cb842550bc8b7&page_size=40").json()
 
        cursor.execute("DELETE FROM Game")
 
        for g in data["results"]:
            cursor.execute(
                "INSERT INTO Game VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)",
                (
                    g["id"],
                    g["name"],
                    ", ".join([x["name"] for x in g.get("genres", [])]),
                    ", ".join([p["platform"]["name"] for p in g.get("platforms", [])]),
                    g.get("background_image", ""),
                    "",
                    f"https://rawg.io/games/{g.get('slug','')}",
                    "",
                    "",
                    "",
                    g.get("released", ""),
                    "",
                    g.get("rating", 0),
                    g.get("rating_top", 0),
                    g.get("added_by_status", {}).get("owned", 0),
                    g.get("added_by_status", {}).get("beaten", 0),
                ),
            )
 
        conn.commit()
        showGames()
 
    searchField = ft.TextField(label="Search", on_change=searchForGames)
 
    music_button = styled_button("Music Off", toggleMusic)
    music_button.playing = False
 
    navbar = ft.Row(
        [
            styled_button("Home", showGames),
            styled_button("Favorites", showFavorites),
            styled_button("Filter", showFilterTab),
            styled_button("Trending", showTrending),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )
 
    mainLayout = ft.Column(
        [
            ft.Text("Games Store", size=32, weight="bold", color=LIGHT_PURPLE),
            navbar,
            searchField,
            ft.Row(
                [styled_button("Load Games", load), music_button],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            output,
        ],
        spacing=20,
        expand=True,
    )
 
    page.add(mainLayout)
 
 
ft.app(target=main)
 