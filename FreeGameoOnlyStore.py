import flet as ft
import sqlite3
import requests
import random
import webbrowser
import pygame
from constVariables import API_KEY
import asyncio
 
conn=sqlite3.connect("games.db",check_same_thread=False)
cursor=conn.cursor()
 
cursor.execute("""
CREATE TABLE IF NOT EXISTS Games(
    id INTEGER PRIMARY KEY,
    title TEXT,
    image TEXT,
    description TEXT,
    url TEXT,
    published_date TEXT,
    favorite INTEGER DEFAULT 0
)
""")
 
cursor.execute("""
CREATE TABLE IF NOT EXISTS Genres(
    genre_id INTEGER PRIMARY KEY AUTOINCREMENT,
    genre_name TEXT
)
""")
 
cursor.execute("""
CREATE TABLE IF NOT EXISTS Platforms(
    platform_id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform_name TEXT
)
""")
 
cursor.execute("""
CREATE TABLE IF NOT EXISTS GameGenres(
    game_id INTEGER,
    genre_id INTEGER
)
""")
 
cursor.execute("""
CREATE TABLE IF NOT EXISTS GamePlatforms(
    game_id INTEGER,
    platform_id INTEGER
)
""")
 
cursor.execute("""
CREATE TABLE IF NOT EXISTS Ratings(
    game_id INTEGER PRIMARY KEY,
    rating REAL,
    rating_top INTEGER
)
""")
 
cursor.execute("""
CREATE TABLE IF NOT EXISTS Owners(
    game_id INTEGER PRIMARY KEY,
    owners INTEGER,
    sales INTEGER,
    beaten INTEGER
)
""")
 
conn.commit()
 
async def main(page:ft.Page):
    page.title="Games Store"
    page.theme_mode=ft.ThemeMode.DARK
    page.bgcolor="#0f0a1f"
    page.scroll=ft.ScrollMode.AUTO
 
    purple="#7c3aed"
    lighterPurple="#a78bfa"
 
    output=ft.Column(spacing=15,expand=True)
 
    pygame.mixer.init()
    pygame.mixer.music.load("assets/audio/song1.mp3")
 
    logo=ft.Image(src="logo.png",width=400,height=400)
 
    warningText=ft.Text(
        "Be careful when you see suspicious links like this. It can harm your computer!",
        color="red",
        visible=False,
    )
 
    prankActive={"value":False}
 
    def styledButton(text,onClick,data=None):
        return ft.ElevatedButton(
            text,
            data=data,
            on_click=onClick,
            style=ft.ButtonStyle(
                bgcolor=purple,
                color="white",
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
        )
 
    def getGenres(gameId):
        rows=cursor.execute("""
        SELECT Genres.genre_name
        FROM Genres
        JOIN GameGenres
        ON Genres.genre_id=GameGenres.genre_id
        WHERE GameGenres.game_id=?
        """,(gameId,)).fetchall()
 
        return ", ".join([r[0] for r in rows])
 
    def getPlatforms(gameId):
        rows=cursor.execute("""
        SELECT Platforms.platform_name
        FROM Platforms
        JOIN GamePlatforms
        ON Platforms.platform_id=GamePlatforms.platform_id
        WHERE GamePlatforms.game_id=?
        """,(gameId,)).fetchall()
 
        return ", ".join([r[0] for r in rows])
 
    def getRating(gameId):
        return cursor.execute("""
        SELECT rating,rating_top
        FROM Ratings
        WHERE game_id=?
        """,(gameId,)).fetchone()
 
    def getOwners(gameId):
        return cursor.execute("""
        SELECT owners,sales,beaten
        FROM Owners
        WHERE game_id=?
        """,(gameId,)).fetchone()
 
    def getAllGames():
        return cursor.execute("""
        SELECT *
        FROM Games
        """).fetchall()
 
    def openArcade(e):
        webbrowser.open("https://www.friv.com/old/")
 
    def playPrank(e):
        pygame.mixer.music.load("assets/audio/song2.mp3")
        pygame.mixer.music.play()
        logo.src="Narwhals.png"
        logo.update()
        warningText.visible=True
        warningText.update()
        prankActive["value"]=True
        page.update()
 
    prankButton=ft.ElevatedButton(
        "Click this button for a free 100% discount",
        on_click=playPrank,
        style=ft.ButtonStyle(
            bgcolor="red",
            color="white",
        ),
    )
 
    rightAlignedRow=ft.Column([
        ft.Row([prankButton],alignment=ft.MainAxisAlignment.END),
        ft.Row([warningText],alignment=ft.MainAxisAlignment.END),
    ])
 
    def gameCard(g):
        rating=getRating(g[0])
 
        imgSrc="Narwhals.png" if prankActive["value"] else g[2]
 
        imgContainer=ft.Container(
            content=ft.Image(
                src=imgSrc,
                width=250,
                height=140,
                border_radius=10,
            ),
            animate_scale=150,
            scale=1,
        )
 
        def onTapDown(e):
            imgContainer.scale=0.95
            imgContainer.update()
 
        def onTapUp(e):
            imgContainer.scale=1
            imgContainer.update()
            showGameDetails(e)
 
        return ft.Container(
            content=ft.Column([
                ft.GestureDetector(
                    data=g,
                    on_tap_down=onTapDown,
                    on_tap_up=onTapUp,
                    content=imgContainer,
                ),
                ft.Text(g[1],weight="bold",size=14),
                ft.Text(f"{getGenres(g[0])} | {getPlatforms(g[0])}",size=11,color="gray"),
                ft.Text(f"⭐ {rating[0]}"),
            ],spacing=5),
            padding=10,
            bgcolor="#1a1333",
            border_radius=15,
            width=260,
        )
 
    def gridList(games):
        rows=[]
 
        for i in range(0,len(games),2):
            rows.append(
                ft.Row(
                    [gameCard(g) for g in games[i:i+2]],
                    spacing=10
                )
            )
 
        return ft.Column(rows,spacing=10)
 
    def toggleMusic(e):
        if e.control.playing:
            pygame.mixer.music.stop()
            e.control.playing=False
        else:
            pygame.mixer.music.load("assets/audio/song1.mp3")
            pygame.mixer.music.play(-1)
            e.control.playing=True
 
        page.update()
 
    def toggleFavorite(e):
        gameId=e.control.data
 
        current=cursor.execute("""
        SELECT favorite
        FROM Games
        WHERE id=?
        """,(gameId,)).fetchone()[0]
 
        newValue=0 if current==1 else 1
 
        cursor.execute("""
        UPDATE Games
        SET favorite=?
        WHERE id=?
        """,(newValue,gameId))
 
        conn.commit()
 
        e.control.text="Remove from Favorites" if newValue else "Add to Favorites"
 
        page.update()
 
    def showFavorites(e=None):
        output.controls.clear()
 
        output.controls.append(ft.Text("Favorites",size=24,weight="bold"))
 
        games=cursor.execute("""
        SELECT *
        FROM Games
        WHERE favorite=1
        """).fetchall()
 
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
        g=e.control.data
 
        rating=getRating(g[0])
        ownerData=getOwners(g[0])
 
        page.controls.clear()
 
        imgSrc="Narwhals.png" if prankActive["value"] else g[2]
 
        favText="Remove from Favorites" if g[6] else "Add to Favorites"
 
        page.add(
            ft.Column([
                ft.Image(src=imgSrc,width=400,height=220),
                ft.Text(g[1],size=26,weight="bold"),
                ft.Text(f"⭐ {rating[0]} / {rating[1]}"),
                ft.Text(f"Owners: {ownerData[0]}"),
                ft.Text(f"Sales: {ownerData[1]}"),
                ft.Text(f"Beaten: {ownerData[2]}"),
                ft.Text(f"{getGenres(g[0])} | {getPlatforms(g[0])}"),
                ft.Text(f"Release: {g[5]}"),
                styledButton(favText,toggleFavorite,g[0]),
                styledButton("Open Game Page",openGameUrl,g[4]),
                styledButton("Back",goBack),
            ],
            spacing=10,
            scroll=ft.ScrollMode.AUTO)
        )
 
        page.update()
 
    def showGames(e=None):
        output.controls.clear()
 
        output.controls.append(ft.Text("Games",size=24,weight="bold"))
 
        games=getAllGames()
 
        if games:
            output.controls.append(gridList(random.sample(games,min(12,len(games)))))
 
        page.update()
 
    def showFilterTab(e=None):
        output.controls.clear()
 
        output.controls.append(ft.Text("Filter",size=24,weight="bold"))
 
        platforms=cursor.execute("""
        SELECT platform_name
        FROM Platforms
        """).fetchall()
 
        genres=cursor.execute("""
        SELECT genre_name
        FROM Genres
        """).fetchall()
 
        for p in platforms:
            output.controls.append(styledButton(p[0],filterPlatform,p[0]))
 
        for g in genres:
            output.controls.append(styledButton(g[0],filterGenre,g[0]))
 
        page.update()
 
    def filterPlatform(e):
        output.controls.clear()
 
        games=cursor.execute("""
        SELECT DISTINCT Games.*
        FROM Games
        JOIN GamePlatforms
        ON Games.id=GamePlatforms.game_id
        JOIN Platforms
        ON Platforms.platform_id=GamePlatforms.platform_id
        WHERE Platforms.platform_name=?
        """,(e.control.data,)).fetchall()
 
        if games:
            output.controls.append(gridList(games))
 
        page.update()
 
    def filterGenre(e):
        output.controls.clear()
 
        games=cursor.execute("""
        SELECT DISTINCT Games.*
        FROM Games
        JOIN GameGenres
        ON Games.id=GameGenres.game_id
        JOIN Genres
        ON Genres.genre_id=GameGenres.genre_id
        WHERE Genres.genre_name=?
        """,(e.control.data,)).fetchall()
 
        if games:
            output.controls.append(gridList(games))
 
        page.update()
 
    def searchForGames(e):
        query=e.control.value.lower()
 
        output.controls.clear()
 
        games=cursor.execute("""
        SELECT *
        FROM Games
        WHERE LOWER(title) LIKE ?
        """,(f"%{query}%",)).fetchall()
 
        if games:
            output.controls.append(gridList(games))
 
        page.update()
 
    def showTrending(e=None):
        output.controls.clear()
 
        output.controls.append(ft.Text("Trending",size=24,weight="bold"))
 
        games=cursor.execute("""
        SELECT DISTINCT Games.*,Ratings.rating,Owners.owners,Owners.beaten
        FROM Games
        JOIN Ratings
        ON Games.id=Ratings.game_id
        JOIN Owners
        ON Games.id=Owners.game_id
        """).fetchall()
 
        worst=sorted(games,key=lambda g:g[7])[:5]
        mostPop=sorted(games,key=lambda g:g[8],reverse=True)[:5]
        leastPop=sorted(games,key=lambda g:g[8])[:5]
        mostBeaten=sorted(games,key=lambda g:g[9],reverse=True)[:5]
        leastBeaten=sorted(games,key=lambda g:g[9])[:5]
 
        sections=[
            ("Worst Rated",worst),
            ("Most Popular",mostPop),
            ("Least Popular",leastPop),
            ("Most Beaten",mostBeaten),
            ("Least Beaten",leastBeaten),
        ]
 
        for title,group in sections:
            output.controls.append(ft.Text(title,size=20))
            output.controls.append(gridList(group))
 
        page.update()
 
    def showOwnersTab(e=None):
        output.controls.clear()
 
        output.controls.append(ft.Text("Top Owners",size=24,weight="bold"))
 
        games=cursor.execute("""
        SELECT DISTINCT Games.*,Owners.owners
        FROM Games
        JOIN Owners
        ON Games.id=Owners.game_id
        """).fetchall()
 
        topMostOwners=sorted(games,key=lambda g:g[7],reverse=True)[:5]
        topLeastOwners=sorted(games,key=lambda g:g[7])[:5]
 
        sections=[
            ("Top 5 Most Owners",topMostOwners),
            ("Top 5 Least Owners",topLeastOwners),
        ]
 
        for title,group in sections:
            output.controls.append(ft.Text(title,size=20,weight="bold"))
            output.controls.append(gridList(group))
 
        page.update()
 
    async def load(e):
        output.controls.clear()
 
        output.controls.append(ft.Text("Loading games... please wait"))
 
        page.update()
 
        url=f"https://api.rawg.io/api/games?key={API_KEY}&page_size=100"
 
        pageCount=0
 
        while url and pageCount<10:
            response=requests.get(url).json()
 
            for g in response["results"]:
                cursor.execute("""
                INSERT INTO Games(
                    id,
                    title,
                    image,
                    description,
                    url,
                    published_date,
                    favorite
                )
                VALUES(?,?,?,?,?,?,0)
                ON CONFLICT(id)
                DO UPDATE SET
                title=excluded.title,
                image=excluded.image,
                url=excluded.url,
                published_date=excluded.published_date
                """,(
                    g["id"],
                    g["name"],
                    g.get("background_image",""),
                    "",
                    f"https://rawg.io/games/{g.get('slug','')}",
                    g.get("released",""),
                ))
 
                cursor.execute("""
                INSERT OR REPLACE INTO Ratings(
                    game_id,
                    rating,
                    rating_top
                )
                VALUES(?,?,?)
                """,(
                    g["id"],
                    g.get("rating",0),
                    g.get("rating_top",0),
                ))
 
                owners=g.get("added_by_status",{}).get("owned",0)
                beaten=g.get("added_by_status",{}).get("beaten",0)
 
                cursor.execute("""
                INSERT OR REPLACE INTO Owners(
                    game_id,
                    owners,
                    sales,
                    beaten
                )
                VALUES(?,?,?,?)
                """,(
                    g["id"],
                    owners,
                    owners,
                    beaten,
                ))
 
                cursor.execute("DELETE FROM GameGenres WHERE game_id=?",(g["id"],))
                cursor.execute("DELETE FROM GamePlatforms WHERE game_id=?",(g["id"],))
 
                for genre in g.get("genres",[]):
                    existing=cursor.execute("""
                    SELECT genre_id
                    FROM Genres
                    WHERE genre_name=?
                    """,(genre["name"],)).fetchone()
 
                    if existing:
                        genreId=existing[0]
                    else:
                        cursor.execute("""
                        INSERT INTO Genres(genre_name)
                        VALUES(?)
                        """,(genre["name"],))
                        genreId=cursor.lastrowid
 
                    cursor.execute("""
                    INSERT INTO GameGenres(game_id,genre_id)
                    VALUES(?,?)
                    """,(g["id"],genreId))
 
                for platform in g.get("platforms",[]):
                    platformName=platform["platform"]["name"]
 
                    existing=cursor.execute("""
                    SELECT platform_id
                    FROM Platforms
                    WHERE platform_name=?
                    """,(platformName,)).fetchone()
 
                    if existing:
                        platformId=existing[0]
                    else:
                        cursor.execute("""
                        INSERT INTO Platforms(platform_name)
                        VALUES(?)
                        """,(platformName,))
                        platformId=cursor.lastrowid
 
                    cursor.execute("""
                    INSERT INTO GamePlatforms(game_id,platform_id)
                    VALUES(?,?)
                    """,(g["id"],platformId))
 
            conn.commit()
 
            url=response.get("next")
            pageCount+=1
 
            output.controls[0]=ft.Text(f"Loading... page {pageCount}/10")
 
            page.update()
 
            await asyncio.sleep(0)
 
        showGames()
 
    searchField=ft.TextField(
        label="Search",
        on_change=searchForGames,
    )
 
    musicButton=styledButton("Music On/Off",toggleMusic)
 
    musicButton.playing=False
 
    navbar=ft.Row([
        styledButton("Home",showGames),
        styledButton("Favorites",showFavorites),
        styledButton("Filter",showFilterTab),
        styledButton("Trending",showTrending),
        styledButton("Owners",showOwnersTab),
        styledButton("Arcade Mode",openArcade),
    ],alignment=ft.MainAxisAlignment.CENTER)
 
    mainLayout=ft.Column([
        ft.Row([logo],alignment=ft.MainAxisAlignment.CENTER),
        ft.Text("Games Store",size=32,weight="bold",color=lighterPurple),
        navbar,
        rightAlignedRow,
        searchField,
        ft.Row([
            styledButton("Load Games",load),
            musicButton,
        ],alignment=ft.MainAxisAlignment.CENTER),
        output,
    ],spacing=20,expand=True)
 
    page.add(mainLayout)
 
ft.app(target=main,assets_dir="assets")