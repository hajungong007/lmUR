#!/usr/bin/env python

import rospy
import sys, threading
import select
import termios, fcntl, sys, os
from keyboard.msg import KeyboardFrame
from geometry_msgs.msg import Point, Vector3

msg = KeyboardFrame()
msg.hand_available = False
msg.palm_position = Point()
msg.ypr = Vector3()

tool = False

def keypress():
	global publisher
	fd = sys.stdin.fileno()
	
	oldterm = termios.tcgetattr(fd)
	newattr = termios.tcgetattr(fd)
	newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
	termios.tcsetattr(fd, termios.TCSANOW, newattr)

	oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
	fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

	try:
		while 1:
			try:
				c = sys.stdin.read(1)
				talker(c)
			except IOError:
				msg.palm_position.y = 0.0
				msg.palm_position.x = 0.0
				msg.palm_position.z = 0.0
				msg.ypr.x = 0
				msg.ypr.y = 0
				msg.ypr.z = 0
				publisher.publish(msg)
	except KeyboardInterrupt:
		rospy.signal_shutdown("KeyboardInterrupt")
	finally:
		termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
		fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)

def talker(inp):
	global msg,action, publisher, tool
	
	
	msg.hand_available = True
 
	if(inp == "t"):
		tool = True
	elif(inp == "r"):
		tool = False
	elif(inp == "w"):
		if tool:
			msg.ypr.y = 90
		else:
			msg.palm_position.y = 250
	elif(inp == "a"):
		if tool:
			msg.ypr.x = -90
		else:
			msg.palm_position.x = -90
	elif(inp == "s"):
		if tool:
			msg.ypr.y = -90
		else:
			msg.palm_position.y = 50
	elif(inp == "d"):
		if tool:
			msg.ypr.x = 90
		else:
			msg.palm_position.x = 90
	elif(inp == "q"):
		if tool:
			msg.ypr.z = -90
		else:
			msg.palm_position.z = -80
	elif(inp == "e"):
		if tool:
			msg.ypr.z = 90
		else:
			msg.palm_position.z = 80
	
	rospy.loginfo(msg)
	publisher.publish(msg)

if __name__ == '__main__':
	try:
		rospy.init_node('KeyboardPublisher', anonymous=True)
		publisher = rospy.Publisher('keyboard/data', KeyboardFrame, queue_size=10)
		keypress()
	except KeyboardInterrupt:
		rospy.signal_shutdown("KeyboardInterrupt")
	except rospy.ROSInterruptException:
		pass
