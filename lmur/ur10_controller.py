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
import socket
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

MODE_TOOL = 1
MODE_JOINTS = 2

HOST = '192.168.1.100'
PORT = 30002
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
host = 0

#last move sended to the robot
last_move = "null"
gripped = False
client = None
changing = False
mode = MODE_JOINTS

#Method to send the command to move the tool
def move_tool(position):
	global last_move
	if position == [0,0,0,0,0,0]:
		if last_move != "stopl":
			stop()
	else:
		command = "speedl(%s,0.5,1)"%position
		last_move = "speedl"
		print command
		s.send(command+"\n")

	# print command

#Method to send the command to move the joints
def move_joints(position):
	global last_move
	if position == [0,0,0,0,0,0]:
		if last_move != "stopl":
			stop()
	else:
		command = "speedj(%s,0.5,1)"%position
		last_move = "speedj"
		print command
		s.send(command+"\n")

def stop():
	global last_move
	#time.sleep(0.05)
	if last_move != "stopl":
		command = "stopl(0.5)"
		s.send(command+"\n")
		last_move = "stopl"

def grab_action():
	global changing
	grab = grip
	string_bool = str(grab)
	command = "set_digital_out(8,"+string_bool+")"
	print command
	s.send(command+"\n")
	time.sleep(2)
	changing = False


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
	global palmY, palmX, palmZ, palmYaw, palmPitch, palmRoll, hands, grip, changing
	palmX = data.palm_position.x
	palmY = data.palm_position.y
	palmZ = data.palm_position.z
	palmYaw = data.ypr.x
	palmPitch = data.ypr.y
	palmRoll = data.ypr.z
	hands = data.hand_available
	if not changing:
		grip = data.grab_action
	#rospy.loginfo("\nx: %s\ny: %s\nz: %s" % (data.palm_position.x,data.palm_position.y,data.palm_position.z))

#Regarding the position of the user hands send different movements to
# the robot, making it moves according to the hand
def send_movement():
	global J1,J2,J3,J4,J5,J6
	global grip,gripped,changing
	if hands:
		if palmX > 70:
			x = float(round(0.000476 * palmX - 0.0333,2))
		elif palmX < -70:
			x = float(round(0.000476 * palmX + 0.0333,2))
		else:
			x = 0.00

		if palmY > 220:
			z = float(round(0.001333 * palmY - 0.28,2))
		elif palmY < 110:
			z = float(round(0.00125 * palmY - 0.15,2))
		else:
			z = 0.00

		if palmZ > 50:
			y = float(round(-0.000666 * palmZ + 0.0333,2))
		elif palmZ < -50:
			y = float(round(-0.000666 * palmZ - 0.0333,2))
		else:
			y = 0.00

		if palmRoll > 25:
			ry = float(round(palmRoll*0.002,2))
		elif palmRoll < -25:
			ry = float(round(palmRoll*0.002,2))
		else:
			ry = 0.00

		if palmPitch > 25:
			rx = float(round(palmPitch*0.002,2))
		elif palmPitch < -25:
			rx = float(round(palmPitch*0.002,2))
		else:
			rx = 0.00

		if palmYaw > 25:
			rz = float(round(-palmYaw*0.002,2))
		elif palmYaw < -25:
			rz = float(round(-palmYaw*0.002,2))
		else:
			rz = 0.00
		
		mode = keyboard_talker.mode_state()
		
		if mode == MODE_TOOL:
			move_tool([x,y,z,rx,ry,rz])
		elif mode == MODE_JOINTS:
			move_joints([rz,rx,ry,0,0,0])

		if grip and not gripped:
			if not changing:
				changing = True
				t = threading.Thread(target=grab_action)
				t.start()
			gripped = True
		if not grip and gripped:
			if not changing:
				changing = True
				t = threading.Thread(target=grab_action)
				t.start()
			gripped = False
	else:
		stop()

def check_input():
	global lm, jy, kb, last
	try:
		a = keyboard_talker.driver_state()
		if(a < 4):
			if(a == 1):
				jy.unregister()
				kb.unregister()
				if (last != 1):
					print last
					lm = rospy.Subscriber("leapmotion/data", LeapFrame, callback)
					print "You are now using <LeapMotion>"
					last = 1
				return True
			elif(a == 2):
				lm.unregister()
				kb.unregister()
				if (last != 2):
					print last
					jy = rospy.Subscriber("joystick/data",JoystickFrame, callback)
					print "You are now using a <Joystick>"
					last = 2
				return True
			elif(a == 3):
				jy.unregister()
				lm.unregister()
				if (last != 3):
					print last
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

def init_leap():
	os.system("LeapControlPanel")

def init_screen(screen):
	counter = 0
	while counter<60:
		for event in pygame.event.get():
			pressed = pygame.key.get_pressed()
			if event.type == pygame.QUIT:
				os.system("pkill LeapControlPane")
				os.system("pkill roscore")
				leapMotion_stop()
				rospy.signal_shutdown("KeyboardInterrupt")
				pygame.quit()
				end = True
		if counter % 20 == 0:
			display.start_screen(screen,3-counter/20)
		time.sleep(0.08)
		counter += 1

def init_threads(screen,clock):

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

def info_connection(screen):
	display.trying_to_connect(screen)

def init_server(screen):
	global s,host
	connected = False
	state = 0
	while not connected:
		host = display.server_screen(screen, state)
		try:
			display.server_screen(screen, 1)
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((host, PORT))
			connected = True
		except socket.error as msg:
			print "Couldn't establish connection with the robot"
			print msg
			state = 2
			pass

def init_subscriber():
	global lm,jy,kb
	jy = rospy.Subscriber("joystick/data",JoystickFrame, callback)
	lm = rospy.Subscriber("leapmotion/data", LeapFrame, callback)
	kb = rospy.Subscriber("keyboard/data", KeyboardFrame, callback)
	jy.unregister()
	lm.unregister()
	kb.unregister()

creating = False

def socket_clean():
	global creating,s,host
	while True:
		time.sleep(30)
		creating = True
		s.close()
		s = socket.create_connection((host, PORT))
		creating = False

def init_move():
	global creating
	while(True):
		if not creating:
			send_movement()
			time.sleep (0.08) #which is almost 120Hz
		if (keyboard_talker.end):
			client.cancel_goal()
			rospy.signal_shutdown("KeyboardInterrupt")
			keyboard_talker.leapMotion_stop()
			pygame.quit()

def main():
	global client,s
	try:
		os.system("roscore &")

		pygame.init()
		screen = pygame.display.set_mode((650,370),0,32)
		clock = pygame.time.Clock()

		init_subscriber()
		init_screen(screen)
		init_server(screen)
		rospy.init_node("test_move", anonymous=True, disable_signals=True)
		init_threads(screen,clock)
		t = threading.Thread(target=socket_clean)
		t.daemon = True
		t.start()
		init_move()
	except KeyboardInterrupt:
		s.close
		rospy.signal_shutdown("KeyboardInterrupt")
		keyboard_talker.leapMotion_stop()
		pygame.quit()
		raise

if __name__ == '__main__': main()
