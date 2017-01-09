# Server Code: DWM1000 Cat Tracker

The Trilateration server takes 3 points [P1,P2,P3] which correspond to the positions of the ancors relative to the origion of the map.
There are 3 tag objects whos addresses need to bet set.  This code uses tornado to create a websocket server that the index.html interface connects to to display packets.

The index.html contains a map of lines to represent the different enviorments an object is being tracked from the Ancors positions in space are stored in 3 points.  The javascript connects back to the python server websocket to get information on the tags locations and plots them to the map as they come in in real time.

forward_trilat.py is a simple script for forwarding broadcast UDP packets with Range data on your network to a remote UDP Python server.

range_broadcaster.py connects to the Master Anchor via serial port and broadcast the range data it dumps.

The basic flow is: ATMasterAncor > SERIAL > Computer > range_broadcaster.py > UDP BROADCAST > forward_trilat.py > UDP SOCKET > trilate_server > WEB_SOCKET > index.html

