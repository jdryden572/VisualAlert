import calendar
import logging
import json
import requests
from requests_negotiate_sspi import HttpNegotiateAuth
import time
import datetime

logger = logging.getLogger('PhoneStatsAPI')
#logging.basicConfig(level=logging.DEBUG)

MAX_STALE = 15 # Max allowable staleness in TSDATA response

class PhoneStatsAPI:
	def __init__(self, URL, timeout=MAX_STALE):
		self.URL = URL
		self.timeout = timeout
		self.session = requests.Session()
		self.session.auth = HttpNegotiateAuth()
		
	def get_stats(self):
		logger.debug('Accessing source URL...')
		try:
			response = self.session.get(self.URL)
		except:
			# exception means general connection issue to machine URL
			logger.warning('CANNOT CONNECT TO PHONE QUEUE STATUS PAGE')
			logger.warning('URL: {} Check network connection and destination URL.'.format(self.URL))
			return None, None, None, True
		if not response.ok:
			# Bad status means connection succeeded but something wrong with machine
			logger.warning('Bad status ' + str(response.status_code) + ' received.')
			return None, None, None, True
		if 'X-Crawl-Stale-Seconds' in response.headers:
			logger.debug("'X-Crawl-Stale-Seconds': " + response.headers['X-Crawl-Stale-Seconds'])
			if int(response.headers['X-Crawl-Stale-Seconds']) > self.timeout:
				logger.warning('Response data stale: ' + response.headers['X-Crawl-Stale-Seconds'] + ' seconds')
				return None, None, None, True
		else:
			logger.warning("'X-Crawl-Stale-Seconds' header missing from HTTP response")
		if 'X-Crawl-Timestamp' in response.headers:
			logger.debug("'X-Crawl-Timestamp': " + response.headers['X-Crawl-Timestamp'])
			crawlTime = calendar.timegm(datetime.datetime.strptime(response.headers['X-Crawl-Timestamp'], '%Y-%m-%dT%H:%M:%S.%fZ').timetuple())
			staleSeconds = time.time() - crawlTime
			logger.debug("Stale time: " + str(staleSeconds))
			if staleSeconds > self.timeout:
				logger.warning('Response data stale: ' + str(staleSeconds) + ' seconds')
				return None, None, None, True
		logger.debug('Success.')
		try:
			data = json.loads(response.content.decode('utf-8'))
			logger.debug(data)
			calls = data['queueCount']
			ready = data['agentsAvailable']
			earliestStr = data['earliestQueueTime']
			if earliestStr is not None:
				earliest = calendar.timegm(datetime.datetime.strptime(earliestStr, '%Y-%m-%dT%H:%M:%S.%fZ').timetuple())
				timeInQueue = time.time() - earliest
			else:
				timeInQueue = 0
			return int(ready), int(calls), timeInQueue, False
		except:
			logger.warning('Parse error on returned data')
			return None, None, None, True