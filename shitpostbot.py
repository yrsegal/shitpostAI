# coding=utf-8
from __future__ import print_function
from util import *
cprintconf.name="Shitposting"
cprintconf.color=bcolors.BROWN
config = Config(CONFIGDIR)
import random
import tweepy
import time
import json
import os
import sys

def weightlist(obj):
	l = []
	for i in obj:
		if isinstance(obj[i], int):
			for j in range(obj[i]): l.append(i)
	return l

class Words(Config):
	def flatlist(self):
		self.checkreload()
		return list(self.data)
	def weighted_list(self, tag):
		return weightlist(self[tag])

def randpop(weight, identifier):
	if not len(weight):
		return random.choice(genobjects[identifier])
	x = random.choice(weight)
	while x in weight:
		weight.remove(x)
	return x

path = os.path.dirname(__file__)

if not os.path.exists(os.path.join(path, "words.json")):
	raise ValueError("There aren't any words to generate from!")

genobjects = Words(os.path.join(path, "words.json"))
def generate(debug=False):
	plurals = genobjects.weighted_list('plurnoun')
	adjectives = genobjects.weighted_list('adjective')
	nouns = genobjects.weighted_list('noun')
	adverbs = genobjects.weighted_list('adverb')
	pastverbs = genobjects.weighted_list('pastverb')
	verbs = genobjects.weighted_list('verb')
	base = random.choice(genobjects.weighted_list('base'))

	while "%" in base:
		if debug: cprint(base)
		base = base.replace("%s", randpop(plurals, 'plurnoun'), 1)
		base = base.replace("%j", randpop(adjectives, 'adjective'), 1)
		base = base.replace("%n", randpop(nouns, 'noun'), 1)
		base = base.replace("%a", randpop(adverbs, 'adverb'), 1)
		while "%ved" in base:
			base = base.replace("%ved", randpop(pastverbs, 'pastverb'), 1)
		base = base.replace("%v", randpop(verbs, 'verb'), 1)
		base = base.replace("%i", str(random.randint(2, 20)), 1)
	if debug: cprint(base)
	if "override" in config:
		tempconf = config.data
		cprint("Overriding generated text.", color=bcolors.YELLOW)
		base = config["override"]
		cprint(format("New text: {endc}{base}", base=base), color=bcolors.YELLOW)
		del tempconf["override"]
		json.dump(tempconf, open(os.path.join(path, "shitpostconfig.json"), "w"), indent = 2)
	return base

if not os.path.exists(os.path.join(path, "authkeys.json")):
	json.dump({
		"TWITTER_CONSUMER_KEY": "",
		"TWITTER_CONSUMER_SECRET": "",
		"TWITTER_ACCESS_KEY": "",
		"TWITTER_ACCESS_SECRET": ""
		}, open(os.path.join(path, "authkeys.json"), "w"), indent=2, sort_keys=True)

a = json.load(open(os.path.join(path, "authkeys.json")))

auth = tweepy.OAuthHandler(a["TWITTER_CONSUMER_KEY"], a["TWITTER_CONSUMER_SECRET"])
auth.set_access_token(a["TWITTER_ACCESS_KEY"], a["TWITTER_ACCESS_SECRET"])
api = tweepy.API(auth)	

def connected_to_internet():
	return bool(getIps(test=True))
def getIps(test=False):
	"""
	Get the IPs this device controls.
	"""
	try:
		from netifaces import interfaces, ifaddresses, AF_INET
	except: return ["install netifaces >:("]
	ips = []
	for ifaceName in interfaces():
		addresses = [i['addr'] for i in ifaddresses(ifaceName).get(AF_INET, [{"addr":"not found"}])]
		if "not found" not in addresses and "127.0.0.1" not in addresses:
			ips += addresses
	if not ips and not test: 
		ips.append("localhost")
	return ips

def main():
	while True:
		try:
			text = generate(debug=True)
			
			while not connected_to_internet():
				time.sleep(1)
			try:
				api.update_status(status=text)
				cprint(format("Made tweet: {text}", text=text))
			except Exception, e:
				if isinstance(e, KeyboardInterrupt):
					break
				cprint(tbformat(e, "Error sending tweet:"), color=bcolors.YELLOW)
			started = time.time()
			stopped = time.time()
			cprint("Slept 0 seconds.")
			while stopped-started < config.get("time", 360):
				if not int(stopped-started) % config.get("notifytime", 60) and int(stopped-started) != 0: 
					print(bcolors.REMAKELINE, end="")
					cprint("Slept "+str(int(stopped-started))+" seconds.")
				time.sleep(1)
				stopped = time.time()

			if int(stopped-started) != config.get("notifytime", 60): print(bcolors.REMAKELINE, end="")
			cprint("Slept "+str(config["time"])+" seconds.")
		except KeyboardInterrupt:
			pass


if __name__ == "__main__": main()
