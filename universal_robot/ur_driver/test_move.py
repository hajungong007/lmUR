#!/usr/bin/env python
import time
import roslib; roslib.load_manifest('ur_driver')
import rospy
import actionlib
import threading

from control_msgs.msg import *
from trajectory_msgs.msg import *
from sensor_msgs.msg import JointState
from ur_msgs.msg import *
from leap_motion.msg import LeapFrame
from joystick.msg import JoystickFrame
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
hands = False
grip = False

lm = 0
jy = 0

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
def callback_lm(data):
	global palmY, palmX, palmZ, hands
	palmX = data.palm_position.x
	palmY = data.palm_position.y
	palmZ = data.palm_position.z
	hands = data.hand_available
	#rospy.loginfo("Leap ROS Data \nx: %s\ny: %s\nz: %s" % (data.palmpos.x,data.palmpos.y,data.palmpos.z))

#Method that compliment the subscription to a topic, each time that
# something is published into the topic this callback method is called
def callback_jy(data):
	global palmY, palmX, palmZ, hands, grip
	palmX = data.palm_position.x
	palmY = data.palm_position.y
	palmZ = data.palm_position.z
	hands = data.hand_available
	grip = data.grab_action
	#rospy.loginfo("Leap ROS Data \nx: %s\ny: %s\nz: %s" % (data.palmpos.x,data.palmpos.y,data.palmpos.z))

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
			y = 0.1
		elif palmY < 110:
			y = -0.1
		else:
			y = 0
			
		if palmZ > 50:
			z = -0.1
		elif palmZ < -50:
			z = 0.1
		else:
			z = 0
			
		#move([J1+d1*x,J2+d1*y,J3+d1*z,J4,J5,J6])
		move([x,y,z,0,0,0])
		
	elif last_move != "stop":
		last_move = "stop"
		client.cancel_goal()
		
	if grip :
		gripped = not gripped
		set_digital_out(8,gripped)
	
def check_input():
	global lm, jy
	try:
		inp = raw_input()
		a = int(inp)

		if(a < 3):
			if(a == 1):
				lm = rospy.Subscriber("leapmotion/data", LeapFrame, callback_lm)
				print "You are now using <LeapMotion>"
				return True

			elif(a == 2):
				jy = rospy.Subscriber("joystick/data",JoystickFrame, callback_jy)
				print "You are now using a <Joystick>"
				return True
		else:
			print "[WARN] Number incorrect"
			return False
	except ValueError:
		print "[EXCEPTION] Introduce a correct number"
		return False
	
def select_hardware():
	global lm,jy
	while(True):
		check_input()
		
def main():
	global client,lm,jy
	try:
		rospy.init_node("test_move", anonymous=True, disable_signals=True)
		client = actionlib.SimpleActionClient('follow_joint_trajectory', FollowJointTrajectoryAction)

		print "Waiting for server..."
		client.wait_for_server()
		print "Connected to server"
		state = rospy.Subscriber("joint_states", JointState, callback_ur)
		set_states()
		set_tool_voltage(24)
		print "Press 1 if you want to use LeapMotion"
		print "Press 2 if you want to use a Joystick "
		print "You can change the input device whenever you want"
		
		lm = rospy.Subscriber("leapmotion/data", LeapFrame, callback_lm)
		jy = rospy.Subscriber("joystick/data",JoystickFrame, callback_jy)
		lm.unregister()
		jy.unregister()
		
		check = False
		while(not check_input):
			check = check_input

		t = threading.Thread(target=select_hardware, args = ())
		t.daemon = True
		t.start()
		
		#move([-0.57,-0.39,-0.43,1.35,0.9,-1])
		#time.sleep(0.08)
		while(True):
			send_movement()
			time.sleep (0.08) #which is almost 120Hz
		



	except KeyboardInterrupt:
		client.cancel_goal()
		rospy.signal_shutdown("KeyboardInterrupt")
		raise

if __name__ == '__main__': main()
