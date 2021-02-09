from quart import Quart, Response, render_template
import sqlite3
import random
import time
from threading import Thread

from globalConfig import config

db = None

async def redirect(shortenUrl: str):
    if db:
        result = db.cursor().execute("SELECT content FROM redirect WHERE shortenUrl = ?;", (shortenUrl,)).fetchone()
        if result:
            return Response(result[0], status=200)
        else:
            imgList = config["webRoute"]["404img"]
            img = imgList[int(random.random() * len(imgList))] if imgList else None
            return Response(await render_template("404.html", reason="该页面已失效", img = img), status=404)


def dbCleanTask():
    dbInThread = sqlite3.connect("redirect.db")
    dbInThread.cursor().execute("DELETE FROM redirect WHERE strftime('%s','now') - createTime >= ttl")
    dbInThread.commit()


def getShortenUrl(length):
    baseStr = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    url = ""
    for i in range(length):
        url += baseStr[random.randint(0, len(baseStr) - 1)]
    return url


async def get404Content(reason:str):
    return await render_template("404.html", reason=reason)


async def getPicSearchByIdContent(title, author, tagList, pid, imgList):
    return await render_template("picSearchById.html", title=title, author=author, tagList=tagList, pid=pid, imgList=imgList, pixivUrl="https://www.pixiv.net/artworks/"+str(pid))


async def getSetuContent(imgUrl):
    return await render_template("setu.html", imgUrl=imgUrl)


async def getRankingContent(imgList, queryType):
    return await render_template("pixivRanking.html", queryType=queryType, imgList=imgList)


async def shortenUrl(content: str):
    if db:
        ttl = config["webRoute"]["ttl"]
        length = config["webRoute"]["urlLength"]
        shortenUrl = getShortenUrl(length)
        db.cursor().execute("INSERT INTO redirect VALUES(NULL, ?, ?, ?, ?);", (shortenUrl, content, ttl, time.time()))
        db.commit()
        return "http://{0}:{1}/{2}".format(config["webRoute"]["apiAddress"], config["cq-reservsews"]["port"], shortenUrl)


def webRouteStart(app, scheduler):
    global db
    app.template_folder = "./template/"
    app.route("/<shortenUrl>")(redirect)
    scheduler.add_job(dbCleanTask, "interval", minutes=1, max_instances=10)
    db = sqlite3.connect("redirect.db")
    db.cursor().execute("""
        CREATE TABLE IF NOT EXISTS redirect (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        shortenUrl STRING  UNIQUE
                           NOT NULL,
        content    TEXT  NOT NULL,
        ttl        INTEGER NOT NULL,
        createTime INTEGER NOT NULL
    );
    """)
