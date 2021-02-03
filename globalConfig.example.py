config = \
{
    # 反向代理配置
    "cq-reservsews": {
        "host": "127.0.0.1",
        "port": 7700,
        "accessToken": ""
    },
    # 机器人配置
    "bot": {
        "debug": True
    },
    # setu功能配置
    "setu": {
        # 开关
        "enable": True,
        # setu的api的apikey列表
        # 如果拥有多个apikey的话每次调用涩图都会从apikey列表里随机抽取一个apikey
        "apikeys": [],
        # 是否允许私聊使用
        "allowPM": True,
        # p站图片代理地址
        "pximgProxy": "i.pixiv.cat",
        # 是否控制图片最大不超过1200
        "size1200": True,
        # 以下四个选项可以每个群拥有自己的自定义选项
        # 撤回时间 若为0则不撤回
        "deleteTime": 60, 
        # 群调用涩图的cd 若为0 则0cd
        # 私聊不受此配置影响
        "cd": 0,
        # 每个群成员调用setu的次数限制 私聊则不受此限制
        "limit": 30,
        # 是否允许R18
        "r18": False,
        # 以上四个选项可以在下面groupCustom中每个群拥有自己的自定义选项
        # 安全模式 若开启则每次发送涩图时只发送一条包含图片的短链接 不会直接发在群里
        # 可以节省带宽 也可以更加的安全
        # 受下面的webRoute功能开关所影响
        "safeMode": True,
        # 每个群的个性化设定 接收到群消息时会优先从个性化设置中找设定项
        # 若没有相关设定项则从上面的公共设定中获取
        "groupCustom":{
            "123123132" : {
                "enable": False,
                "deleteTime": 60, 
                "cd": 0,
                "limit": 30,
                "r18": False
            }
        }
    },
    # 匹配接受到消息的正则表达式列表 若是发送过来的消息有相应匹配 则会触发相应的功能
    "regs": {
        # 开启搜图功能的正则表达式
        "searchModeOn": "^beta酱搜[图圖]$",
        # 开启搜本子功能的正则表达式
        "searchModeOnDoujin": "^beta酱搜本子$",
        # 开启搜动画功能的正则表达式
        "searchModeOnAnime": "^beta酱搜动[画漫]$",
        # 关闭搜图、本子、动画功能的正则表达式
        "searchModeOff": "^[谢謝]+beta酱$",  
        # 申请setu的正则表达式（带命名组
        "setu": "^beta酱.*[来來发發给給][张張个個幅点點份]?(?P<r18>[Rr]18的?)?(?P<keyword>.*?)?的?[色涩瑟][图圖]|^--setu$",
        # 按P站id搜图的正则表达式
        "watchPixivIMG": "^beta酱.*[看搜][pP][站][图圖][:： ]*(?P<pid>.*)",
        # P站排行榜的正则表达式
        "watchPixivRanking": "^beta酱.*[来來发發给給][张張份]?[pP][站](?P<r18>[Rr]18的?)?(?P<type>.*?)[榜] ?([Dd][Aa][Tt][Ee][:： ](?P<dateStr>.*))?"
},
    "replys": {
        # 当私聊或群聊at并未触发任何功能时的默认回复
        "default": "干啥！有事上奏没事退朝",

        # 以下关于setu功能的回复
        # setu功能调用额度达到上限
        "setuQuotaExceeded": "图太涩了，爷先冲了",
        # setu功能调用频率太高 间隔时间少于cd数时的回复
        "setuCdLimit": "您冲得太快了，小心炸膛哦~",
        # 群员当日调用setu次数达到上限
        "setuCountLimit": "为了您的身体健康与生命安全，您今天不能再冲了~",
        # 功能不开放时的回复
        "setuReject": "很抱歉，该功能暂不开放_(:3」」",
        #r18功能不允许开启时的回复
        "setuR18NotAllow": "你这淫虫，留在这世界上只会把米吃贵！！！（该群并不开放r18功能",
        # 以上关于setu功能的回复

        # 以下关于搜图功能的回复
        # 搜索失败的回复
        "searchFailed": "搜索失败惹 QAQ\n有可能是服务器网络爆炸，请重试一次，或尝试二次截图后发送",
        # 功能不开放时的回复
        "searchReject": "很抱歉，该功能暂不开放_(:3」」",
        # 群员搜索功能调用次数达到当日上限时的回复
        "searchCountLimit": "为了您的身体健康与生命安全，您今天不能再冲了~",
        # 开启搜图模式的回复
        "searchModeOn": "了解～请发送图片吧！支持批量噢！\n如想退出搜索模式请发送“谢谢beta酱”",
        # 已经在搜图模式下再次开启搜图模式的回复
        "searchModeAlreadyOn": "您已经在搜图模式下啦！\n如想退出搜索模式请发送“谢谢beta酱”",
        # 关闭搜图模式的回复
        "searchModeOff": "不用谢～",
        # 已经关闭搜图模式再次关闭时的回复
        "searchModeAlreadyOff": "にゃ～",
        # 搜图功能超市未关闭的回复
        "searchModeTimeout": "由于超时，已为您自动退出搜图模式，以后要记得说“谢谢beta酱”来退出搜图模式噢"
        # 以上关于搜图功能的回复
  
    },
    # 关于搜图功能的配置项
    "picSearch":{
        # 搜图模式总开关
        "enable": True,
        # 是否隐藏搜索缩略图
        "hideImg": False,
        # 群员每日查询次数限制
        "limit": 10,
        # 搜图模式的开启时间（超过这个时间惠自动关闭
        "timeout": 60,
        # 群组的自定义设置（类似涩图功能的自定义设置
        # 允许自定义enable和limit
        "groupCustom":{
            "123456":{
                "enable":True,
                "limit":5
            }
        },
        # 关于saocenao的设置
        "saucenao": {
            # saucenao开启开关
            "enable":True,
            # saucenao域名列表（大于一个时会随机抽取一个使用
            "saucenaoHost": ["saucenao.com"],
            # saucenao的apikey（saucenao不允许不带apikey请求搜图结果
            "saucenaoApiKey": "",
            # 当同步率低于最低限时不显示缩略图
            "hideImgWhenLowAcc": False,
            # 同步率的最低限
            "saucenaoLowAcc": 60,
            # 当低于同步率最低限时是否自动使用ascii2d搜图
            "useAscii2dWhenLowAcc": True,
            # 当saucenao api达到当日调用次数上限时是否自动使用ascii2d搜图
            "useAscii2dWhenQuotaExcess": True,
            # 当搜索结果来自danbooru时是否从danbooru获取结果（在国内不太好使
            "autoGetSourceFromDanbooru": False
        },
        # 关于whatanime的设置
        "whatanime":{
            # whatanime总开关
            "enable":True,
            # whatanime域名列表（大于一个时会随机抽取一个使用
            "whatanimeHost": ["trace.moe"],
            # whatanime的token（可选
            "whatanimeToken": "",
            # 当结果时r18时是否隐藏缩略图
            "hideImgWhenWhatanimeR18": True
        },
        # 关于ascii2d的设置
        "ascii2d":{
            # ascii2d总开关
            "enable": True,
            # ascii2d域名列表（大于一个时会随机抽取一个使用
            "ascii2dHost": ["ascii2d.net"]
        },
        # 关于nhentai的设置
        "nhentai":{
            # nhentai总开关
            "enable": True,
            # 是否隐藏缩略图（大概率有r18缩略图建议隐藏
            "hideImg": False,
            # nhentai api地址（代理用
            "nhentaiApiHost": "www.example.com",
            # nhentai cdn地址（代理用
            "nhentaiCdnHost": "www.example.com",
            # nhentai 本子地址（聊天中发送用
            "nhentaiUrlHost": "www.example.com"
            # 不带http:// https://
        }
    },
    # 反bilibili小程序设置
    "antiBiliMiniApp":{
        # 反bilibili小程序开关
        "enable": True,
        "getVideoInfo": True
    },
    # p站按id搜图 搜榜单设置
    # p站发送东西的结果都会以短链接的形式呈现 与短路由功能关系密切
    "pixiv":{
        # p站相关功能总开关
        "enable": True,
        # 是否允许r18 榜单 榜单 榜单 榜单
        "r18": False,
        # p站登录的生存周期 p站登录后 超过这个时间会触发重新登录
        "loginttl": 3600,
        # 图片代理（国内无法直接访问pixiv
        "pximgProxy": "i.pixiv.cat",
        # 使用p站功能需要账号密码
        "username": "",
        "password": ""
    },
    # 短地址路由功能
    "webRoute":{
        # 短地址路由功能
        "enable":True,
        # 在聊天时发送的短地址的域名（可以填写自己的域名但是必须解析到该机器人所在的ip地址上
        # 发送时会将http://{{ 指定的域名 }}:机器人的反代端口号/{{ 生成的短地址 }}发送出去
        "apiAddress": "127.0.0.1",
        # 短地址的存活时长 单位second
        "ttl":3600,
        # 生成的短地址长度
        "urlLength":6
    }
}

# 下面这些不要改
modeDict = {
  "all": 999,
  "pixiv": 5,
  "danbooru": 9,
  "doujin": 18,
  "anime": 21
}
# 上面这些不要改
