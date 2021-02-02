from .common import getResultMsg, getErrorMsg

import re
import json
import random
import aiohttp

from globalConfig import config


async def whatanimeSearch(imgUrl, bot):
	setting = config["picSearch"]["whatanime"]
	token = setting["whatanimeToken"] if setting["whatanimeToken"] else ""
	host = setting["whatanimeHost"][int(random.random() * len(setting["whatanimeHost"]))]
	warnMsgs = []
	if host == "trace.moe":
		host = "https://" + host
	elif re.match("^https?:\/\/", host) == None:
		host = "http://" + host

	msg = ""
	success = False
	excess = False

	response = {
			"status": -1,
			"data": "Network Error"
		}
	async with aiohttp.request("GET", host + "/api/search", params={"url": imgUrl, "token": token}) as res:
		response["status"] = res.status
		response["data"] = await res.text()
	if response["status"] == 200:
		data = json.loads(response["data"])
		neededRes = data["docs"][0]

		#信息获取
		limit = data["limit"]
		limit_ttl = data["limit_ttl"]

		similarity = round(neededRes["similarity"] * 100)
		jpName = neededRes["title_native"] if neededRes["title_romaji"] else ""
		romaName = neededRes["title_romaji"] if neededRes["title_romaji"] else ""
		cnName = neededRes["title_chinese"] if neededRes["title_chinese"] else ""
		posTime = "%d:%d" % (int(neededRes["at"] / 60), int(neededRes["at"] % 60))
		isR18 = neededRes["is_adult"]
		anilistID = neededRes["anilist_id"]
		episode = neededRes["episode"] if neededRes["episode"] else "-"

		engineTitle = "WhatAnime ({0}%)\n该截图出自第{1}集的{2}".format(similarity, episode, posTime)
		title = ""
		if cnName:
			title = cnName
		elif jpName:
			title = jpName
		elif romaName:
			title = romaName
		thumbnail = None
		otherInfo = ["作品详情："]

		aniInfoResponse = {
			"status": -1,
			"data": "Network Error"
		}
		async with aiohttp.request("GET", host + "/info?anilist_id=" + str(anilistID)) as res:
			aniInfoResponse["status"] = res.status
			aniInfoResponse["data"] = await res.text()
		if aniInfoResponse["status"] == 200:
			aniInfoResult = json.loads(aniInfoResponse["data"])[0]
			#信息组拼
			#类型
			type = aniInfoResult["type"] + " - " + aniInfoResult["format"]
			#播出时间
			startTime = "%d-%d-%d" % (
				aniInfoResult["startDate"]["year"],
				aniInfoResult["startDate"]["month"],
				aniInfoResult["startDate"]["day"],
			)
			endTime = None
			if aniInfoResult["endDate"]["year"] != None and aniInfoResult["endDate"]["month"] != None and aniInfoResult["endDate"]["day"] != None:
				endTime = "%d-%d-%d" % (
					aniInfoResult["endDate"]["year"],
					aniInfoResult["endDate"]["month"],
					aniInfoResult["endDate"]["day"],
				)
			#缩略图
			thumbnail = None if isR18 and setting["hideImgWhenWhatanimeR18"] else aniInfoResult["coverImage"]["large"]
			synonyms = aniInfoResult["synonyms_chinese"] if aniInfoResult["synonyms_chinese"] else []
			otherInfo.append("罗马音：" + romaName)
			otherInfo.append("日文名：" + jpName)
			otherInfo.append("中文名：" + cnName)
			otherInfo.append("别名：" + "、".join(synonyms))
			otherInfo.append("类型：" + type)
			otherInfo.append("播出时间：" + startTime)
			if endTime:
				otherInfo.append("完结时间：" + endTime)
			if isR18:
				otherInfo.append("R18注意！")
		else:
			otherInfo.append("获取番剧信息失败~")
		success = True
		other = "\n".join(otherInfo)
		if limit < 3:
			warnMsgs.append("WhatAnime-%s：注意，%d秒内搜索次数仅剩%d次" % (host, limit_ttl, limit))
		msg = getResultMsg(engineTitle, title, None, thumbnail, None, None, None, other)
	elif response["status"] == 413:
		msg = getErrorMsg("WhatAnime：图片体积太大啦，请尝试发送小一点的图片（或者也可能是您发送了GIF，是不支持的噢）")
	elif response["status"] == 429:
		msg = getErrorMsg("WhatAnime：短时间内的检索次数用光啦，请等待一小会儿之后再试哦~")
		excess = True
	else:
		bot.logger.warning("WhatAnime预料之外的返回结果：" + response["data"])
		msg = getErrorMsg("WhatAnime-{%s} %s" % (host, response["data"]))

	warnMsg = "\n".join(warnMsgs)
	return {
		"success": success,
		"msgs": [msg],
		"warnMsg": warnMsg,
		"excess": excess,
	}
