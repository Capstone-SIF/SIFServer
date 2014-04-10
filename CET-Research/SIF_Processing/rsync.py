from subprocess import call
import os
from sys import argv
import logging

common = ['CapstoneDatabase.db',
			 'DBManager.py',
			 'EXIF.py',
			 'config.py',
			 'rsync.py',
			 'outputFiles']


# baseCmd = "rsync -r -t -p -v -z --progress --delete"
baseCmd = "rsync -r -C -t -p -a -z -v --progress --delete"
cet_research_root = 'sif@cet-research.colorado.edu:~/SIF_Processing'

class rsync:
	def __init__(self, debug=False):
		self.debug  = debug
		if self.debug:
			logLevel = logging.DEBUG
		else:
			logLevel = logging.INFO
		logging.basicConfig(format='%(levelname)s: %(message)s', level=logLevel)

	def syncServerCode(self):
		source = os.path.abspath( 'sockets' )
		dest   = 'sif@cet-sif.colorado.edu:~/SIF_Server/'

		cmd = baseCmd
		cmd = cmd.split(' ')
		cmd.append( source )
		cmd.append( dest )

		print '----------------------------'
		print '>> %s\n' % ' '.join( cmd )
		call( cmd )

		self.syncCommonToSIF()

	def syncProcessingCode(self):
		source = os.path.abspath( 'Matlab' )
		dest   = cet_research_root

		cmd = baseCmd
		cmd = cmd.split(' ')
		cmd.append( source )
		cmd.append( dest )

		print '----------------------------'
		print '>> %s\n' % ' '.join( cmd )
		call( cmd )

		source = os.path.abspath( 'Forecast' )

		cmd = baseCmd
		cmd = cmd.split(' ')
		cmd.append( source )
		cmd.append( dest )

		print '----------------------------'
		print '>> %s\n' % ' '.join( cmd )
		call( cmd )

		self.syncCommonToResearch()

	def syncCommonToSIF(self):
		dest = 'sif@cet-sif.colorado.edu:~/SIF_Server/'
		for c in common:
			source = os.path.abspath(c)
			cmd = baseCmd
			cmd = cmd.split(' ')
			cmd.append( source )
			cmd.append( dest )

			print '----------------------------'
			print '>> %s\n' % ' '.join( cmd )
			call( cmd )

	def syncCommonToResearch(self):
		dest = '%s/' % cet_research_root
		for c in common:
			source = os.path.abspath(c)
			cmd = baseCmd
			cmd = cmd.split(' ')
			cmd.append( source )
			cmd.append( dest )


			print '----------------------------'
			print '>> %s\n' % ' '.join( cmd )
			call( cmd )

	def sendToCETResearch(self, groupDir, verbose=False ):
		dest = '%s/outputFiles/Unprocessed/%s/' % (cet_research_root, os.path.basename( groupDir ) )

		cmd = baseCmd
		cmd = cmd.split(' ')
		cmd.append( '%s/' % groupDir )
		cmd.append( dest )

		if verbose:
			print '----------------------------'
			print '>> %s\n' % ' '.join( cmd )
		call( cmd )

		dest = cet_research_root

		cmd = baseCmd
		cmd = cmd.split(' ')
		cmd.append( 'CapstoneDatabase.db' )
		cmd.append( dest )

		if verbose:
			print '----------------------------'
			print '>> %s\n' % ' '.join( cmd )
		call( cmd )

		print '%s synced to cet-research' % os.path.basename( groupDir )

if __name__ == '__main__':
	possibleArgs = ['cet-research', 'cet-sif', 'commonSIF', 'commonResearch']
	if len(argv) < 2:
		print 'Requires one of these arguments to run: %s' % possibleArgs
		exit(1)
	if argv[1] not in possibleArgs:
		print 'Requires one of these arguments to run: %s' % possibleArgs
		exit(1)
	rsync = rsync()
	if argv[1] == 'cet-research':
		rsync.syncProcessingCode()
	elif argv[1] == 'cet-sif':
		rsync.syncServerCode()
	elif argv[1] == 'commonSIF':
		rsync.syncCommonToSIF()
	elif argv[1] == 'commonResearch':
		rsync.syncCommonToResearch()


'''
Rsync Options:

	 -v, --verbose               increase verbosity
	 -q, --quiet                 suppress non-error messages
	     --no-motd               suppress daemon-mode MOTD (see manpage caveat)
	 -c, --checksum              skip based on checksum, not mod-time & size
	 -a, --archive               archive mode; same as -rlptgoD (no -H)
	     --no-OPTION             turn off an implied OPTION (e.g. --no-D)
	 -r, --recursive             recurse into directories
	 -R, --relative              use relative path names
	     --no-implied-dirs       don't send implied dirs with --relative
	 -b, --backup                make backups (see --suffix & --backup-dir)
	     --backup-dir=DIR        make backups into hierarchy based in DIR
	     --suffix=SUFFIX         set backup suffix (default ~ w/o --backup-dir)
	 -u, --update                skip files that are newer on the receiver
	     --inplace               update destination files in-place (SEE MAN PAGE)
	     --append                append data onto shorter files
	 -d, --dirs                  transfer directories without recursing
	 -l, --links                 copy symlinks as symlinks
	 -L, --copy-links            transform symlink into referent file/dir
	     --copy-unsafe-links     only "unsafe" symlinks are transformed
	     --safe-links            ignore symlinks that point outside the source tree
	 -k, --copy-dirlinks         transform symlink to a dir into referent dir
	 -K, --keep-dirlinks         treat symlinked dir on receiver as dir
	 -H, --hard-links            preserve hard links
	 -p, --perms                 preserve permissions
	     --executability         preserve the file's executability
	     --chmod=CHMOD           affect file and/or directory permissions
	 -o, --owner                 preserve owner (super-user only)
	 -g, --group                 preserve group
	     --devices               preserve device files (super-user only)
	     --specials              preserve special files
	 -D                          same as --devices --specials
	 -t, --times                 preserve times
	 -O, --omit-dir-times        omit directories when preserving times
	     --super                 receiver attempts super-user activities
	 -S, --sparse                handle sparse files efficiently
	 -n, --dry-run               show what would have been transferred
	 -W, --whole-file            copy files whole (without rsync algorithm)
	 -x, --one-file-system       don't cross filesystem boundaries
	 -B, --block-size=SIZE       force a fixed checksum block-size
	 -e, --rsh=COMMAND           specify the remote shell to use
	     --rsync-path=PROGRAM    specify the rsync to run on the remote machine
	     --existing              skip creating new files on receiver
	     --ignore-existing       skip updating files that already exist on receiver
	     --remove-source-files   sender removes synchronized files (non-dirs)
	     --del                   an alias for --delete-during
	     --delete                delete extraneous files from destination dirs
	     --delete-before         receiver deletes before transfer (default)
	     --delete-during         receiver deletes during transfer, not before
	     --delete-after          receiver deletes after transfer, not before
	     --delete-excluded       also delete excluded files from destination dirs
	     --ignore-errors         delete even if there are I/O errors
	     --force                 force deletion of directories even if not empty
	     --max-delete=NUM        don't delete more than NUM files
	     --max-size=SIZE         don't transfer any file larger than SIZE
	     --min-size=SIZE         don't transfer any file smaller than SIZE
	     --partial               keep partially transferred files
	     --partial-dir=DIR       put a partially transferred file into DIR
	     --delay-updates         put all updated files into place at transfer's end
	 -m, --prune-empty-dirs      prune empty directory chains from the file-list
	     --numeric-ids           don't map uid/gid values by user/group name
	     --timeout=TIME          set I/O timeout in seconds
	 -I, --ignore-times          don't skip files that match in size and mod-time
	     --size-only             skip files that match in size
	     --modify-window=NUM     compare mod-times with reduced accuracy
	 -T, --temp-dir=DIR          create temporary files in directory DIR
	 -y, --fuzzy                 find similar file for basis if no dest file
	     --compare-dest=DIR      also compare destination files relative to DIR
	     --copy-dest=DIR         ... and include copies of unchanged files
	     --link-dest=DIR         hardlink to files in DIR when unchanged
	 -z, --compress              compress file data during the transfer
	     --compress-level=NUM    explicitly set compression level
	 -C, --cvs-exclude           auto-ignore files the same way CVS does
	 -f, --filter=RULE           add a file-filtering RULE
	 -F                          same as --filter='dir-merge /.rsync-filter'
	                             repeated: --filter='- .rsync-filter'
	     --exclude=PATTERN       exclude files matching PATTERN
	     --exclude-from=FILE     read exclude patterns from FILE
	     --include=PATTERN       don't exclude files matching PATTERN
	     --include-from=FILE     read include patterns from FILE
	     --files-from=FILE       read list of source-file names from FILE
	 -0, --from0                 all *-from/filter files are delimited by 0s
	     --address=ADDRESS       bind address for outgoing socket to daemon
	     --port=PORT             specify double-colon alternate port number
	     --sockopts=OPTIONS      specify custom TCP options
	     --blocking-io           use blocking I/O for the remote shell
	     --stats                 give some file-transfer stats
	 -8, --8-bit-output          leave high-bit chars unescaped in output
	 -h, --human-readable        output numbers in a human-readable format
	     --progress              show progress during transfer
	 -P                          same as --partial --progress
	 -i, --itemize-changes       output a change-summary for all updates
	     --out-format=FORMAT     output updates using the specified FORMAT
	     --log-file=FILE         log what we're doing to the specified FILE
	     --log-file-format=FMT   log updates using the specified FMT
	     --password-file=FILE    read password from FILE
	     --list-only             list the files instead of copying them
	     --bwlimit=KBPS          limit I/O bandwidth; KBytes per second
	     --write-batch=FILE      write a batched update to FILE
	     --only-write-batch=FILE like --write-batch but w/o updating destination
	     --read-batch=FILE       read a batched update from FILE
	     --protocol=NUM          force an older protocol version to be used
	 -E, --extended-attributes   copy extended attributes
	     --cache                 disable fcntl(F_NOCACHE)
	 -4, --ipv4                  prefer IPv4
	 -6, --ipv6                  prefer IPv6
	     --version               print version number
	(-h) --help                  show this help (-h works with no other options)
'''