from globalConfig import config

import re
import json
import aiohttp
from aiocqhttp import Message, MessageSegment


def unescape(text:str):
    return text.replace("&#44;", ",").replace("&#91;", "[").replace("&#93;", "]").replace("&amp;", "&")


def humanNum(num):
    return str(num) if num < 10000 else str(round(num / 10000, 2)) + "万"


def getAvBvFromNormalLink(text:str):
    search = re.findall("bilibili\.com\/video\/(?:[Aa][Vv]([0-9]+)|([Bb][Vv][0-9a-zA-Z]+))", text)
    if search:
        return {
            "aid": search[0][0],
            "bvid": search[0][1]
        }
    else:
        return None


async def getAvBvFromShortLink(shortlink:str):
    async with aiohttp.request("GET", shortlink, max_redirects=0) as res:
        return getAvBvFromNormalLink(str(res.real_url))


async def getAvBvFromMsg(msg):
    search = getAvBvFromNormalLink(msg)
    if search:
        return search
    search = re.search(r"(?P<url>(b23|acg)\.tv\/[0-9a-zA-Z]+)", msg)
    if search:
        return await getAvBvFromShortLink("http://" + search.group("url"))
    return None


def getResultMsg(thumbnail, av, title, up, viewNum, danmakuNum, bv):
    message = Message()
    if thumbnail:
        message.append(MessageSegment.image(thumbnail))
    if av:
        message.append(MessageSegment.text("\n"))
        message.append(MessageSegment.text("av" + str(av)))
    if title:
        message.append(MessageSegment.text("\n"))
        message.append(MessageSegment.text(title))
    if up:
        message.append(MessageSegment.text("\n"))
        message.append(MessageSegment.text("UP:" + up))
    if viewNum and danmakuNum:
        message.append(MessageSegment.text("\n"))
        message.append(MessageSegment.text(str(viewNum) + "播放" + " " + str(danmakuNum) + "弹幕"))
    if bv:
        message.append(MessageSegment.text("\n"))
        message.append(MessageSegment.text("https://www.bilibili.com/video/" + bv))
    return message


async def getVideoInfo(param):
    response = {
        "status": -1,
        "data": None
    }
    async with aiohttp.request("GET", "https://api.bilibili.com/x/web-interface/view", params=param) as res:
        response["status"] = res.status
        response["data"] = await res.text()
    if response["status"] == 200:
        result = json.loads(response["data"])
        thumbnail = result["data"]["pic"]
        av = result["data"]["aid"]
        title = result["data"]["title"]
        up = result["data"]["owner"]["name"]
        viewNum = result["data"]["stat"]["view"]
        danmakuNum = result["data"]["stat"]["danmaku"]
        bv = result["data"]["bvid"]
        return getResultMsg(thumbnail, av, title, up, viewNum, danmakuNum, bv)
    else:
        return None


def parseMsg(text:str):
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        return None
    jsonStr = unescape(text[start: end + 1])
    return json.loads(jsonStr)


async def antiBiliMiniApp(context, replyFunc, bot):
    setting = config["antiBiliMiniApp"]
    setting = {
        "enable": True,
        "getVideoInfo": True
    }
    data = None
    abv = await getAvBvFromMsg(context.message)
    if context.message.find("com.tencent.miniapp_01") != -1 and context.message.find("哔哩哔哩") != -1:
        data = parseMsg(context.message)
        qqdocurl = data["meta"]["detail_1"]["qqdocurl"]
        title = data["meta"]["detail_1"]["desc"]
        if setting["getVideoInfo"]:
            param = await getAvBvFromMsg(qqdocurl)
            reply = await getVideoInfo(param)
            if reply:
                await replyFunc(bot, context, reply)
                return True
    elif abv:
        reply = await getVideoInfo(abv)
        if reply:
            await replyFunc(bot, context, reply)
            return True
    return False

