import socket
from time import sleep

class TCPServer:
	def __init__(self,port,ip=''):
		self.DEBUG = True

		self.BUFFER_SIZE = 1
		self.newData = True
		self.data = ''
	
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.bind((ip, port))
		print 'TCPServer> Listening to port: ', port
		print 'TCPServer> Waiting for client...'
		self.s.listen(1)
		(self.con, addr) = self.s.accept()
		print 'TCPServer> client is at', addr
		self.con.setblocking(0)
	
	def close(self):
		self.con.close()

	#returns most recent message in the buffer, purges all others
	def recvmostrecent(self):
		notDone = True
		toReturn = ""
		while(notDone):
			try:
				toReturn = self.con.recv(self.BUFFER_SIZE)
			except:
				notDone = False

		return toReturn

	def recv(self):
		''' Recv one message '''
		try:
			self.data = self.con.recv(self.BUFFER_SIZE)
			if not self.data:
				if self.DEBUG:
					print "TCPServer> Lost connection with client"
				return None
			return self.data
		except:
			return ''

	def send(self,data):
		self.con.send(data)


class TCPClient:
    def __init__(self, host, port):
		self.DEBUG = False
	
		self.BUFFER_SIZE = 32768
		self.newData = False
		self.data = ''
		
		#self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s = socket.create_connection((host, port))
		self.s.setblocking(0)

    def close(self):
		self.s.close()

    def send(self, data):
		self.s.sendall(data)

    def recvmostrecent(self):
		''' Recv most recent message '''
		while (1):

			try:
				self.data = self.s.recv(self.BUFFER_SIZE)
				self.newData = True;
				if not self.data:
					if self.DEBUG:
						print "TCPClient> No data"
					return None
			except:
				if (self.newData):
					self.newData = False
					if self.DEBUG:
						print "TCPClient> data received"
					return self.data
				else:
					return ''
