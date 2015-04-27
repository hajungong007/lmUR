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
            # print 'Stuff'
            msg.hand_available = True
        elif buttonNumber == 2:
            msg.palm_position.z = 127
        elif buttonNumber == 3:
            msg.palm_position.z = -128
        elif buttonNumber == 4:
            msg.palm_position.x = -128
        elif buttonNumber == 5:
            msg.palm_position.x = 127
        elif buttonNumber == 8:
            msg.ypr.x = -45
        elif buttonNumber == 9:
            msg.ypr.x = 45
    elif action[4] == 0:
        # Button released
        if buttonNumber == 1:
            msg.hand_available = False
        elif buttonNumber == 2 or buttonNumber == 3:
            msg.palm_position.z = 0
        elif buttonNumber == 4 or buttonNumber == 5:
            msg.palm_position.x = 0
        elif buttonNumber == 8 or buttonNumber == 9:
            msg.ypr.x = 0

def joystickMoved(action):
    global msg
    value = converToSignedByte(action[5])
    if action[7] == 0:
        # X axis movement
        msg.ypr.z = round((value+0.5) / 1.41666666666)
    elif action[7] == 1:
        # Y axis movement
        msg.ypr.y = round((value+0.5) / 1.41666666666)
    elif action[7] == 2:
        # Z axis movement
        msg.palm_position.y = -(value + 1) + 165 # Invert

# while 1:
#     for byte in pipe.read(1):
#         action += [ord(byte)]
#         if len(action) == 8:
#             # print action
#             if isButtonAction(action):
#                 buttonAction(action)
#             elif isJoystickMovement(action):
#                 joystickMoved(action)
#
#             action = []

def talker():
    global msg
    global action
    publisher = rospy.Publisher('joystick/data', JoystickFrame, queue_size=10)
    rospy.init_node('JoystickPublisher', anonymous=True)
    while 1:

        for byte in pipe.read(1):
            action += [ord(byte)]
            if len(action) == 8:
                # print action
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
