import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.template

import datetime

import math
import numpy

import socket

from Queue import Queue
from threading import Thread

P1 = numpy.array([11.811, 10.6934, 0])
P2 = numpy.array([6.4262, 0.2159, -0.1016])
P3 = numpy.array([1.8796, 9.2725875, 0.1016])

def trilat(d1, d2 , d3):

	DistA = d1*299702547*(1.0/499.2e6/128.0)
	DistB = d2*299702547*(1.0/499.2e6/128.0)
	DistC = d3*299702547*(1.0/499.2e6/128.0)

	#print DistA, DistB, DistC

	#from wikipedia
	#transform to get circle 1 at origin
	#transform to get circle 2 on x axis
	ex = (P2 - P1)/(numpy.linalg.norm(P2 - P1))
	i = numpy.dot(ex, P3 - P1)
	ey = (P3 - P1 - i*ex)/(numpy.linalg.norm(P3 - P1 - i*ex))
	ez = numpy.cross(ex,ey)
	d = numpy.linalg.norm(P2 - P1)
	j = numpy.dot(ey, P3 - P1)

	#from wikipedia
	#plug and chug using above values
	x = (pow(DistA,2) - pow(DistB,2) + pow(d,2))/(2*d)
	y = ((pow(DistA,2) - pow(DistC,2) + pow(i,2) + pow(j,2))/(2*j)) - ((i/j)*x)

	#print x, y

	z = 0

	# only one case shown here
	try:
		z = numpy.sqrt(pow(DistA,2) - pow(x,2) - pow(y,2))
	except:
		print "BAD", pow(DistA,2) - pow(x,2) - pow(y,2)
		z = numpy.sqrt(abs(pow(DistA,2) - pow(x,2) - pow(y,2)))

	#triPt is an array with ECEF x,y,z of trilateration point
	triPt = P1 + x*ex + y*ey + z*ez

	return triPt

numpy.seterr(all='raise')

class Tag:

	name = None

	p_beef = None
	p_base = None
	p_ball = None

	p_beef_ts = 0
	p_base_ts = 0
	p_ball_ts = 0

	pts = []

def check_stmps(tag):

	if(abs(tag.p_beef_ts-tag.p_base_ts) < 3 and abs(tag.p_beef_ts-tag.p_ball_ts) < 3 and abs(tag.p_ball_ts-tag.p_base_ts) < 3):
		triPt = trilat(tag.p_base, tag.p_beef, tag.p_ball)
		print triPt
		if(not math.isnan(triPt[1]) and not math.isnan(triPt[0])):

			if(triPt[2] < -3.3):
				print "Downstairs"
			else:
				print "Upstairs"

			pt_str = str(triPt[0])+","+str(triPt[1])+","+str(triPt[2])+","+tag.name

			tag.pts.append(pt_str)
			if len(tag.pts) > 10:
				tag.pts.pop(0)

			q.put(pt_str)

def process_line(line, tags):

	print line

	name = line[11:15]
	try:
		tag = tags[name]
	except:
		tag = Tag()
		tag.name = name
		tags[name] = tag

	if line[6:10] == "BEEF":
		tag.p_beef = int(line[16:24], 16)
		tag.p_beef_ts = float(line[25:])
		check_stmps(tag)
	elif line[6:10] == "BA11":
		tag.p_ball = int(line[16:24], 16)
		tag.p_ball_ts = float(line[25:])
		check_stmps(tag)
	elif line[6:10] == "BA5E":
		tag.p_base = int(line[16:24], 16)
		tag.p_base_ts = float(line[25:])
		check_stmps(tag)


q = Queue(maxsize=0)

tags = {}

def recv_samples(q):

	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind(('',50000))

	while True:

		m = s.recvfrom(1024)
		process_line(m[0], tags)

worker = Thread(target=recv_samples, args=(q,))
worker.setDaemon(True)
worker.start()

class MainHandler(tornado.web.RequestHandler):
    def get(self):
	loader = tornado.template.Loader(".")
        self.write(loader.load("index.html").generate())

connections = []

def send_updates():
    try:

	try:
		pt = q.get(False)
		print "Sending:", pt

	        for client in clients:
			client.write_message(str(pt))

	except:
		pass
		#print "no new samples"

    finally:
        tornado.ioloop.IOLoop.instance().add_timeout(timedelta(seconds=2),
                                                     send_message_to_clients)

class WSHandler(tornado.websocket.WebSocketHandler):

	def check_origin(self, origin):
		return True

	def open(self):

		print 'Connection opened.'
		for tag in tags:
			for pt in tags[tag].pts:
				print "Sending:", pt
				self.write_message(str(pt))

		connections.append(self)

	def on_message(self, message):
		print 'Message received: \'%s\'' % message

	def on_close(self):
		print 'Connection closed.'
		connections.remove(self)

application = tornado.web.Application([
    (r'/ws', WSHandler),
    (r"/", MainHandler),
    (r"/(.*)", tornado.web.StaticFileHandler, {"path": "./resources"}),
])

def schedule_func():
	self.write_message("Test")

if __name__ == "__main__":

	application.listen(9090)
	tornado.ioloop.IOLoop.instance().start()
	tornado.ioloop.IOLoop.instance().add_timeout(datetime.timedelta(seconds=2), send_updates)

