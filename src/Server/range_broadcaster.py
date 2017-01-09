import socket
import serial

ser = serial.Serial(
	port='/dev/ttyUSB0',
	baudrate=115200
)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

while 1:

	data = ser.readline().strip();

	print data
	if data[0:5] == "RANGE":
		print "SENDING!"
		s.sendto(data, ('<broadcast>', 50000))


