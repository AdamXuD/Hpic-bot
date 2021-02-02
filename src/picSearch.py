from .logger import Logger
from .utils import isAtMe
from globalConfig import config, modeDict

import re
import asyncio
from aiocqhttp import MessageSegment

from .picSearcher.ascii2d import ascii2dSearch
from .picSearcher.saucenao import saucenaoSearch
from .picSearcher.whatanime import whatanimeSearch
from .picSearcher.nhentai import nhentaiSearch
from .picSearcher.common import getErrorMsg



async def openPicSearcherMode(context, replyFunc, logger, bot):
	regexs = config["regs"]
	mode = None
	modeStr = ""
	if re.search(regexs["searchModeOn"], context.message) != None:
		mode = modeDict["all"]
	elif re.search(regexs["searchModeOnDoujin"], context.message) != None:
		mode = modeDict["doujin"]
		modeStr = "\n当前在本子模式"
	elif re.search(regexs["searchModeOnAnime"], context.message) != None:
		mode = modeDict["anime"]
		modeStr = "\n当前在动画模式"
	if mode != None:
		if context.group_id == None and mode == modeDict["all"]:
			await replyFunc(bot, context, "私聊模式下直接发图就可以了哦~", True)
		else:
			if logger.getSearchMode(context.user_id, context.group_id)["isOpen"]:
				await replyFunc(bot, context, config["replys"]["searchModeAlreadyOn"], True)
			else:
				await replyFunc(bot, context, config["replys"]["searchModeOn"] + modeStr, True)
				logger.setSearchMode(context.user_id, context.group_id, True, mode, config["picSearch"]["timeout"], lambda: asyncio.run(replyFunc(bot, context, config["replys"]["searchModeTimeout"], True, True)))
		return True
	else:
		return False


async def closePicSearcherMode(context, replyFunc, logger, bot):
	regexs = config["regs"]
	if re.search(regexs["searchModeOff"], context.message) != None:
		if logger.getSearchMode(context.user_id, context.group_id)["isOpen"]:
			logger.cancelSearchMode(context.user_id, context.group_id)
			await replyFunc(bot, context, config["replys"]["searchModeOff"], True)
			return True
		else:
			await replyFunc(bot, context, config["replys"]["searchModeAlreadyOff"], True)
			return True
	else:
		return False


def getCustomSetting(uid, key:str):
    setting = config["picSearch"]
    if setting["groupCustom"].get(str(uid)) != None:
        if setting["groupCustom"][str(uid)].get(key) != None:
            return setting["groupCustom"][str(uid)][key]
    return setting[key]


def getImgs(msg:str):
	reg = re.compile("\[CQ:image,file=([^,]+),url=([^\]]+)\]")
	ret = []
	for item in reg.findall(msg):
		ret.append({
			"file": item[0],
			"url" : item[1]
		})
	return ret


def hasImage(msg:str):
	return msg.find("[CQ:image") != -1


async def picSearch(context, replyFunc, logger, bot):
	if hasImage(context.message):
		searchMode = logger.getSearchMode(context.user_id, context.group_id)
		setting = config["picSearch"]
		replys = config["replys"]
		rejectReply = replys["searchReject"]
		enable = False
		allLimit = {
			"limit": 0
		}
		if context.group_id:
			if searchMode["isOpen"] == False and isAtMe(context) == False:
				return False
			enable = getCustomSetting(context.group_id, "enable")
			allLimit["limit"] = getCustomSetting(context.group_id, "limit")
		else:
			enable = setting["enable"]
			allLimit["limit"] = setting["limit"]

		canSearch = logger.canSearch(context.user_id, context.group_id, allLimit, "search")
		if canSearch != 0:
			if canSearch == Logger.searchCountLimit:
				await replyFunc(bot, context, MessageSegment.text(replys["searchCountLimit"]), True)
			return True


		if enable:
			imgs = getImgs(context.message)
			useSauceNao = True
			useAscii2d = False
			useWhatAnime = False
			useNhentai = False

			mode = searchMode["mode"]
			if mode == modeDict["doujin"]:
				useNhentai = True
			elif mode == modeDict["anime"]:
				useWhatAnime = True

			for img in imgs:
				saucenaoRes = None
				if useSauceNao:
					if setting["saucenao"]["enable"]:
						saucenaoRes = await saucenaoSearch(img["url"], bot)
						if saucenaoRes["msgs"]:
							for msg in saucenaoRes["msgs"]:
								await replyFunc(bot, context, msg, True, True)
						if saucenaoRes["excess"] or saucenaoRes["lowAcc"]:
							useAscii2d = True
						if saucenaoRes["warnMsg"]:
							await replyFunc(bot, context, saucenaoRes["warnMsg"], True, True)
					else:
						await replyFunc(bot, context, getErrorMsg("SauceNAO:" + rejectReply), True, True)
				if useAscii2d:
					if setting["ascii2d"]["enable"]:
						ascii2dRes = await ascii2dSearch(img["url"], bot)
						if ascii2dRes["msgs"]:
							for msg in ascii2dRes["msgs"]:
								await replyFunc(bot, context, msg, True, True)
					else:
						await replyFunc(bot, context, getErrorMsg("Ascii2d:" + rejectReply), True, True)
				if useWhatAnime:
					if setting["whatanime"]["enable"]:
						whatanimeRes = await whatanimeSearch(img["url"], bot)
						if whatanimeRes["msgs"]:
							for msg in whatanimeRes["msgs"]:
								await replyFunc(bot, context, msg, True, True)
						if whatanimeRes["warnMsg"]:
							await replyFunc(bot, context, whatanimeRes["warnMsg"], True, True)
					else:
						await replyFunc(bot, context, getErrorMsg("WhatAnime:" + rejectReply), True, True)
				if useNhentai and saucenaoRes["doujinName"] != None:
					if setting["nhentai"]["enable"]:
						nhentaiRes = await nhentaiSearch(saucenaoRes["doujinName"], bot)
						if nhentaiRes["msgs"]:
							for msg in nhentaiRes["msgs"]:
								await replyFunc(bot, context, msg, True, True)
					else:
						await replyFunc(bot, context, getErrorMsg("nhentai:" + rejectReply), True, True)
			return True
		else:
			await replyFunc(bot, context, getErrorMsg(rejectReply), True, True)
			return True
	else:
		return False
