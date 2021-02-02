from .common import getErrorMsg, getResultMsg

import re
import json
import aiohttp

from globalConfig import config


# TODO nhentai只有开启了代理或者反代才能链接 所以这个功能咕咕咕
# https://nhentai.unblock.my.id/api/galleries/search?query=lovelive
async def nhentaiSearch(doujinName : str, bot):
	ext = {"j" : "jpg", "p": "png", "g": "gif"}

	setting = config["picSearch"]["nhentai"]
	ApiHost = setting["nhentaiApiHost"]
	CdnHost = setting["nhentaiCdnHost"]
	UrlHost = setting["nhentaiUrlHost"]

	name = re.sub(r"\s", "", doujinName)
	success = False
	msg = getErrorMsg("")

	response = {
		"status": -1,
		"data": "Network Error"
	}
	async with aiohttp.request("GET", "https://" + ApiHost + "/api/galleries/search", params={"query": name, "page": 1, "sort": "popular"}) as res:
		response["status"] = res.status
		response["data"] = await res.text()
	if res.status == 200:
		result = json.loads(response["data"])
		if len(result.get("result")) != 0:
			neededRes = result["result"][0]
			url = "https://" + UrlHost + "/g/" + str(neededRes["id"])
			title = ""
			if neededRes["title"].get("japanese"):
				title = neededRes["title"].get("japanese")
			elif neededRes["title"].get("english"):
				title = neededRes["title"].get("english")
			elif neededRes["title"].get("pretty"):
				title = neededRes["title"].get("pretty")
			thumbnail = None if setting["hideImg"] else "https://" + CdnHost + "/galleries/" + str(
				neededRes["media_id"]) + "/cover." + ext[neededRes["images"]["thumbnail"]["t"]]
			tags = []
			for tag in neededRes["tags"]:
				tags.append(tag["name"])
			other = "tags:" + ",".join(tags)
			msg = getResultMsg("nhentai", title, None, thumbnail, url, None, other)
			success = True
	else:
		bot.logger.error("nhentai发生不可预料的错误：%s" % (response["data"]))
		msg = getErrorMsg("nhentai发生不可预料的错误。")
	return {
		"success": success,
		"msgs" : [msg],
	}
