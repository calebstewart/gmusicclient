# -*- coding: utf-8 -*-
# @Author: caleb
# @Date:   2016-02-27 14:19:14
# @Last Modified by:   caleb
# @Last Modified time: 2016-02-27 14:27:47
from colorama import Fore
LOG_LEVELS = [Fore.GREEN + "[info]\t" + Fore.RESET,
				Fore.YELLOW + "[warn]\t" + Fore.RESET,
				Fore.RED + "[error]\t" + Fore.RESET ]
INFO = 0
WARNING = 1
ERROR = 2

def info(message):
	log(INFO, message)
def warn(message):
	log(WARNING, message)
def error(message):
	log(ERROR, message)

def log(lvl, message):
	if lvl > 2 or lvl < 0:
		log(ERROR, "unknown log level " + str(lvl))
	print LOG_LEVELS[lvl] + message