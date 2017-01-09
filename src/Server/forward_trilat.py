import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('',50000))

while True:

	m = s.recvfrom(1024)
	print "Forwarding: ", m[0]
	s.sendto(m[0], ("dryerzinia.io", 50000))

