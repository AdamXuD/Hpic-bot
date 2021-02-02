from .common import getErrorMsg, getResultMsg

import re
import json
import random
import aiohttp
from bs4 import BeautifulSoup

from globalConfig import config


async def getSource(url:str):
	domainList = ["danbooru.donmai.us", "konachan.com", "yande.re", "gelbooru.com"]
	containDomain = False
	for domain in domainList:
		if url.find(domain) != -1:
			containDomain = True
			break
	if containDomain:
		response = {
			"status": -1,
			"data": "Network Error"
		}
		async with aiohttp.request("GET", url) as res:
			response["status"] = res.status
			response["data"] = await res.text()
		if response["status"] == 200:
			soup = BeautifulSoup(response["data"], features="html.parser")
			soup.attrs
			if url.find(domainList[0]) != -1:
				return soup.select(".image-container")[0]["data-normalized-source"]
			if url.find(domainList[1]) != -1 or url.find(domainList[2]) != -1:
				return soup.select("#stats li:contains(Source) a")[0]["href"]
			if url.find(domainList[3]) != -1:
				return soup.select("#tag-list li:contains(Source) a")[0]["href"]
	return None



async def saucenaoSearch(imgUrl, bot, db = 999):
	setting = config["picSearch"]["saucenao"]
	host = setting["saucenaoHost"][int(random.random() * len(setting["saucenaoHost"]))]
	apikey = setting["saucenaoApiKey"]
	warnMsgs = []
	other = None

	msg = getErrorMsg("") # 默认返回结果
	warnMsg = ""
	lowAcc = False
	success = False
	excess = False
	doujinName = None

	if host == "saucenao.com":
		host = "https://" + host
	elif re.match("^https?:\/\/", host) == None:
		host = "http://" + host

	response = {
		"status": -1,
		"data": "Network Error"
	}
	async with aiohttp.request("GET", host + "/search.php", params={"api_key": apikey, "db": db, "output_type": 2, "numres": 3, "url": imgUrl}) as res:
		response["status"] = res.status
		response["data"] = await res.text()
	if response["status"] == 200:
		result = json.loads(response["data"])
		if result.get("results") and len(result.get("results")) > 0:
			neededRes = {
				"short_remaining": result["header"].get("short_remaining"),  # 短时剩余
				"long_remaining": result["header"].get("long_remaining"),  # 长时剩余
				"similarity": result["results"][0]["header"].get("similarity"),  # 相似度
				"thumbnail": result["results"][0]["header"].get("thumbnail"),  # 缩略图

				"ext_urls": result["results"][0]["data"].get("ext_urls"),
				"title": result["results"][0]["data"].get("title"),  # 标题
				"member_name": result["results"][0]["data"].get("member_name"),  # 作者
				"member_id": result["results"][0]["data"].get("member_id"),  # 可能 pixiv uid

				"eng_name": result["results"][0]["data"].get("eng_name"),  # 本子名
				"jp_name": result["results"][0]["data"].get("jp_name"),  # 本子名
			}
			engineTitle = "SauceNAO ({0}%)".format(neededRes["similarity"])
			url = ""
			source = ""
			if neededRes["ext_urls"]:
				url = neededRes["ext_urls"][0]
				for item in neededRes["ext_urls"]:
					if item.find("pixiv") != -1:
						url = item
				if setting["autoGetSourceFromDanbooru"]: # 优先取danbooru地址 咕咕咕
					for item in neededRes["ext_urls"]:
						if item.find("danbooru") != -1:
							url = item
					source = getSource(url)

			author = neededRes["member_name"]
			thumbnail = None if setting["hideImgWhenLowAcc"] and neededRes["similarity"] < setting["saucenaoLowAcc"] else neededRes["thumbnail"]
			author_url = "https://pixiv.net/u/" + str(neededRes["member_id"]) if neededRes["member_id"] and url.find("pixiv.net") != -1 else None
			title = neededRes["title"] if neededRes["title"] != None else ("搜索结果" if url.find("anidb.net") == -1 else "AniDB")

			if neededRes["jp_name"]:
				doujinName = neededRes["eng_name"]
			elif neededRes["eng_name"]:
				doujinName = neededRes["jp_name"]
			if doujinName:
				other = "本子名：" + doujinName

			if neededRes["long_remaining"] < 20:
				warnMsgs.append("saucenao-%s：注意，24h内搜图次数仅剩%d次" % (host, neededRes["long_remaining"]))
			elif neededRes["short_remaining"] < 5:
				warnMsgs.append("saucenao-%s：注意，30s内搜图次数仅剩%d次" % (host, neededRes["short_remaining"]))
			if float(neededRes["similarity"]) < setting["saucenaoLowAcc"]:
				lowAcc = True
				warnMsgs.append("相似度 {}% 过低，如果这不是你要找的图，那么可能：确实找不到此图/图为原图的局部图/图清晰度太低/搜索引擎尚未同步新图".format(neededRes["similarity"]))
				warnMsgs.append("自动调用Ascii2d搜索")

			msg = getResultMsg(engineTitle, title, author, thumbnail, url, author_url, source, other)
			success = True
			warnMsg = "\n".join(warnMsgs)
		elif result["header"]["message"]:
			if result["header"]["message"] == "Specified file no longer exists on the remote server!":
				msg = getErrorMsg("该图片已过期，请尝试二次截图后发送")
			elif result["header"]["message"] == "Problem with remote server...":
				msg = getErrorMsg("saucenao-{%s} 远程服务器出现问题，请稍后尝试重试" % (host))
			else:
				bot.logger.warning("SauceNAO预料之外的返回结果：" + result)
				msg = getErrorMsg("saucenao-{%s} %s" % (host, result))
		else:
			bot.logger.error("SauceNAO错误的返回结果：" + result)
	elif response["status"] == 429:
		msg = getErrorMsg("saucenao-%s 搜索次数已达单位时间上限，请稍候再试\n自动调用Ascii2d搜索" % (host))
		excess = True
	else:
		bot.logger.error("SauceNao发生不可预料的错误：%s" % (response["data"]))
		msg = getErrorMsg("SauceNao发生不可预料的错误。")
	return {
		"success": success,
		"msgs": [msg],
		"warnMsg": warnMsg,
		"lowAcc": lowAcc,
		"excess": excess,
		"doujinName": doujinName
	}
