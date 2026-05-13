import flet as ft
import sqlite3
import requests
import random
import webbrowser
import pygame
from constVariables import API_KEY
import asyncio
 
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
 
async def main(page: ft.Page):
    page.title = "Games Store"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0f0a1f"
    page.scroll = ft.ScrollMode.AUTO
 
    Purple = "#7c3aed"
    LighterPurple = "#a78bfa"
 
    output = ft.Column(spacing=15, expand=True)
 
    pygame.mixer.init()
    pygame.mixer.music.load("assets/audio/song1.mp3")
 
    logo = ft.Image(src="logo.png", width=400, height=400)
    warningText = ft.Text("Things like this can genuinely happen to your computer if you're not careful, watchout!", color="red", visible=False)
 
    prank_active = {"value": False}
 
    def styledButton(text, on_click, data=None):
        return ft.ElevatedButton(
            text,
            data=data,
            on_click=on_click,
            style=ft.ButtonStyle(
                bgcolor=Purple,
                color="white",
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
        )
 
    def openArcade(e):
        webbrowser.open("https://www.friv.com/old/")
    
    def playPrank(e):
        pygame.mixer.music.load("assets/audio/song2.mp3")
        pygame.mixer.music.play()
        logo.src = "Narwhals.png"
        logo.update()
        warningText.visible = True
        warningText.update()
        prank_active["value"] = True
        page.update()
 
    prankButton = ft.ElevatedButton(
        "Click this button for a free 100% discount",
        on_click=playPrank,
        style=ft.ButtonStyle(bgcolor="red", color="white"),
    )
 
 
    rightAlignedRow = ft.Column(
        [
            ft.Row([prankButton], alignment=ft.MainAxisAlignment.END),
            ft.Row([warningText], alignment=ft.MainAxisAlignment.END),
        ]
    )
 
    def gameCard(g):
        img_src = "Narwhals.png" if prank_active["value"] else g[4]
 
        img_container = ft.Container(
            content=ft.Image(src=img_src, width=250, height=140, border_radius=10),
            animate_scale=150,
            scale=1,
        )
 
        card_container = ft.Container(animate_scale=200, scale=1)
 
        def on_tap_down(e):
            img_container.scale = 0.95
            img_container.update()
 
        def on_tap_up(e):
            img_container.scale = 1
            img_container.update()
            showGameDetails(e)
 
        card_container.content = ft.Column(
            [
                ft.GestureDetector(
                    data=g,
                    on_tap_down=on_tap_down,
                    on_tap_up=on_tap_up,
                    content=img_container,
                ),
                ft.Text(g[1], weight="bold", size=14),
                ft.Text(f"{g[2]} | {g[3]}", size=11, color="gray"),
            ],
            spacing=5,
        )
 
        return ft.Container(
            content=card_container,
            padding=10,
            bgcolor="#1a1333",
            border_radius=15,
            width=260,
        )
 
    def gridList(games):
        rows = []
        for i in range(0, len(games), 2):
            pair = games[i:i + 2]
            rows.append(ft.Row([gameCard(g) for g in pair], spacing=10))
        return ft.Column(rows, spacing=10)
 
    def toggleMusic(e):
        if e.control.playing:
            pygame.mixer.music.stop()
            e.control.text = "Music"
            e.control.playing = False
        else:
            pygame.mixer.music.load("assets/audio/song1.mp3")
            pygame.mixer.music.play(-1)
            e.control.text = "Music On"
            e.control.playing = True
        page.update()
 
    def toggleFavorite(e):
        game_id = e.control.data
        current = cursor.execute(
            "SELECT favorite FROM Game WHERE id=?", (game_id,)
        ).fetchone()[0]
 
        new_value = 0 if current == 1 else 1
 
        cursor.execute(
            "UPDATE Game SET favorite=? WHERE id=?",
            (new_value, game_id),
        )
        conn.commit()
 
        e.control.text = "Remove from Favorites" if new_value == 1 else "Add to Favorites"
        page.update()
 
    def showFavorites(e=None):
        output.controls.clear()
        output.controls.append(ft.Text("Favorites", size=24, weight="bold"))
        games = cursor.execute("SELECT * FROM Game WHERE favorite=1").fetchall()
        if games:
            output.controls.append(gridList(games))
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
 
        img_src = "Narwhals.png" if prank_active["value"] else g[4]
 
        is_fav = g[16] == 1
        fav_text = "Remove from Favorites" if is_fav else "Add to Favorites"
 
        page.add(
            ft.Column(
                [
                    ft.Image(src=img_src, width=400, height=220),
                    ft.Text(g[1], size=26, weight="bold"),
                    ft.Text(f"⭐ {g[12]} / {g[13]}"),
                    ft.Text(f"Owners: {g[14]}"),
                    ft.Text(f"Beaten: {g[15]}"),
                    ft.Text(f"{g[2]} | {g[3]}"),
                    ft.Text(f"Release: {g[10]}"),
                    styledButton(fav_text, toggleFavorite, g[0]),
                    styledButton("Open Game Page", openGameUrl, g[6]),
                    styledButton("Back", goBack),
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
        if games:
            output.controls.append(gridList(random.sample(games, min(12, len(games)))))
        page.update()
 
    def showFilterTab(e=None):
        output.controls.clear()
        output.controls.append(ft.Text("Filter", size=24, weight="bold"))
 
        games = cursor.execute("SELECT * FROM Game").fetchall()
 
        platforms = sorted({p.strip() for g in games for p in g[3].split(",")})
        genres = sorted({x.strip() for g in games for x in g[2].split(",")})
 
        for p in platforms:
            if p:
                output.controls.append(styledButton(p, filterPlatform, p))
 
        for g in genres:
            if g:
                output.controls.append(styledButton(g, filterGenre, g))
 
        page.update()
 
    def filterPlatform(e):
        output.controls.clear()
        games = cursor.execute("SELECT * FROM Game").fetchall()
        filtered = [g for g in games if e.control.data in g[3]]
        if filtered:
            output.controls.append(gridList(filtered))
        page.update()
 
    def filterGenre(e):
        output.controls.clear()
        games = cursor.execute("SELECT * FROM Game").fetchall()
        filtered = [g for g in games if e.control.data in g[2]]
        if filtered:
            output.controls.append(gridList(filtered))
        page.update()
 
    def searchForGames(e):
        query = e.control.value.lower()
        output.controls.clear()
        games = cursor.execute("SELECT * FROM Game").fetchall()
        filtered = [g for g in games if query in g[1].lower()]
        if filtered:
            output.controls.append(gridList(filtered))
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
            if group:
                output.controls.append(gridList(group))
 
        page.update()
 
    async def load(e):
        output.controls.clear()
        output.controls.append(ft.Text("Loading games... please wait"))
        page.update()
 
        url = f"https://api.rawg.io/api/games?key={API_KEY}&page_size=100"
        page_count = 0
        MAX_PAGES = 10
 
        while url and page_count < MAX_PAGES:
            response = requests.get(url).json()
 
            for g in response["results"]:
                cursor.execute(
                    """
                    INSERT INTO Game (id, title, genre, platform, image, description, url, worth, users, status, published_date, instructions, rating, rating_top, owners, beaten, favorite)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                    ON CONFLICT(id) DO UPDATE SET
                    title=excluded.title,
                    genre=excluded.genre,
                    platform=excluded.platform,
                    image=excluded.image,
                    url=excluded.url,
                    published_date=excluded.published_date,
                    rating=excluded.rating,
                    rating_top=excluded.rating_top,
                    owners=excluded.owners,
                    beaten=excluded.beaten,
                    favorite=Game.favorite
                    """,
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
            url = response.get("next")
            page_count += 1
 
            output.controls[0] = ft.Text(f"Loading... page {page_count}/10")
            page.update()
 
            await asyncio.sleep(0)
 
        showGames()
 
    searchField = ft.TextField(label="Search", on_change=searchForGames)
 
    musicButton = styledButton("Music On/Off", toggleMusic)
    musicButton.playing = False
 
    navbar = ft.Row(
        [
            styledButton("Home", showGames),
            styledButton("Favorites", showFavorites),
            styledButton("Filter", showFilterTab),
            styledButton("Trending", showTrending),
            styledButton("Arcade Mode", openArcade),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )
 
    mainLayout = ft.Column(
        [
            ft.Row([logo], alignment=ft.MainAxisAlignment.CENTER),
            ft.Text("Games Store", size=32, weight="bold", color=LighterPurple),
            navbar,
            rightAlignedRow,
            searchField,
            ft.Row([styledButton("Load Games", load), musicButton],
                   alignment=ft.MainAxisAlignment.CENTER),
            output,
        ],
        spacing=20,
        expand=True,
    )
 
    page.add(mainLayout)
 
ft.app(target=main, assets_dir="assets")