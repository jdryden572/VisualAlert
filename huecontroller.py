"""
huecontroller

Brett Nelson and James Dryden
OSIsoft, LLC

July 2014

Controller program fo an implementation of Philips Hue as a status indicator.

"Hue Personal Wireless Lighting" is a trademark owned by 
Philips Electronics N.V. See www.meethue.com for more information.
"""


import urllib.request
import atexit
import time
import json
import re
import warnings
import logging
try: 
	import phue
except:
	exit('The phue module must be installed. Visit https://github.com/studioimaginaire/phue')

logger = logging.getLogger('huecontroller')
	

class BaseURLMonitor(object):
	
	""" Base Class for URL data monitors.  
	
	Defines the open_url(URL) method, which returns raw data from 
	the given URL. 
	
	"""
	
	def __init__(self, controller):
		"""Constructor.  May be overridden."""		
		self.controller = controller
		self.standby = False
	
	def open_url(self, URL):
		"""Returns raw data from given URL."""
		try:
			with urllib.request.urlopen(URL) as f:
				data = f.read()
			return data
		except Exception as e:
			logger.warning('Received Exception: {}'.format(e))
			return None
		
	def execute(self):
		"""Should be overridden by child class."""
		logger.warning('execute() method has not been overriden!')
		
	def run_forever(self, interval=None):
		"""Run execute() method repeatedly with delay defined by the 
		checkInterval attribute"""
		if interval:
			checkInterval = interval
		else:
			checkInterval = 15
		try:
			logger.info('Running forever. Hit ^C to interrupt.')
			while True:
				tic = time.time()
				self.standby = self.execute()
				toc = time.time()
				if (not self.standby) and (toc - tic) < checkInterval:	
					time.sleep(checkInterval - (toc - tic))
		except KeyboardInterrupt:
			logger.warning('Keyboard interrupt detected, stopping.')

class HueController(object):
	
	"""Main controller object. """
	
	def __init__(self, ip=None, username=None):
		""" Initialization function.
		
		ip : string (dotted quad), optional
		userName : string, optional
		
		Will attempt to find Bridge IP automatically and connect.  Will 
		attempt to use given userName first if present.  If not, will 
		default to "newdeveloper".
		
		Once connected, instruct Bridge to search for new lights using 
		get_new_lights().
		"""
		
		self.IP = ip
		self.userName = username
		self.hue = None
		
		if self.IP:
			logger.info('Using IP: {}'.format(self.IP))
			self.hue = self.connect(self.IP)
			if self.hue is None:
				logger.warning('Given IP failed. Finding IP automatically...')
				self.IP = self.get_bridge_IP()
				logger.info('Found IP: {}'.format(self.IP))
				self.hue = self.connect(self.IP)
		self.IP = self.get_bridge_IP()
		logger.info('Found IP: {}'.format(self.IP))
		self.hue = self.connect(self.IP)
		
		if self.hue:
			pass
			#self.get_new_lights()									#UNCOMMENT WHEN DONE, YOU DUMMY
		else:
			logger.critical('Unable to connect to Bridge.')
			exit('Quitting.')

	def connect(self, IP):
		"""Attempts to connect to Bridge"""
		if not self.userName: 
			self.userName = 'newdeveloper'
		hue = phue.Bridge(ip=IP, username=self.userName)
		try:
			test = hue.get_api()
			logger.info('Found Bridge at {0}'.format(IP))
			if isinstance(test, dict):
				return hue
			elif isinstance(test, list):
				logger.warning(
					'Username unregistered. Attempting to register username "{}"'.format(
						self.userName))
				connected = self.register_user()
				if connected:
					logger.warning('Username "{}" successfully registered.'.format(
						self.userName))
					return hue
				else:
					logger.critical('Unable to register with hue. Attempt manual registration.')
					return None	
		except: 
			return None
	
	def get_bridge_IP(self):
		"""Attempts to automatically find a Hue Bridge on the network.
		
		Hue Bridges automatically upload their IP address daily to a Philips
		database.  Accessing http://www.meethue.com/api/nupnp returns a list 
		of Hue Bridges connected to the network you are connecting from.
		
		"""
		with urllib.request.urlopen('http://www.meethue.com/api/nupnp') as connection:
			data = str(connection.read())
		ipPatternCompiled = re.compile(r'(\d+\.\d+\.\d+\.\d+)')
		match = ipPatternCompiled.search(data)
		if match is None:
			logger.warning('Could not find Bridge IP address automatically')
			exit('Quitting.')
		else: 
			return match.group(1)
			
	def post_user(self):
		"""Sends POST request to Hue Bridge to register a username and program."""
		url = 'http://' + self.IP + '/api' 
		r = json.dumps({'devicetype':'Python Hue Controller', 'username':self.userName}).encode('utf-8')
		req = urllib.request.Request(url, data=r, method='POST')
		with urllib.request.urlopen(req) as connection:
			response = connection.read()	
		return json.loads(str(response, encoding='utf-8'))	

	def register_user(self):
		"""Registers a username with the Philips hue. Will prompt user to push
		the link button on the Bridge if needed."""
		response = self.post_user()
		for line in response:
			for key in line:
				if 'success' in key:
					return True
				if 'error' in key:
					errorType = line['error']['type']
					if errorType == 101:
						logger.warning(
							'Bridge link button has not been pressed.')
						logger.warning(
							'Press the link button and hit enter to continue.')
						input()
						return self.register_user()
					else:
						logger.critical(
							'Error registering username. Error type: {}'.format(
								errorType))
						return False
		
	def get_new_lights(self):
		"""Instructs the Hue Bridge to search for new Hue lights.
	
		The 'find new lights' function appears to be unsupported by the phue 
		module.  This function will instruct the bridge to search for and add
		any new hue lights.  Searching continues for 1 minute and is only 
		capable of locating up to 15 new lights. To add additional lights, 
		the command must be run again.
		"""
		logger.info('Instructing Bridge to search for new lights.')
		url = 'http://' + self.IP + '/api/' + self.userName + '/lights'
		req = urllib.request.Request(url, method='POST')
		with urllib.request.urlopen(req) as connection:
			response = connection.read()
		logger.debug(response)
		connection.close()
		
	def set_state(self, state):
		"""Accepts a state (type: dictionary) and applies it to all Hue lights."""
		logger.debug('Setting lights to {}'.format(state))
		try:
			#response = self.hue.set_group(0, state)
			response = "Response would come here."
			#logger.debug(response)
		except Exception as e:
			logger.error('Received Exception, {}'.format(e))
			logger.error('Unable to connect to Hue Bridge. Check network connection.')
	
