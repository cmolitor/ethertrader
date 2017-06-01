import urllib2
import json
import logging
import sys
import ConfigParser
from pushbullet import Pushbullet
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from collections import deque

# print(sys.path)

## Todos
# heart beat every 24 hours
# intervals in config.ini
# price difference in percent in config.ini

logging.basicConfig()

#listPrices = collections.deque(maxlen=5)
listPrices = deque(maxlen=1440)
currentPrice = 0.0
oldMinPrice = 1000.0
oldMaxPrice = 0.0

# https://coinmarketcap-nexuist.rhcloud.com/api/eth
# https://min-api.cryptocompare.com/data/pricemulti?fsyms=ETH,DASH&tsyms=BTC,USD,EUR
# https://min-api.cryptocompare.com/data/pricemulti?fsyms=ETH&tsyms=EUR

def getPrices():
	global currentPrice
	# Get Ether prices
	response = urllib2.urlopen('https://min-api.cryptocompare.com/data/pricemulti?fsyms=ETH&tsyms=EUR')
	data = json.loads(response.read())

	# extract price in euro
	currentPrice = data["ETH"]["EUR"]
	# print priceEur

	listPrices.append(currentPrice)
	# print listPrices, min(listPrices), max(listPrices)

def evalPrices():
	global currentPrice
	global oldMinPrice
	global oldMaxPrice

	# print "---- Start Eval prices ----"
	print currentPrice, oldMinPrice, oldMaxPrice

	if currentPrice < 0.995 * oldMinPrice:
		print "New min price: ", currentPrice, " Old min Price: ", oldMinPrice
		push = pb.push_note("New min price", "{:.2f}".format(currentPrice)) 
		oldMinPrice = currentPrice

	if currentPrice > 1.005 * oldMaxPrice:
		print "New max price: ", currentPrice, " Old max Price: ", oldMaxPrice
		push = pb.push_note("New max price", "{:.2f}".format(currentPrice)) 
		oldMaxPrice = currentPrice

	oldMinPrice = min(listPrices)
	oldMaxPrice = max(listPrices)

	# print "---- End Eval prices ----"


print "====== Start Program ======="

# Load data from config.ini
config = ConfigParser.ConfigParser()
config.readfp(open(r'config.ini'))
# pushbullet token
token = config.get('General', 'token')

# Connect to Pushbullet with specified token
pb = Pushbullet(token)

# Start the scheduler
sched = BlockingScheduler()

sched.add_job(getPrices, 'interval', seconds=int(60))
sched.add_job(evalPrices, 'interval', seconds=int(300))
sched.start()