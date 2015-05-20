#!/usr/bin/env python

import rospy
import sys, threading
import select
import termios, fcntl, sys, os
sys.path.insert(0, '/home/ubuntu/catkin_ws/src/GUI/')
import button
from keyboard.msg import KeyboardFrame
from geometry_msgs.msg import Point, Vector3
import pygame
from pygame.locals import *

publiser = False
tool = False
grab = False

msg = KeyboardFrame()
msg.hand_available = False
msg.palm_position = Point()
msg.ypr = Vector3()

"""
if  state = 0 no drivers inicialized
	state = 1 Leap Motion
	state = 2 Joystick
	state = 3 Keyboard
"""
state = 0

def driver_state():
	global state
	return state

def update_display(screen, Button1, Button2, Button3):
	 screen.fill((250,250,250))
	 #Parameters:	surface,color,x,y,length, height, width, text, text_color
	 Button1.create_button(screen, (145,185,255), 50, 225, 150,75,100,"LeapMotion", (255,255,255))
	 Button2.create_button(screen, (145,185,255), 245, 225, 150,75,100,"Joystick", (255,255,255))
	 Button3.create_button(screen, (145,185,255), 450, 225, 150,75,100,"Keyboard", (255,255,255))
	 pygame.display.flip()

def keypress(screen, clock):
	global tool,grab, state
	pygame.init()
	#screen = pygame.display.set_mode((640, 480))
	#clock = pygame.time.Clock()
	
	msg.palm_position.y = 160
	msg.hand_available = True
	
	#rospy.init_node('KeyboardPublisher', anonymous=True)
	publisher = rospy.Publisher('keyboard/data', KeyboardFrame, queue_size=10)
	Button1 = button.Button()
	Button2 = button.Button()
	Button3 = button.Button()
	update_display(screen,Button1, Button2, Button3)

	pygame.key.set_repeat(50,50)

	while True:
		for event in pygame.event.get():
			pressed = pygame.key.get_pressed()
			
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit 
				return
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_w :
					if tool:
						msg.ypr.y = 90
					else:
						msg.palm_position.y = 250
				if event.key == pygame.K_a:
					if tool:
						msg.ypr.x = -90
					else:
						msg.palm_position.x = -90
				if event.key == pygame.K_s:
					if tool:
						msg.ypr.y = -90
					else:
						msg.palm_position.y = 50
				if event.key == pygame.K_d :
					if tool:
						msg.ypr.x = 90
					else:
						msg.palm_position.x = 90
				if event.key == pygame.K_q:
					if tool:
						msg.ypr.z = -90
					else:
						msg.palm_position.z = -90
				if event.key == pygame.K_e:
					if tool:
						msg.ypr.z = 90
					else:
						msg.palm_position.z = 80
				if event.key == pygame.K_r :
					tool = False
				if event.key == pygame.K_t:
					tool = True
				if event.key == pygame.K_SPACE:
					grab = not grab
					msg.grab_action = grab
			if event.type == pygame.KEYUP:
				if not pressed[K_w] and not pressed[K_s]:
					if tool:
						msg.ypr.y = 0.0
					else:
						msg.palm_position.y = 160
				if not pressed[K_a] and not pressed[K_d]:
					if tool:
						msg.ypr.x = 0.0
					else:
						msg.palm_position.x = 0.0
				if not pressed[K_q] and not pressed[K_e]:
					if tool:
						msg.ypr.z = 0.0
					else:
						msg.palm_position.z = 0.0
			if event.type == MOUSEBUTTONDOWN:
				if Button1.pressed(pygame.mouse.get_pos()):
					update_display(screen, Button1, Button2, Button3)
					myfont = pygame.font.SysFont("Calibri", 30)
					label = myfont.render("You are now using Leap Motion", 1, (145,185,255))
					screen.blit(label, (180, 100))
					state = 1
				if Button2.pressed(pygame.mouse.get_pos()):
					update_display(screen, Button1, Button2, Button3)
					myfont = pygame.font.SysFont("Calibri", 30)
					label = myfont.render("You are now using Joystick", 1, (145,185,255))
					screen.blit(label, (180, 100))
					state = 2
				if Button3.pressed(pygame.mouse.get_pos()):
					update_display(screen, Button1, Button2, Button3)
					myfont = pygame.font.SysFont("Calibri", 30)
					label = myfont.render("You are now using Keyboard", 1, (145,185,255))
					screen.blit(label, (180, 100))
					state = 3
				# determine if a letter key was unpressed 
		pygame.display.flip()
		publisher.publish(msg)
		clock.tick(20)
		#rospy.loginfo(msg)
		
		
if __name__ == "__main__":
	try:
		keypress()
	except KeyboardInterrupt:
		rospy.signal_shutdown("KeyboardInterrupt")
		raise
		
