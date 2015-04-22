#!/usr/bin/env python
import time
import roslib; roslib.load_manifest('ur_driver')
import rospy
import actionlib

from control_msgs.msg import *
from trajectory_msgs.msg import *
from sensor_msgs.msg import JointState
from ur_msgs.msg import *
from leap_motion.msg import leap
from leap_motion.msg import leapros

JOINT_NAMES = ['shoulder_pan_joint', 'shoulder_lift_joint', 'elbow_joint',
               'wrist_1_joint', 'wrist_2_joint', 'wrist_3_joint']

PI = 3.14159265359
d1 = 0.017453293 #1 degree in rad

global J1,J2,J3,J4,J5,J6
J1 = 0
J2 = 0
J3 = 0
J4 = 0
J5 = 0
J6 = 0

global palmY, palmX, palmZ, number
palmX = 0
palmY = 0
palmZ = 0
number = 0

global last_move
last_move = "null"

client = None

def move_up(UP):
    g = FollowJointTrajectoryGoal()
    g.trajectory = JointTrajectory()
    g.trajectory.joint_names = JOINT_NAMES
    g.trajectory.points = [JointTrajectoryPoint(positions=UP, velocities=[0]*6, time_from_start=rospy.Duration(10.0))]
    client.send_goal(g)

        
def move_down(DOWN):
    g = FollowJointTrajectoryGoal()
    g.trajectory = JointTrajectory()
    g.trajectory.joint_names = JOINT_NAMES
    g.trajectory.points = [JointTrajectoryPoint(positions=DOWN, velocities=[0]*6, time_from_start=rospy.Duration(10.0))]
    client.send_goal(g)
    

def callback_ur(data):
	#get each wrist position and change it from rad to degrees
	J1 = data.position[0]*180/PI
	J2 = data.position[1]*180/PI
	J3 = data.position[2]*180/PI
	J4 = data.position[3]*180/PI
	J5 = data.position[4]*180/PI
	J6 = data.position[5]*180/PI
	#rospy.loginfo("\nShoulder pan %s\nShoulder lift %s\nElbow %s\nWrist1 %s\nWrist2 %s\nwrist3 %s\n" % (J1,J2,J3,J4,J5,J6)) 

def callback_lm(data):
    global palmY, palmX, palmZ, number
    palmX = data.palmpos.x
    palmY = data.palmpos.y
    palmZ = data.palmpos.z
    number = data.hand_number
    #rospy.loginfo("Leap ROS Data \nx: %s\ny: %s\nz: %s" % (data.palmpos.x,data.palmpos.y,data.palmpos.z))
    
def send_movement():
	global last_move
	global J1,J2,J3,J4,J5,J6
	
	if palmY > 200: 
		if last_move != "up":
			 last_move = "up"
			 move_up([J1,J2+d1*2,J3,J4,J5,J6])			 
			 rospy.loginfo("moving up %s " % palmY)
	elif palmY < 130:
		if last_move != "down":
			last_move = "down"
			move_down([J1,J2-d1*2,J3,J4,J5,J6])
			rospy.loginfo("moving down %s " % palmY)
	else:
		if last_move != "stop":
			last_move = "stop"
			client.cancel_goal()
			rospy.loginfo("stop")	
	# x > 50 and x < -50and  y > 200 and y > 130 and z > 40 and z < 40)

def main():
    global client
    try:
        rospy.init_node("test_move", anonymous=True, disable_signals=True)
        client = actionlib.SimpleActionClient('follow_joint_trajectory', FollowJointTrajectoryAction)
        print "Waiting for server..."
        client.wait_for_server()
        print "Connected to server"
        
        rospy.Subscriber("joint_states", JointState, callback_ur)
        rospy.Subscriber("leapmotion/data", leapros, callback_lm)
        
        while(True):
			#send_movement()
			1+1

    except KeyboardInterrupt:
        client.cancel_goal()
        rospy.signal_shutdown("KeyboardInterrupt")
        raise

if __name__ == '__main__': main()
