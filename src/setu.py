from .logger import Logger
from globalConfig import config
from .utils import startSchedule, base64Decode
from .webRoute import shortenUrl, getSetuContent

import re
import json
import random
import aiohttp
import asyncio
from aiocqhttp import MessageSegment


setuQueryUrl = base64Decode("aHR0cHM6Ly9hcGkubG9saWNvbi5hcHAvc2V0dS96aHV6aHUucGhw")

def getCustomSetting(uid, key:str):
    setting = config["setu"]
    if setting["groupCustom"].get(str(uid)) != None:
        if setting["groupCustom"][str(uid)].get(key) != None:
            return setting["groupCustom"][str(uid)][key]
    return setting[key]

async def sendSetu(context, replyFunc, logger, bot):
    setting = config["setu"]
    replys = config["replys"]
    proxy = setting["pximgProxy"]
    setuReg = re.compile(config["regs"]["setu"])

    setuSearch = setuReg.search(context.message)
    
    if setuSearch:
        apikey = setting["apikeys"][int(random.random() * len(setting["apikeys"]))] if setting["apikeys"] else ""

        setuGroupDict = setuSearch.groupdict()
        keyword = setuGroupDict["keyword"]

        delTime = None
        allLimit = None
        r18 = 0 if setuGroupDict["r18"] == None else 1

        if context.group_id: # 判断是否是群消息
            if getCustomSetting(context.group_id, "enable") == False:
                await replyFunc(bot, context, MessageSegment.text(replys["setuReject"]), True)
                return True
            if getCustomSetting(context.group_id, "r18") == False and r18 == int(True):
                await replyFunc(bot, context, MessageSegment.text(replys["setuR18NotAllow"]), True)
                return True
            delTime = getCustomSetting(context.group_id, "deleteTime")
            allLimit = {
                "cd": getCustomSetting(context.group_id, "cd"),
                "limit": getCustomSetting(context.group_id, "limit")
            }
        else:
            if setting["allowPM"] == False:
                await replyFunc(bot, context, MessageSegment.text(replys["setuReject"]), True)
                return True
            delTime = 0
            allLimit = {
                "cd" : 0,
                "limit": 2147483647
            }

        canSearch = logger.canSearch(context.user_id, context.group_id, allLimit, "setu")
        if canSearch != 0:
            if canSearch == Logger.setuCdLimit:
                await replyFunc(bot, context, MessageSegment.text(replys["setuCdLimit"]), True)
            if canSearch == Logger.setuCountLimit:
                await replyFunc(bot, context, MessageSegment.text(replys["setuCountLimit"]), True)
            return True

        async with aiohttp.request("GET", setuQueryUrl, params={ "apikey" : apikey, "r18" : r18, "keyword" : keyword, "size1200" : int(setting["size1200"]) }) as res:
            result = json.loads(await res.text())
        if result["code"] != 0:
            if result["code"] == 429: 
                await replyFunc(bot, context, MessageSegment.text(replys["setuQuotaExceeded"] if replys["setuQuotaExceeded"] else result["error"]), True);
            else:
                await replyFunc(bot, context, MessageSegment.text(result["error"]), True)
            return True
        await replyFunc(bot, context, MessageSegment.text("%(url)s (p%(p)s)" % {"url": result["url"], "p": result["p"]}), True)

        picUrl = re.sub("i.pximg.net", proxy, result["file"]) if proxy else result["file"]

        # base64

        if setting["safeMode"] and config["webRoute"]["enable"]:
            await replyFunc(bot, context, MessageSegment.text(await shortenUrl(await getSetuContent(picUrl))))
        else:
            ret = await replyFunc(bot, context, MessageSegment.image(picUrl))
            msgId = ret["message_id"] if ret and ret["message_id"] != None else 0
            if msgId and delTime > 0:
                startSchedule(delTime, lambda: asyncio.run(bot.call_action("delete_msg", message_id=msgId)))
        logger.doneSearch(context.user_id, context.group_id, "setu")
        return True
    else:
        return False
