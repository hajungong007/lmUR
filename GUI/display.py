#!/usr/bin/env python
import time
import pygame
import sys
import os
import rospy
sys.path.insert(0, '/home/ubuntu/catkin_ws/src/GUI/')
import inputBox
from pygame.locals import *


def start_screen(screen,counter):
	screen.fill((255,255,255))
	os.chdir("/home/ubuntu/catkin_ws/src/keyboard/scripts/")
	logo = pygame.image.load('logo.png')
	logo = pygame.transform.scale(logo, (int(146*1.3),int(188*1.3)))
	screen.blit(logo,(220,-3))
	#robot = pygame.image.load('robot.jpg')
	university = pygame.image.load('university.png')
	university = pygame.transform.scale(university, (int(259*0.7),int(194*0.7)))
	screen.blit(university,(450,225))
	myfont = pygame.font.SysFont("Calibri", 20)
	label = myfont.render("Made by:", 1, (105,185,255))
	screen.blit(label, (160,200))
	label = myfont.render("Alejandro Ariel Lora", 1, (105,185,255))
	screen.blit(label, (260,200))
	label = myfont.render("Gerard Sala", 1, (105,185,255))
	screen.blit(label, (260,220))
	label = myfont.render("Manuel Lagunas", 1, (105,185,255))
	screen.blit(label, (260,240))
	myfont = pygame.font.SysFont("Calibri", 15)
	label = myfont.render("Thanks to:", 1, (145,165,255))
	screen.blit(label, (160,270))
	label = myfont.render("Michael Alroe", 1, (145,165,255))
	screen.blit(label, (260,270))
	label = myfont.render("The application will start in: "+str(counter), 1, (105,185,255))
	screen.blit(label, (240,320))
	
	pygame.display.flip()
	
def show_error(text,screen):
	myfont = pygame.font.SysFont("Calibri", 30)
	label = myfont.render(text, 1, (145,185,255))
	screen.blit(label, (130, 100))
	pygame.display.flip()
	
def server_screen(screen, state):
	try:
		screen.fill((255,255,255))
		myfont = pygame.font.SysFont("Calibri", 19)
		label = myfont.render("Set the robot IP", 1, (0,0,0))
		screen.blit(label, (80, 165))
		label = myfont.render("to start moving it", 1, (0,0,0))
		screen.blit(label, (80, 185))
		myfont = pygame.font.SysFont("Calibri", 14)
		label = myfont.render(" 'numpad' may not work", 1, (145,185,255))
		screen.blit(label, (220, 200))
		myfont = pygame.font.SysFont("Calibri", 16)
		if state == 1:
			label = myfont.render(" Connecting...", 1, (105,185,255))
			screen.blit(label, (220, 140))
			return
		if state == 2:
			label = myfont.render(" Couldn.t stablish connection, try again", 1, (105,185,255))
			screen.blit(label, (160, 140))
		ip = inputBox.ask(screen, 'Robot IP:')
		pygame.display.flip()
		return ip
	except KeyboardInterrupt:
		rospy.signal_shutdown("KeyboardInterrupt")
		pygame.quit()
		raise


def update_display(screen, Button1, Button2, Button3):
	screen.fill((255,255,255))
	pygame.display.set_caption('leap motion - Universal robot (lmur)')
	#Parameters:	surface,color,x,y,length, height, width, text, text_color
	Button1.create_button(screen, (145,185,255), 50, 225, 150,75,100,"LeapMotion", (255,255,255))
	Button2.create_button(screen, (145,185,255), 245, 225, 150,75,100,"Joystick", (255,255,255))
	Button3.create_button(screen, (145,185,255), 450, 225, 150,75,100,"Keyboard", (255,255,255))
	pygame.display.flip()
