# -*- coding: utf-8 -*-

from quart import Quart, render_template
import json
from pixivpy3 import *
import re
import time
import datetime
from globalConfig import config

from .webRoute import shortenUrl, getPicSearchByIdContent, getRankingContent

api = None
loginTime = None

def loginToPixiv():
    if config["pixiv"]["enable"]:
        global api, loginTime
        api = ByPassSniApi()
        api.require_appapi_hosts(hostname="public-api.secure.pixiv.net")
        api.login(config["pixiv"]["username"], config["pixiv"]["password"])
        loginTime = time.time()


async def searchPicById(context, replyFunc, logger, bot):
    setting = config["pixiv"]
    proxy = setting["pximgProxy"]
    pidReg = re.compile(config["regs"]["watchPixivIMG"])
    pidSearch = pidReg.search(context.message)

    if pidSearch:
        if api == None or time.time() - loginTime >= setting["loginttl"]:
            loginToPixiv()
        pidGroupDict = pidSearch.groupdict()
        pid = int(pidGroupDict["pid"])

        result = api.illust_detail(pid)
        url = None
        if result.get("illust"):
            needRes = result["illust"]
            title = needRes["title"]
            author = needRes["user"]["name"]
            pid = needRes["id"]
            tags = [tag["name"] for tag in needRes["tags"]]
            tagStr = " ".join(tags)
            imgList = []
            if needRes["meta_pages"]:
                for imgItem in needRes["meta_pages"]:
                    if proxy:
                        imgList.append(imgItem["image_urls"]["large"].replace("i.pximg.net", proxy))
                    else:
                        imgList.append(imgItem["image_urls"]["large"])
            else:
                if proxy:
                    imgList.append(needRes["meta_single_page"]["original_image_url"].replace("i.pximg.net", proxy))
                else:
                    imgList.append(needRes["meta_single_page"]["original_image_url"])
            url = await shortenUrl(await getPicSearchByIdContent(title, author, tagStr, pid, imgList))
            await replyFunc(bot, context, url, True, True)
            return True
        elif result.get("error"):
            errMsg = result["error"]["user_message"]
            await replyFunc(bot, context, errMsg, True, True)
            return True
        return False
    else:
        return False


async def getPixivRanking(context, replyFunc, logger, bot):
    setting = config["pixiv"]
    rankingReg = re.compile(config["regs"]["watchPixivRanking"])
    rankingSearch = rankingReg.search(context.message)
    proxy = setting["pximgProxy"]

    if rankingSearch:
        if api == None or time.time() - loginTime >= setting["loginttl"]:
            loginToPixiv()
        rankingGroupDict = rankingSearch.groupdict()
        r18 = rankingGroupDict["r18"]
        type = rankingGroupDict["type"]
        dateStr = rankingGroupDict["dateStr"]
        if dateStr:
            if re.search("^(((?:19|20)\d\d)-(0?[1-9]|1[0-2])-(0?[1-9]|[12][0-9]|3[01]))$", dateStr) == None:
                await replyFunc(bot, context, "日期输入不合法哦~", True, True)
                return True

        if r18 and setting["r18"] == False:
            await replyFunc(bot, context, config["replys"]["setuR18NotAllow"], True, True)
            return True
        mode = None
        if type == "日":
            mode = "day"
        elif type == "月":
            mode = "month"
        elif type == "周":
            mode = "week"
        elif type == "男性日":
            mode = "day_male"
        elif type == "女性日":
            mode = "day_female"
        elif type == "原创" and r18:
            await replyFunc(bot, context, "并不支持查看该榜单类型哦~", True, True)
            return True
        elif type == "原创":
            mode = "original"
        else:
            await replyFunc(bot, context, "并不支持查看该榜单类型哦~", True, True)
            return True

        if r18:
            mode += "_r18"

        date = ""
        if dateStr:
            date = dateStr
        else:
            if mode.find("day") != -1:
                date = (datetime.datetime.now() - datetime.timedelta(days=2)).strftime('%Y-%m-%d')
            elif mode.find("week") != -1:
                date = (datetime.datetime.now() - datetime.timedelta(weeks=1)).strftime('%Y-%m-%d')
            elif mode.find("month") != -1:
                date = (datetime.datetime.now() - datetime.timedelta(weeks=4)).strftime('%Y-%m-%d')
            else:
                date = (datetime.datetime.now() - datetime.timedelta(days=2)).strftime('%Y-%m-%d')

        result = api.illust_ranking(mode=mode, date=date)
        if result:
            if result.get("illusts"):
                imgList = []
                queryType = date + type + "榜"
                for resultItem in result["illusts"]:
                    result = {
                        "title" : resultItem["title"],
                        "author" : resultItem["user"]["name"],
                        "pid" : resultItem["id"]
                    }
                    if proxy:
                        result["imgUrl"] = resultItem["image_urls"]["large"].replace("i.pximg.net", proxy)
                    else:
                        result["imgUrl"] = resultItem["image_urls"]["large"]
                    imgList.append(result)
                url = await shortenUrl(await getRankingContent(imgList, queryType))
                msg = ""
                if dateStr == None:
                    msg += "未指定日期，自动获取{0}的{1}榜榜单哦~\n".format(date, type)
                msg += url
                await replyFunc(bot, context, msg, True, True)
                return True
            else:
                msgText = "请求{0}的{1}榜单失败，可能是该日期的榜单还未更新，试着用“惠酱来份p站榜单 date:yyyy-mm-dd”的格式指定日期检索榜单吧~".format(date, type)
                await replyFunc(bot, context, msgText, True, True)
                return True
        else:
            await replyFunc(bot, context, "榜单模块查询错误~", True, True)
            return True
    else:
        return False


loginToPixiv()