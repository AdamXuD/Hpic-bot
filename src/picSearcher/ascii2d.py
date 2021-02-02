from .common import getResultMsg

import re
import random
import aiohttp
from bs4 import BeautifulSoup

from globalConfig import config


def getAscii2dDetail(html, baseURL):
	result = None
	soup = BeautifulSoup(html, features="html.parser")
	itembox = soup.select(".item-box")
	for item in itembox:
		link = item.select(".detail-box a")
		if len(link) != 0:
			title = link[0]
			author = link[1]
			result = {
				"thumbnail": baseURL + item.select(".image-box img")[0]["src"],
				"title": title.string,
				"author": author.string,
				"url": title["href"],
				"author_url": author["href"]
			}
			break
	return result


async def ascii2dSearch(imgUrl, bot):
	setting = config["picSearch"]["ascii2d"]
	host = setting["ascii2dHost"][int(random.random() * len(setting["ascii2dHost"]))]

	success = False
	msg = []  # 默认返回结果

	if host == "ascii2d.net":
		host = "https://" + host
	elif re.match("^https?:\/\/", host) == None:
		host = "http://" + host

	colorURL = None
	colorResponse = {
		"status": -1,
		"data": "Network Error"
	}
	async with aiohttp.request("GET", host + "/search/url/" + imgUrl) as res:
		colorResponse["status"] = res.status
		colorURL = str(res.real_url)
		colorResponse["data"] = await res.text()
	if colorResponse["status"] == 200:
		colorDetail = getAscii2dDetail(colorResponse["data"], host)
		msg.append(getResultMsg("Ascii2d色合検索", **colorDetail))

		bovwURL = colorURL.replace("/color/", "/bovw/")
		bovwResponse = {
			"status": -1,
			"data": "Network Error"
		}
		async with aiohttp.request("GET", bovwURL) as res:
			bovwResponse["status"] = res.status
			bovwResponse["data"] = await res.text()
		if bovwResponse["status"] == 200:
			bovwDetail = getAscii2dDetail(bovwResponse["data"], host)
			msg.append(getResultMsg("Ascii2d特徴検索", **bovwDetail))
			success = True
	return {
		"success": success,
		"msgs" : msg,
	}
