from .utils import startSchedule
from globalConfig import modeDict

import time


def getKey(uid, groupid):
	key = str(uid)
	if groupid:
		key += str(groupid)
	return key


class Logger:
	# 返回值表
	success = 0
	setuCdLimit = -10
	setuCountLimit = -11
	searchCountLimit = -20
	# 返回值表

	def __init__(self, *args, **kwargs):
		self.searchCount = {}

		startSchedule(86400, lambda: self.searchCount.clear())


	def initUserInfo(self, uid, groupid):
		self.searchCount[getKey(uid, groupid)] = {
			"setu":{
				"lastQueryTime" : -1,
				"count" : 0
			},
			"search":{
				"count" : 0,
				"isOpen": False,
				"mode": modeDict["all"],
				"timer": None
			}
		}


	def getSearchMode(self, uid, groupid):
		if self.searchCount.get(getKey(uid, groupid)) == None:
			self.initUserInfo(uid, groupid)
		return {
			"isOpen": self.searchCount[getKey(uid, groupid)]["search"]["isOpen"],
			"mode": self.searchCount[getKey(uid, groupid)]["search"]["mode"]
		}


	def setSearchMode(self, uid, groupid, isOpen:bool, mode:int, timeout = 0, func = None):
		if self.searchCount.get(getKey(uid, groupid)) == None:
			self.initUserInfo(uid, groupid)
		self.searchCount[getKey(uid, groupid)]["search"]["isOpen"] = isOpen
		self.searchCount[getKey(uid, groupid)]["search"]["mode"] = mode
		def resetSearchMode():
			self.searchCount[getKey(uid, groupid)]["search"]["isOpen"] = False
			self.searchCount[getKey(uid, groupid)]["search"]["mode"] = modeDict["all"]
			if func != None:
				func()
		if timeout != 0:
			self.searchCount[getKey(uid, groupid)]["search"]["timer"] = startSchedule(timeout, resetSearchMode)

	def cancelSearchMode(self, uid, groupid):
		if self.searchCount.get(getKey(uid, groupid)) == None:
			self.initUserInfo(uid, groupid)
		self.searchCount[getKey(uid, groupid)]["search"]["isOpen"] = False
		self.searchCount[getKey(uid, groupid)]["search"]["mode"] = modeDict["all"]
		if self.searchCount[getKey(uid, groupid)]["search"]["timer"]:
			self.searchCount[getKey(uid, groupid)]["search"]["timer"].cancel()


	def doneSearch(self, uid, groupid, key):
		if self.searchCount.get(getKey(uid, groupid)) == None:
			self.initUserInfo(uid, groupid)
		if key == "setu":
			self.searchCount[getKey(uid, groupid)][key]["lastQueryTime"] = time.time()
			self.searchCount[getKey(uid, groupid)][key]["count"] += 1
		elif key == "search":
			pass

	def canSearch(self, uid, groupid, limit, key) -> int:
		if self.searchCount.get(getKey(uid, groupid)) == None:
			self.initUserInfo(uid, groupid)
		if key == "setu":
			if self.searchCount[getKey(uid, groupid)][key]["lastQueryTime"] == -1:
				return self.success
			if time.time() - self.searchCount[getKey(uid, groupid)][key]["lastQueryTime"] < limit["cd"]:
				return self.setuCdLimit
			if self.searchCount[getKey(uid, groupid)][key]["count"] >= limit["limit"]:
				return self.setuCountLimit
			return self.success
		elif key == "search":
			if self.searchCount[getKey(uid, groupid)][key]["count"] >= limit["limit"]:
				return self.searchCountLimit
			return self.success

