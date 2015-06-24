#lmUR

Description
-----------
lmUR is an application used to move a robot, the UR10, which is controlled by an input device. The different input devices used in the project are Leap Motion (Main goal of the project), a joystick (Logitech 3D extreme pro) and a keyboard. All of them send different coordinates to the robot through a computer. Furthermore, the background used is the operating system ROS, an operating system made to work with robots. This background enables the transfer of information easily between the robot and the input devices. All the drivers are already programmed inside lmUR.

Installation
-----------
In order to run the application we need at least one of the input devices mentioned above and the UR10 connected with the computer with an RJ45 cable, robot and the computer must be in the same network. Also, you need the library pyGame installed and ROS Hydro, running on Ubuntu.

Usage
-----------
First of all we have to go inside the folder catkin_ws, once we are there we have to run `catkin_make` to compile all the files. After that the command `rosrun lmur ur10_controller.py` has to be run. Now we can easily control the robot regarding the position of the tool or regarding the position of the joints and we can move it using either Leap Motion, the Joystick or the Keyboard.
