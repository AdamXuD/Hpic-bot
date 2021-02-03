from src.setu import sendSetu
from src.utils import replyMsg ,isAtMe
from src.logger import Logger
from globalConfig import config
from src.webRoute import webRouteStart
from src.antiBiliMiniApp import antiBiliMiniApp
from src.picSearch import picSearch, openPicSearcherMode, closePicSearcherMode, hasImage
from src.pixiv import searchPicById, getPixivRanking

import uvicorn
import time
from aiocqhttp import CQHttp, Event

bot = CQHttp()
logger = Logger()
startTime = time.time()

if config["webRoute"]["enable"]:
    webRouteStart(bot.server_app, logger.scheduler)

async def commonHandle(context):
    if config["setu"]["enable"] == True:
        if await sendSetu(context, replyMsg, logger, bot) == True:
            return True
    if config["picSearch"]["enable"] == True:
        if await openPicSearcherMode(context, replyMsg, logger, bot) or await closePicSearcherMode(context, replyMsg, logger, bot):
            return True
        if await picSearch(context, replyMsg, logger, bot):
            return True
    if config["antiBiliMiniApp"]["enable"] == True:
        if await antiBiliMiniApp(context, replyMsg, bot):
            return True
    if config["pixiv"]["enable"] == True:
        if await searchPicById(context, replyMsg, logger, bot):
            return True
        if await getPixivRanking(context, replyMsg, logger, bot):
            return True
    return False


@bot.on_message("private")
async def onPrivate(event: Event):
    if event.time < startTime:
        return
    if await commonHandle(event):
        return True
    else:
        await replyMsg(bot, event, config["replys"]["default"], True, True)


@bot.on_message("group")
async def onGroup(event: Event):
    if event.time < startTime:
        return
    if isAtMe(event):
        if hasImage(event.message):
            if config["picSearch"]["enable"] == True:
                if await picSearch(event, replyMsg, logger, bot):
                    return True
        else:
            await replyMsg(bot, event, config["replys"]["default"], True, True)
            return True
    if await commonHandle(event):
        return True


# TODO 管理员可直接修改配置


if __name__ == '__main__':
    uvicorn.run(app='main:bot.asgi', host=config["cq-reservsews"]["host"], port=config["cq-reservsews"]["port"], reload=True, debug=True)

