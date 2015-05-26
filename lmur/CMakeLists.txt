cmake_minimum_required(VERSION 2.8.3)
project(lmur)

## Find catkin macros and libraries
## if COMPONENTS list like find_package(catkin REQUIRED COMPONENTS xyz)
## is used, also find other catkin packages
find_package(catkin REQUIRED dynamic_reconfigure)

catkin_python_setup()


generate_dynamic_reconfigure_options(
  cfg/URDriver.cfg
)

###################################
## catkin specific configuration ##
###################################
catkin_package()

#############
## Install ##
#############
install(PROGRAMS ur10_controller.py
   DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

#############
## Testing ##
#############
