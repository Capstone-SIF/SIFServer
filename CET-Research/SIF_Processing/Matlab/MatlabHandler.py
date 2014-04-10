import sys
import os
sys.path.append( os.path.abspath('.') )
sys.path.append( os.path.abspath('./Matlab') )
sys.path.append( os.path.abspath('./Forecast') )
import datetime
import shutil
import logging
import pexpect # http://www.noah.org/wiki/Pexpect

sys.path.append('outputFiles')
from DBManager import DB
from makeKML import kmlMaker

class matlab:
	def __init__(self, debug=False):
		self.debug = debug
		if os.getlogin() is not 'timfurlong':
			mlabCmd = 'matlab -nodesktop -noFigureWindows' #  -nodisplay
		else:
			mlabCmd = 'matlab -maci -nodesktop -noFigureWindows' #'-nojvm' -nodisplay
		print '$ %s' % mlabCmd
		self.child = pexpect.spawn( mlabCmd )
		print '\nstarting MATLAB...'
		self.child.expect('>> ')
		print 'MATLAB started successfully\n'

	def __del__(self):
		self.quit()

	def call(self, cmd):
		try:
			self.child.sendline( cmd )
		except pexpect.EOF:
			print 'MATLAB process has not been spawned!'

		self.child.expect('>> ')
		if self.debug:
			print '>> %s' % self.child.before
		# respCode = self.child.expect(['>> ', '??? Error using ==>'])
		# if respCode == 0:
		# 	# command ran successfully
		# 	if self.debug:
		# 		print '>> %s' % self.child.before
		# else:
		# 	# MATLAB command failed. Print the error and move on...
		# 	print '>> %s' % self.child.before


	def quit(self):
		print 'quiting MATLAB'
		self.child.kill(0)
		# self.child.sendline( 'exit;' )

class MatlabHandler:

	MIN_WAIT_TIME     = 5 # Seconds
	MIN_NUM_PHOTOS    = 1
	PUBLIC_DIR	  = os.path.join('/data/home/sif','public_html/Forecast')
	PUBLICIMAGES_DIR  = os.path.join(PUBLIC_DIR, 'ForecastOutput')
	OUTPUT_DIR        = os.path.abspath( 'outputFiles' )
	UNPROCESSED_DIR   = os.path.join( OUTPUT_DIR, 'Unprocessed' )
	PROCESSED_DIR     = os.path.join( OUTPUT_DIR, 'Processed' )
	PROCESSING_DIR    = os.path.join( OUTPUT_DIR, 'Processing' )
	PREVIOUS_DIR	  = 'None'
	MATLAB_SOURCE_DIR = os.path.abspath( 'Matlab' )

	def __init__(self, debug=False):
		self.debug  = debug
		self.db     = DB(self.debug)
		self.kml    = kmlMaker(self.debug)
		self.mlab   = matlab(self.debug)

		if self.debug:
			logLevel = logging.DEBUG
		else:
			logLevel = logging.INFO
		logging.basicConfig(format='%(levelname)s: %(message)s', level=logLevel)

		if not os.path.isdir(self.PUBLIC_DIR):
			os.mkdir(self.PUBLIC_DIR)
	      	if not os.path.isdir(self.PUBLICIMAGES_DIR):
			os.mkdir(self.PUBLICIMAGES_DIR)
		if not os.path.isdir(self.OUTPUT_DIR):
			os.mkdir(self.OUTPUT_DIR)
		if not os.path.isdir(self.PROCESSING_DIR):
			os.mkdir(self.PROCESSING_DIR)
		if not os.path.isdir(self.UNPROCESSED_DIR):
		 	os.mkdir(self.UNPROCESSED_DIR)
		if not os.path.isdir(self.PROCESSED_DIR):
			os.mkdir(self.PROCESSED_DIR)

		self.modTimes = {}

	def keepCheckingQueue(self):
		while 1:
			logging.info('Waiting for unprocessed queue items...')
			while 1:
				now = datetime.datetime.now()
				unproc = self.getUnprocessedQueueItems()
				for queueEntry in unproc:
					if queueEntry['baseName'] not in self.modTimes:
						self.modTimes[queueEntry['baseName']] = datetime.datetime.now()
					if queueEntry['num_images'] < self.MIN_NUM_PHOTOS:
						continue
					timeDiff = now - self.modTimes[queueEntry['baseName']]
					if timeDiff.seconds > self.MIN_WAIT_TIME:
						self.callMotion(queueEntry)
						break

	def callMotion(self, queueEntry):

			currentLoc = os.path.abspath( queueEntry['groupDir'] )
			groupDirBase = os.path.split( queueEntry['groupDir'] )[1]
			newLoc = os.path.join( self.PROCESSING_DIR, groupDirBase, 'Input' )
			shutil.move(currentLoc, newLoc)
			try:
				shutil.rmtree(currentLoc)
			except:
				pass
			currentLoc = newLoc
			queueEntry['groupDir'] = currentLoc

			foutFileDir = os.path.join(self.PROCESSED_DIR, groupDirBase, 'ForecastOutput/' )
			voutFileDir = os.path.join(self.PROCESSED_DIR, groupDirBase, 'VectorOutput/' )
			if not os.path.isdir( os.path.join(self.PROCESSED_DIR, groupDirBase) ):
				os.mkdir( os.path.join(self.PROCESSED_DIR, groupDirBase) )
			if not os.path.isdir( foutFileDir ):
				os.mkdir( foutFileDir )
			if not os.path.isdir( voutFileDir ):
				os.mkdir( voutFileDir )
			# outFile    = os.path.join( outFileDir, '%s.jpg' % timeProcessed )
			matlabCmds = [ 'cd %s;' % self.MATLAB_SOURCE_DIR,
								'startup;',
								'set_forecasts(\'%s\',\'%s\',1024);' % (currentLoc, foutFileDir),
								'get_motion_vectors(\'%s\',\'%s\',\'%s\');' % (self.PREVIOUS_DIR, currentLoc, voutFileDir),
								]
			
			
			
			
			for cmd in matlabCmds:
				self.mlab.call(cmd)
			shutil.rmtree(self.PUBLICIMAGES_DIR)
			shutil.copytree(foutFileDir, self.PUBLICIMAGES_DIR)			

			self.kml.createKML(voutFileDir, foutFileDir,self.PUBLIC_DIR)

			newLoc = os.path.join(self.PROCESSED_DIR, groupDirBase)
			oldLoc = os.path.join(self.PROCESSING_DIR, groupDirBase)
			shutil.move(currentLoc, newLoc)

			self.PREVIOUS_DIR = os.path.join(newLoc, 'Input')

			try:
				shutil.rmtree(oldLoc)
			except:
				pass
			currentLoc = newLoc
			logging.info( 'Finished Processing Group: %s' % queueEntry['groupID'] )

	def getUnprocessedQueueItems(self):
		queueTasks = []
		for Dir in os.listdir( self.UNPROCESSED_DIR ):
			groupDir = os.path.join(self.UNPROCESSED_DIR, Dir)
			if Dir.startswith( '.' ) or os.path.isfile(groupDir):
				continue # ignore hidden folders and all files
			groupID        = int( Dir[0] )
			idealTimeTaken = Dir[2:]
			mtime          = os.path.getmtime( groupDir )
			lastUpdated    = datetime.datetime.fromtimestamp( mtime )

			files = [ f for f in os.listdir( groupDir ) if os.path.isfile( os.path.join(groupDir,f) ) ]
			images = [ f for f in files if f.endswith('.jpg') ]

			task = {
				'groupID': groupID,
				'baseName': os.path.basename(groupDir),
				'groupDir': os.path.join(self.UNPROCESSED_DIR, Dir),
				'idealTimeTaken': idealTimeTaken,
				'lastUpdated': lastUpdated,
				'images': images,
				'num_images': len(images)
			}

			queueTasks.append( task )
		return queueTasks

	def moveImg(self, im, newLocation):
		# Move all files to Processing dir
		newLocation = os.path.join(self.PROCESSING_DIR, os.path.basename(im) )
		shutil.move(im, newLocation)
		return newLocation

if __name__ == '__main__':
	debug = False
	if 'debug' in sys.argv:
		debug=True
	debug = True
	print 'DEBUG MODE = %s' % debug
	matHandle = MatlabHandler(debug=debug)
	# mlab = matlab()
	matHandle.keepCheckingQueue()


