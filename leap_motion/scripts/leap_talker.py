#!/usr/bin/env python
import rospy
import os, sys, inspect
import Leap
from begginer_tutorials.msg import LeapFrame
class SampleListener(Leap.Listener):

    def on_init(self, controller):
        print "Leap Motion Controller Initialized"
        self.publisher = rospy.Publisher('leapmotion/data',LeapFrame, queue_size=10)
        rospy.init_node('LeapPublisher', anonymous = True)
        self.msg = LeapFrame()
        self.msg.hand_available = False
        self.msg.palm_position = Point()
        self.msg.ypr = Vector3()

    def on_connect(self, controller):
        print "Connected"

    def on_frame(self, controller):
        print "Frame available"
        frame = controller.frame()
        hands = frame.hands
        if not hands.is_empty:
            hand = hands.rightmost
            position = hand.palm_position

            # Fill message with information from Leap
            self.msg.hand_available = True
            self.msg.palm_position.x = position.x
            self.msg.palm_position.y = position.y
            self.msg.palm_position.z = position.z
            self.msg.ypr.x = hand.direction.yaw * Leap.RAD_TO_DEG
            self.msg.ypr.y = hand.direction.pitch * Leap.RAD_TO_DEG
            self.msg.ypr.z = hand.palm_normal.roll * Leap.RAD_TO_DEG
        else:
            self.msg.hand_available = False
            self.msg.palm_position.x = 0
            self.msg.palm_position.y = 0
            self.msg.palm_position.z = 0
            self.msg.ypr.x = 0
            self.msg.ypr.y = 0
            self.msg.ypr.z = 0

        # Publish message to the topic
        rospy.loginfo(self.msg)
        self.publisher.publish(self.msg)

    def on_disconnect(self, controller):
        print "Leap Motion Disconnected"

    def on_exit(self, controller):
        print "Leap Motion Controller Exited"


def main():
	# Create a sample listener and controller
    listener = SampleListener()
    controller = Leap.Controller()

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    # Keep this process running until Enter is pressed
    print "Press Enter to quit..."
    try:
        raw_input("\n")
    except KeyboardInterrupt:
        pass
    finally:
        # Remove the sample listener when done
    	controller.remove_listener(listener)

if __name__ == "__main__":
    main()
