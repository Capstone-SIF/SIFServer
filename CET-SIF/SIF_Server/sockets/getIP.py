import socket

HOST = socket.gethostbyname(socket.gethostname())
print HOST


import sys
sys.path.append( '..' )
from config import config
print config['rootPath']
