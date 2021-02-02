from globalConfig import config

import re
from aiocqhttp import Message, MessageSegment

def getShortenPixivUrl(url) ->str:
	pidSearch = re.findall(r"pixiv.+illust_id=([0-9]+)", url)
	if pidSearch:
		return "https://pixiv.net/i/" + pidSearch[0]
	uidSearch = re.findall(r"pixiv.+member\.php\?id=([0-9]+)", url)
	if uidSearch:
		return "https://pixiv.net/u/" + uidSearch[0]
	return url

def getResultMsg(engineTitle, title = None, author = None, thumbnail = None, url = None, author_url = None, source = None, other = None) -> Message:
	message = Message()
	message.append(MessageSegment.text(engineTitle))
	if title:
		message.append(MessageSegment.text("\n"))
		message.append(MessageSegment.text("标题：「%s」" % (title)))
	if author:
		message.append(MessageSegment.text("\n"))
		message.append(MessageSegment.text("作者：「%s」" % (author)))
	if thumbnail and config["picSearch"]["hideImg"] == False:
		message.append(MessageSegment.text("\n"))
		message.append(MessageSegment.image(thumbnail))
	if url:
		message.append(MessageSegment.text("\n"))
		message.append(MessageSegment.text("URL: " + getShortenPixivUrl(url)))
	if author_url:
		message.append(MessageSegment.text("\n"))
		message.append(MessageSegment.text("Author: " + getShortenPixivUrl(author_url)))
	if source:
		message.append(MessageSegment.text("\n"))
		message.append(MessageSegment.text("Source: " + getShortenPixivUrl(source)))
	if other:
		message.append(MessageSegment.text("\n"))
		message.append(MessageSegment.text(other))
	return message


def getErrorMsg(err:str):
	return Message().append(MessageSegment.text(err))
