#!/usr/bin/env python
import time
import roslib; roslib.load_manifest('ur_driver')
import rospy
import actionlib

from control_msgs.msg import *
from trajectory_msgs.msg import *
from sensor_msgs.msg import JointState
from ur_msgs.msg import *
from leap_motion.msg import LeapFrame
from threading import Thread

JOINT_NAMES = ['shoulder_pan_joint', 'shoulder_lift_joint', 'elbow_joint',
               'wrist_1_joint', 'wrist_2_joint', 'wrist_3_joint']

PI = 3.14159265359
d1 = 0.017453293 #1 degree in rad

#Robot joints position
global J1,J2,J3,J4,J5,J6
J1 = 0
J2 = 0
J3 = 0
J4 = 0
J5 = 0
J6 = 0

#Hand palm position and status
global palmY, palmX, palmZ, hands
palmX = 0
palmY = 0
palmZ = 0
hands = False

#last move sended to the robot
global last_move
last_move = "null"

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

#Regarding the position of the user hands send different movements to
# the robot, making it moves according to the hand
def send_movement():
	global last_move
	global J1,J2,J3,J4,J5,J6
	global p

	if hands:

		if palmX > 50 and palmY > 200 and palmZ > 30:
			#if last_move != "+x+y+z":
				#client.cancel_goal()
			last_move = "+x+y+z"
			move([J1-d1,J2+d1,J3-d1,J4,J5,J6])

		elif palmX < -50 and palmY > 200 and palmZ > 30:
			#if last_move != "-x+y+z":
				#client.cancel_goal()
			last_move = "-x+y+z"
			move([J1+d1,J2+d1,J3-d1,J4,J5,J6])

		elif palmX < -50 and palmY < 130 and palmZ > 30:
			#if last_move != "-x-y+z":
				#client.cancel_goal()
			last_move = "-x-y+z"
			move([J1+d1,J2-d1,J3-d1,J4,J5,J6])

		elif palmX < -50 and palmY < 130 and palmZ < -30:
			#if last_move != "-x-y-z":
				#client.cancel_goal()
			last_move = "-x-y-z"
			move([J1+d1,J2-d1,J3-d1,J4,J5,J6])

		elif palmX < -50 and palmY > 200 and palmZ < -30:
			#if last_move != "-x+y-z":
				#client.cancel_goal()
			last_move = "-x+y-z"
			move([J1+d1,J2+d1,J3+d1,J4,J5,J6])

		elif palmX > 50 and palmY > 200 and palmZ < -30:
			#if last_move != "+x+y-z":
				#client.cancel_goal()
			last_move = "+x+y-z"
			move([J1-d1,J2+d1,J3+d1,J4,J5,J6])

		elif palmX > 50 and palmY > 200:
			#if last_move != "+x+y":
				#client.cancel_goal()
			last_move = "+x+y"
			move([J1-d1,J2+d1,J3,J4,J5,J6])

		elif palmX < -50 and palmY < 130:
			#if last_move != "-x-y":
				#client.cancel_goal()
			last_move = "-x-y"
			move([J1+d1,J2-d1,J3,J4,J5,J6])

		elif palmX < -50 and palmY > 200:
			#if last_move != "-x+y":
				#client.cancel_goal()
			last_move = "-x+y"
			move([J1+d1,J2+d1,J3,J4,J5,J6])

		elif palmX > 50 and palmY < 130:
			#if last_move != "+x-y":
				#client.cancel_goal()
			last_move = "+x-y"
			move([J1-d1,J2-d1,J3,J4,J5,J6])

		elif palmX > 50 and palmZ > 30:
			#if last_move != "+x+z":
				#client.cancel_goal()
			last_move = "+x+z"
			move([J1-d1,J2,J3-d1*2,J4,J5,J6])

		elif palmX > 50 and palmZ < -30:
			#if last_move != "+x-z":
			#client.cancel_goal()
			last_move = "+x-z"
			move([J1-d1,J2,J3+d1*2,J4,J5,J6])

		elif palmX < -50 and palmZ > 30:
			#if last_move != "-x+z":
				#client.cancel_goal()
			last_move = "-x+z"
			move([J1+d1,J2,J3-d1*2,J4,J5,J6])

		elif palmX < -50 and palmZ < -30:
			#if last_move != "-x-z":
				#client.cancel_goal()
			last_move = "-x-z"
			move([J1+d1,J2,J3+d1*2,J4,J5,J6])

		elif palmY > 200 and palmZ > 30:
			#if last_move != "+y+z":
				#client.cancel_goal()
			last_move = "+y-z"
			move([J1,J2+d1,J3-d1*2,J4,J5,J6])

		elif palmY > 200 and palmZ < -30:
			#if last_move != "+y-z":
				#client.cancel_goal()
			last_move = "+y-z"
			move([J1,J2+d1,J2+d1*2,J4,J5,J6])

		elif palmY < 130 and palmZ < -30:
			#if last_move != "-y-z":
				#client.cancel_goal()
			last_move = "-y-z"
			move([J1,J2-d1,J3+d1*2,J4,J5,J6])

		elif palmY < 130 and palmZ > 30:
			#if last_move != "-y+z":
				#client.cancel_goal()
			last_move = "-y+z"
			move([J1,J2-d1,J3-d1*2,J4,J5,J6])

		elif palmY > 200:
			#if last_move != "up":
				#client.cancel_goal()
			last_move = "up"
			move([J1,J2+d1,J3,J4,J5,J6])

		elif palmY < 130:
			#if last_move != "down":
				#client.cancel_goal()
			last_move = "down"
			move([J1,J2-d1,J3,J4,J5,J6])

		elif palmX > 50:
			#if last_move != "right":
				#client.cancel_goal()
			last_move = "right"
			move([J1-d1,J2,J3,J4,J5,J6])

		elif palmX < -50:
			#if last_move != "left":
				#client.cancel_goal()
			last_move = "left"
			move([J1+d1,J2,J3,J4,J5,J6])

		elif palmZ > 30:
			#if last_move != "back":
				#client.cancel_goal()
			last_move = "back"
			move([J1,J2,J3-d1*2,J4,J5,J6])

		elif palmZ < -30:
			#if last_move != "front":
				#client.cancel_goal()
			last_move = "front"
			move([J1,J2,J3+d1*2,J4,J5,J6])
	else:
		if last_move != "stop":
			last_move = "stop"
			client.cancel_goal()
			rospy.loginfo("stop")

def main():
    global client
    try:
        rospy.init_node("test_move", anonymous=True, disable_signals=True)
        client = actionlib.SimpleActionClient('follow_joint_trajectory', FollowJointTrajectoryAction)
        print "Waiting for server..."
        client.wait_for_server()
        print "Connected to server"

        rospy.Subscriber("joint_states", JointState, callback_ur)
        rospy.Subscriber("leapmotion/data", LeapFrame, callback_lm)

        while(True):
			send_movement()
			#Sleep 0.08 which is almost 120Hz
			time.sleep(0.08)


    except KeyboardInterrupt:
        client.cancel_goal()
        rospy.signal_shutdown("KeyboardInterrupt")
        raise

if __name__ == '__main__': main()
