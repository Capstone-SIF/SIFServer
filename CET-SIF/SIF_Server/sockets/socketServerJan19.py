# Echo server program
import socket
import datetime
import sys
import os
import time
import eventlet
from math import floor
import logging

sys.path.append('.')
sys.path.append('..')
from DBManager import DB # Capstone database manager
from rsync import rsync

class sockServer:

	PORT              = 5000  # Arbitrary non-privileged port
	MESSAGE_SIGNATURE = 'cachemoney'

	BUFF_SIZE     = 512
	MIN_PIC_LINES = 50

	OUTPUT_DIR      = 'outputFiles'
	UNPROCESSED_DIR = os.path.join( OUTPUT_DIR, 'Unprocessed' )
	PROCESSED_DIR   = os.path.join( OUTPUT_DIR, 'Processed' )
	PROCESSING_DIR  = os.path.join( OUTPUT_DIR, 'Processing' )
	OUTPUT_EXT      = 'jpg'

	numReceived = 0

	def __init__(self, debug=False):
		self.debug  = debug
		if self.debug:
			logLevel = logging.DEBUG
		else:
			logLevel = logging.INFO
		logging.basicConfig(format='%(levelname)s: %(message)s', level=logLevel)

		if not os.path.isdir(self.OUTPUT_DIR):
		 	os.mkdir(self.OUTPUT_DIR)
		if not os.path.isdir(self.UNPROCESSED_DIR):
		 	os.mkdir(self.UNPROCESSED_DIR)
		if not os.path.isdir(self.PROCESSED_DIR):
		 	os.mkdir(self.PROCESSED_DIR)
		if not os.path.isdir(self.PROCESSING_DIR):
		 	os.mkdir(self.PROCESSING_DIR)
		self.db = DB(debug = self.debug)
		self.rsync = rsync( self.debug )

		if socket.gethostname() == 'cet-sif':
			self.OnServer = True
			# self.host = socket.gethostbyname( 'cet-research.colorado.edu' )
			self.host = '128.138.248.205'
		else:
			self.OnServer = False
			self.host = socket.gethostbyname(socket.gethostname())
		# self.host = socket.gethostbyname(socket.gethostname())

	def runNonBlockingSocket(self):
		listener = eventlet.listen( (self.host, self.PORT)  )
		print 'Recieving on %s, %s'%(self.host, self.PORT)
		eventlet.serve(listener, self.recieveData)

	def recieveData(self, client_sock, client_addr):
		'''Callback function for every time a client connects to the nonblocking socket'''

		print "client connected", client_addr
		first = True
		lines = []
		while 1:
			line = client_sock.recv( self.BUFF_SIZE )
			if first:
				tic = time.time()
				first = False
			if not line:
				break
			lines.append(line)

		if len(lines) == 0:
			logging.info('No message provided. Ignoring client.')
			return
		# Check signature and get image file name
		if len(lines[0].split('\n')) < 2:
			logging.info('Incoming message is not the required format. Ignoring client.')
			return # ignore this message
		signature, imageName = tuple( lines[0].split('\n')[0:2] )
		if self.MESSAGE_SIGNATURE != signature:
			logging.info('Illegal message recieved with signature:\n%s' % lines[0])
			return # ignore this message
		lines[0] = ''.join( lines[0].split('%s\n' % imageName)[1:] )
		cameraID, timeTaken, lat, lon, powerData = tuple( imageName.split('_') )
		groupID = self.numReceived%2
		self.numReceived += 1

		if len(lines) > self.MIN_PIC_LINES:
			lat = float( lat.replace(',','.') )
			lon = float( lon.replace(',','.') )
			timeTaken = time.strptime( timeTaken, '%H%M%S')
			groupID = self.timeToGroupID( timeTaken )
			self.db.setCameraGeoTag(cameraID, lat, lon)

			imPath = self.saveImg(lines, groupID, cameraID)
			if self.OnServer:
				self.rsync.sendPhotoToCETResearch( os.path.dirname(imPath), verbose=False )
			logging.debug('Image added to queue')
		else:
			self.db.writePowerData( lines[0], 'TEST_GEOTAG', datetime.datetime.now() )
			logging.debug('Power data written to database')
			self.db.syncPowerWithCETResearch(verbose=False)
			logging.debug( 'Total time taken = %f' % (time.time()-tic) )

	def groupIDtoDatetime( self, groupID ):
		today    = datetime.date.today()
		midnight = datetime.datetime(year=today.year, month=today.month, day=today.day,
								  hour=0, minute=0, second=0)
		thirtySec = datetime.timedelta(seconds=30)
		return midnight + (groupID * thirtySec)

	def timeToGroupID( self, t ):
		return int( 120 * t.tm_hour + 2 * t.tm_min + floor(t.tm_sec/30) )

	def saveImg(self, dataLines, groupID, sensorID):
		idealDateTimeTaken = self.groupIDtoDatetime( groupID )
		timeStr = idealDateTimeTaken.strftime("%h%d_%Y-%H_%M_%S")
		now = datetime.datetime.now()
		nowStr = now.strftime("%h%d_%Y %H_%M_%S")

		outputFileDir = os.path.join( self.UNPROCESSED_DIR,
												'%i-%s' % (groupID, timeStr) )
		if os.path.isdir(outputFileDir) is False:
			os.mkdir( outputFileDir )
		outputFilePath = os.path.join( outputFileDir,
												 '%i_%s_%s.%s' % (groupID, sensorID,timeStr,self.OUTPUT_EXT) )
		f = open(outputFilePath, 'w')
		for line in dataLines:
			f.write( line )
		f.close()

		logging.info('%s written successfully' % outputFilePath)

		return outputFilePath

	'''
	==============================================================================
	=============================== OLD CODE BELOW ===============================
	==============================================================================
	'''

	def runSocket(self,customHostPort=None):
		if customHostPort:
			host, port = customHostPort
		else:
			host, port = self.host, self.PORT
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind((host, port))
		self.sock.listen(1)
		self.conn, self.addr = self.sock.accept()

		logging.debug( 'Connected by %s' % (self.addr,) )

	def recieveOne(self):
		self.runSocket()
		lines = []
		first = True
		while 1:
			line = self.conn.recv( self.BUFF_SIZE )
			if first:
				tic = time.time()
				first = False
			lines.append( line )
			if not line:
				break
		self.saveImg(lines)
		print 'Total time taken = %f' % (time.time()-tic)
		self.conn.close()
		exit()

	def reciveFileName(self):
	   filename = self.conn.recv( self.BUFF_SIZE )
	   return filename


	def recieveArray(self):
		self.runSocket()
		line = self.conn.recv( self.BUFF_SIZE )
		logging.debug(line)
		self.conn.close()
		exit()

	def keepRecievingStrs(self):
		lines = []
		while 1:
			self.runSocket()
			try:
				while 1:
					line = self.conn.recv( self.BUFF_SIZE )
					if not line:
						break
					lines.append(line)
			except socket.error, e:
				print e
			if len(lines) == 1:
				logging.debug(lines[0])
			else:
				logging.debug('%d lines received' % len(lines))
				# print lines[:50]
			self.conn.close()
			self.runSocket()

if __name__ == '__main__':
	debug = False
	if 'debug' in sys.argv:
		debug = True
	print 'DEBUG MODE = %s' % debug
	server = sockServer(debug=debug)
	# server.keepRecievingStrs()
	# server.recieveArray()
	# server.recieveOne()
	# server.recieveMany()
	# server.keepRecieving()
	server.runNonBlockingSocket()
	# p = os.path.join( 'outputFiles', 'test.jpg' )
	# np = os.path.join( 'outputFiles', 'test_reduced.jpg' )
	# server.reduceImSize(p, np)

