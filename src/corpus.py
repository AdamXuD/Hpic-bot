import re
from globalConfig import config
from aiocqhttp import Message, CQHttp

sceneDict = {
    "p": ["private"],
    "g": ["group"],
    "a": ["private", "group"]
}

async def corpus(context, replyFunc, logger, bot: CQHttp):
    setting = config["corpus"]
    list = setting["list"]

    for item in list:
        if re.search(item["regexp"], context.message):
            if sceneDict.get(item["scene"]).count(context.detail_type) != 0:
                await replyFunc(bot, context, item["reply"])
                return True
    return False

