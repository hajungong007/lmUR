#!/usr/bin/env python

import rospy
import sys

from joystick.msg import JoystickFrame
from geometry_msgs.msg import Point, Vector3

pipe = open('/dev/input/js0','r')

msg = JoystickFrame()
msg.hand_available = False
msg.palm_position = Point()
msg.ypr = Vector3()

action = []

def converToSignedByte(byte):
    if byte > 127:
        return (256-byte) * (-1)
    else:
        return byte

def isButtonAction(action):
    if action[6] == 1:
        return True
    else:
        return False

def isJoystickMovement(action):
    if action[6] == 2:
        return True
    else:
        return False

def buttonAction(action):
    global msg
    buttonNumber = action[7]+1
    if action[4] == 1:
        # Button pressed
        if buttonNumber == 1:
            # Trigger
            msg.hand_available = True
        elif buttonNumber == 2:
            # Grab
            msg.grab_action = True

    elif action[4] == 0:
        # Button released
        if buttonNumber == 1:
            # Trigger
            msg.hand_available = False
        elif buttonNumber == 2:
            # Grab
            msg.grab_action = False

def joystickMoved(action):
    global msg
    value = converToSignedByte(action[5])
    if action[7] == 0:
        # Roll movement
        msg.ypr.z = round((value+0.5) / 1.41666666666)
    elif action[7] == 1:
        # Pitch movement
        msg.ypr.y = round((value+0.5) / 1.41666666666)
    elif action[7] == 2:
        # Yaw movement
        msg.ypr.x = round((value+0.5) / 1.41666666666)
    elif action[7] == 3:
        # Y movement
        msg.palm_position.y = -(value + 1) + 165 # Invert
    elif action[7] == 4:
        # X movement
        msg.palm_position.x = value
    elif action[7] == 5:
        # Z movement
        msg.palm_position.z = value

def talker():
    global msg
    global action
    publisher = rospy.Publisher('joystick/data', JoystickFrame, queue_size=10)
    rospy.init_node('JoystickPublisher', anonymous=True)
    while 1:

        for byte in pipe.read(1):
            action += [ord(byte)]
            if len(action) == 8:
                if isButtonAction(action):
                    buttonAction(action)
                elif isJoystickMovement(action):
                    joystickMoved(action)

                action = []

                rospy.loginfo(msg)
                publisher.publish(msg)

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
