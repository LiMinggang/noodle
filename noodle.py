#!/usr/bin/env python3
'''
TODO:
	global send buff
	burst
	raw packet
	time to run
	time to run per session
	epoll?
	adaptive send over second
	mixed sessions
'''

import argparse
import sys
import threading
import time
import random
import string
import socket
import struct
import errno

class Config:

	def __init__(self):
		self.parser = argparse.ArgumentParser(description='Noodle - Fire some ip based connections')
		s = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(1024)])
		self.gBuff = s.encode()
		self.socket_mode = socket.SOCK_STREAM

	def parse_args(self, args=None):
		self.parser.add_argument('-s', help='server mode', action='store_true')
		self.parser.add_argument('-u', help='udp mode - default(tcp)', action='store_true')
		self.parser.add_argument('-c', help='client mode: server host address')
		self.parser.add_argument('-p', help='port', type=int, default=10005)
		self.parser.add_argument('-P', help='local port bind start - default(random)', type=int)
		self.parser.add_argument('-A', help='local address to bind - default(ANY)')
		self.parser.add_argument('-C', help='Num concurrent connections - default(100)', type=int, default=100)
		self.parser.add_argument('-n', help='Ramp up connections per second - default(100)', type=int, default=100)
		self.parser.add_argument('-r', help='Num threads to use - default(1)', type=int, default=1)
		self.parser.add_argument('-b', help='Banwidth per connection in kmgKMG - default(1m)', default='1m')
		self.parser.add_argument('-B', help='Total Banwidth in kmgKMG bits. no default. Overrides -b')
		self.parser.add_argument('-l', help='length of buffer in bytes to read or write - default(auto)', type=int)

		self.args = self.parser.parse_args(args)

		if self.args.u:
				self.socket_mode = socket.SOCK_DGRAM

		# bandwidth calcs - store result in c.args.b
		if self.args.B[-1] not in "kmgKMG":
			print("Error in BW")
		if self.args.B:
			mes = lambda x: (x=='k' and '1000') or (x=='K' and 1000) or (x=='m' and 1000000) or (x=='M' and 1000000) or (x=='g' and 1000000000) or (x=='G' and 1000000000) or 1
			t = int(mes(self.args.B[-1]))
			nbw = int(c.args.B[0:-1])*t
			print("DEBUG:", nbw)
			self.args.b = nbw/self.args.C
		else:
			bw = self.args.b

		# each thread shoud create ramp/r conns per second
		self.args.n = min(self.args.C, self.args.n)
		self.args.n = max(int(self.args.n/self.args.r), 1)

		print("real BW:", t*nbw, "Per conn:", nbw/self.args.C, "conns per thread ramp=",self.args.n)
		return

class Connection():
	def __init__(self, socket_mode, gBuff, bit_rate, daddr, dport, saddr=0, sport=0):
		self.saddr = saddr
		self.sport = sport
		self.daddr = daddr
		self.dport = dport
		self.sent_this_second = 0
		self.send_per_second = int(bit_rate/8)
		self.is_active = False
		self.buf = gBuff
		self.socket_mode = socket_mode

	def zero_round_counters(self):
		print("D:", self.send_per_second, self.sent_this_second)
		self.sent_this_second = 0

	def connect(self):
		self.socket = socket.socket(socket.AF_INET, self.socket_mode)
		self.socket.setblocking(0)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 0))
		try:
			self.socket.connect((self.daddr, self.dport))
		except BlockingIOError:
			pass
		time.sleep(0.1)

		self.is_active = True

	def send(self):
		if self.sent_this_second < self.send_per_second:
				try: 
					self.sent_this_second += self.socket.send(self.buf)
					#print("sent:", self.sent_this_second)
				except socket.error as e:
					if self.socket_mode == socket.SOCK_DGRAM:
							return
					if e.errno != errno.EAGAIN:
						raise e



class ConnectionManager(object):
# Manage Total/threads sessions within a thread.
	def __init__(self, idx, config):
		print("Config:", config.args.s, " id:", idx)
		self.id = idx
		self.config = config
		self.num_conns = int(config.args.C/config.args.r)
		self.conns = []
		print("run id=", self.id, threading.get_ident(), "BW=", " Thread num_conns=", self.num_conns)
		for i in range(self.num_conns):
			self.conns.append(Connection(config.socket_mode, config.gBuff, self.config.args.b, self.config.args.c, self.config.args.p))

		self.should_run = True

		thread = threading.Thread(target=self.run)
		#thread.daemon = True                            # Daemonize thread
		thread.start()
	def second_over(self):
		self.second_not_over = False
	
	def run(self):
		
		while self.should_run:
			#print("Zeroing")
			self.second_not_over = True
			t = threading.Timer(1.0, self.second_over)
			t.start()
			for conn in self.conns:
				conn.zero_round_counters()
			conns_left_to_create = self.config.args.n
			# zero conns counters
			while self.second_not_over:
				for conn in self.conns:
						if conn.is_active:
								conn.send()
						elif conns_left_to_create:
								conn.connect()
								--conns_left_to_create
				#send something on all conns if needed
				#open sessions according to ramp plan if needed
					



if __name__ == '__main__':
	c = Config()    
	c.parse_args(sys.argv[1:])
	print(c.args.s)



	
	loaders = []
	for i in range(c.args.r):
		loaders.append(ConnectionManager(i, c))



