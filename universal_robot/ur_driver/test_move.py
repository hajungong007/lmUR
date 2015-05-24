#!/usr/bin/env python
import time
import roslib; roslib.load_manifest('ur_driver')
import rospy
import actionlib
import threading
import pygame
import sys
import os
sys.path.insert(0, '/home/ubuntu/catkin_ws/src/keyboard/scripts/')
import keyboard_talker
sys.path.insert(0, '/home/ubuntu/catkin_ws/src/joystick/scripts/')
import joystick_talker
sys.path.insert(0, '/home/ubuntu/catkin_ws/src/leap_motion/scripts/')
import leap_talker
sys.path.insert(0, '/home/ubuntu/catkin_ws/src/GUI/')
import display


from pygame.locals import *
from control_msgs.msg import *
from trajectory_msgs.msg import *
from sensor_msgs.msg import JointState
from ur_msgs.msg import *
from leap_motion.msg import LeapFrame
from joystick.msg import JoystickFrame
from keyboard.msg import KeyboardFrame
from ur_driver.io_interface import *


JOINT_NAMES = ['shoulder_pan_joint', 'shoulder_lift_joint', 'elbow_joint',
		   'wrist_1_joint', 'wrist_2_joint', 'wrist_3_joint']

PI = 3.14159265359
d1 = 0.017453293 #1 degree in rad

#Robot joints position
J1 = 0
J2 = 0
J3 = 0
J4 = 0
J5 = 0
J6 = 0

#Hand palm position and status
palmX = 0
palmY = 0
palmZ = 0
palmYaw = 0
palmPitch = 0
palmRoll = 0
hands = False
grip = False

lm = 0
jy = 0
kb = 0
last = 0

#last move sended to the robot
last_move = "null"
gripped = False
client = None

#Method which truncate a number (f). the result will be (f) with only
# (n) decimal numbers
def truncate(f, n):
	'''Truncates/pads a float f to n decimal places without rounding'''
	s = '{}'.format(f)
	if 'e' in s or 'E' in s:
		return '{0:.{1}f}'.format(f, n)
	i, p, d = s.partition('.')
	return '.'.join([i, (d+'0'*n)[:n]])

#Method which creates a new Goal and send it, making the robot moves in
# a certain way
def move(position):
	g = FollowJointTrajectoryGoal()
	g.trajectory = JointTrajectory()
	g.trajectory.joint_names = JOINT_NAMES
	g.trajectory.points = [JointTrajectoryPoint(positions=position, velocities=[0]*6, time_from_start=rospy.Duration(20.0))]
	client.send_goal(g)

#Method that compliment the subscription to a topic, each time that
# something is published into the topic this callback method is called
def callback_ur(data):
	#get each wrist position and change it from rad to degrees
	global J1,J2,J3,J4,J5,J6
	J1 = data.position[0]
	J2 = data.position[1]
	J3 = data.position[2]
	J4 = data.position[3]
	J5 = data.position[4]
	J6 = data.position[5]
	#rospy.loginfo("\nShoulder pan %s\nShoulder lift %s\nElbow %s\nWrist1 %s\nWrist2 %s\nwrist3 %s\n" % (J1,J2,J3,J4,J5,J6))

#Method that compliment the subscription to a topic, each time that
# something is published into the topic this callback method is called
def callback(data):
	global palmY, palmX, palmZ, palmYaw, palmPitch, palmRoll, hands, grip
	palmX = data.palm_position.x
	palmY = data.palm_position.y
	palmZ = data.palm_position.z
	palmYaw = data.ypr.x
	palmPitch = data.ypr.y
	palmRoll = data.ypr.z
	hands = data.hand_available
	grip = data.grab_action
	rospy.loginfo(data)

#Regarding the position of the user hands send different movements to
# the robot, making it moves according to the hand
def send_movement():
	global last_move
	global J1,J2,J3,J4,J5,J6
	global grip,gripped
	if hands:
		last_move = "move"
		if palmX > 70:
			x = -0.1
		elif palmX < -70:
			x = 0.1
		else:
			x = 0.0

		if palmY > 220:
			z = 0.1
		elif palmY < 110:
			z = -0.1
		else:
			z = 0

		if palmZ > 50:
			y = -0.1
		elif palmZ < -50:
			y = 0.1
		else:
			y = 0

		if palmRoll > 50:
			rx = 0.1
		elif palmRoll < -50:
			rx = -0.1
		else:
			rx = 0

		if palmPitch > 50:
			ry = 0.1
		elif palmPitch < -50:
			ry = -0.1
		else:
			ry = 0

		if palmYaw > 50:
			rz = 0.1
		elif palmYaw < -50:
			rz = -0.1
		else:
			rz = 0

		move([x,y,z,rx,ry,rz])

	elif last_move != "stop":
		last_move = "stop"
		client.cancel_goal()

	if grip :
		gripped = not gripped
		#set_digital_out(8,gripped)

def check_input():
	global lm, jy, kb, last
	try:
		a = keyboard_talker.driver_state()
		if(a < 4):
			if(a == 1):
				if (last != 1):
					jy.unregister()
					kb.unregister()
					lm = rospy.Subscriber("leapmotion/data", LeapFrame, callback)
					print "You are now using <LeapMotion>"
					last = 1

				return True

			elif(a == 2):
				if (last != 2):
					lm.unregister()
					kb.unregister()
					jy = rospy.Subscriber("joystick/data",JoystickFrame, callback)
					print "You are now using a <Joystick>"
					last = 2
				return True
			elif(a == 3):
				if (last != 3):
					jy.unregister()
					lm.unregister()
					last = 3
					kb = rospy.Subscriber("keyboard/data", KeyboardFrame, callback)
					print "You are now using <Keyboard>"

				return True
		else:
			print "[WARN] Number incorrect"
			return False
	except ValueError:
		print "[EXCEPTION] Introduce a correct number"
		return False

def select_hardware():
	while(True):
		check_input()

def leapMotion_init():
	os.system("LeapControlPanel")

def init_threads(screen,clock):
	
	t = threading.Thread(target=leapMotion_init, args = ())
	t.daemon = True
	t.start()
	
	t = threading.Thread(target=select_hardware, args = ())
	t.daemon = True
	t.start()

	t = threading.Thread(target=joystick_talker.talker, args = ())
	t.daemon = True
	t.start()

	t = threading.Thread(target=keyboard_talker.keypress, args = (screen, clock))
	t.daemon = True
	t.start()
	
	t = threading.Thread(target=leap_talker.main, args = ())
	t.daemon = True
	t.start()


def main():
	global client,lm,jy,kb
	try:
		rospy.init_node("test_move", anonymous=True, disable_signals=True)
		client = actionlib.SimpleActionClient('follow_joint_trajectory', FollowJointTrajectoryAction)

		pygame.init()
		screen = pygame.display.set_mode((650,370),0,32)
		clock = pygame.time.Clock()
		
		counter = 0
		while counter<60:
			for event in pygame.event.get():
				pressed = pygame.key.get_pressed()
				if event.type == pygame.QUIT:
					leapMotion_stop()
					rospy.signal_shutdown("KeyboardInterrupt")
					pygame.quit()
					end = True
			if counter % 20 == 0:
				display.start_screen(screen,3-counter/20)
			print counter
			time.sleep(0.1)
			counter += 1

		display.server_screen(screen)

		jy = rospy.Subscriber("joystick/data",JoystickFrame, callback)
		lm = rospy.Subscriber("leapmotion/data", LeapFrame, callback)
		kb = rospy.Subscriber("keyboard/data", KeyboardFrame, callback)
		jy.unregister()
		lm.unregister()
		kb.unregister()
		
		init_threads(screen,clock)

		while(True):
			send_movement()
			time.sleep (0.08) #which is almost 120Hz
			if (keyboard_talker.end):
				client.cancel_goal()
				rospy.signal_shutdown("KeyboardInterrupt")
				keyboard_talker.leapMotion_stop()
				pygame.quit()


	except KeyboardInterrupt:
		client.cancel_goal()
		rospy.signal_shutdown("KeyboardInterrupt")
		keyboard_talker.leapMotion_stop()
		pygame.quit()
		raise

if __name__ == '__main__': main()
