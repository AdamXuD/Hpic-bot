from globalConfig import config

import base64
from threading import Timer
from aiocqhttp import Event, Message, MessageSegment, NetworkError


def isAtMe(context):
    if context.raw_message and context.raw_message.find("[CQ:at,qq={}]".format(context.self_id)) != -1:
        return True
    return False


def startTimer(second, func):
    t = Timer(second, func)
    t.start()
    return t


def base64Encode(text:str):
    return str(base64.b64encode(text.encode("utf-8")))


def base64Decode(text:str):
    return base64.b64decode(text).decode("utf-8")


async def baseReplyMsg(bot, context:Event, msg):
    return await bot.send(context, msg)


async def replyMsg(bot, context : Event, msg, at = False, reply = False):
    message = Message()
    if context.detail_type != "private":
        if reply: # reply消息段静态构造没有被实现
            message.append(MessageSegment(type_ = "reply", data = {"id" : context.message_id}))
        if at:
            message.append(MessageSegment.at(context.user_id))
    if isinstance(msg, MessageSegment):
        message.append(msg)
    elif isinstance(msg, Message):
        message.extend(msg)
    elif isinstance(msg, str):
        message.append(MessageSegment.text(msg))
    if context.detail_type == "private":
        if config["bot"]["debug"] == True:
            bot.logger.info("回复私聊消息 qq = " + str(context.user_id) + "内容 = " + message.extract_plain_text()); 
    elif context.detail_type == "group":
        if config["bot"]["debug"] == True:
            bot.logger.info("回复群组消息 group = " + str(context.group_id) + "qq = " + str(context.user_id) + "内容 = " + message.extract_plain_text());
    elif context.detail_type == "discuss":
        if config["bot"]["debug"] == True:
            bot.logger.info("回复讨论组消息 discuss = " + str(context.discuss_id) + "qq = " + str(context.user_id) + "内容 = " + message.extract_plain_text());
    ret = None
    try:
        ret = await baseReplyMsg(bot, context, message)
    except NetworkError as e:
        bot.logger.warning("发生网络错误。")
    return ret
