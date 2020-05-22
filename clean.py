#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from math import pi, fabs, sqrt, pow, atan2

class Cleaner(object):
    def __init__(self):
        self.velo = Twist()
        self.theta = 0
        self.x_pos = 0
        self.y_pos = 0
        self.x0 = 0
        self.y0 = 0

        clean = raw_input('What type of cleaning would you like (Enter spiral or grid): ')

        if clean == 'grid':
            self.currentPosition()
            self.Goal(1, 1)
            self.desiredOrientation(0)
            self.move(9)
            self.desiredOrientation(90)
            self.move(9)
            self.desiredOrientation(180)
            self.move(2)
            self.desiredOrientation(-90)
            self.move(9)
        elif clean == 'spiral':
            self.spiralClean()
        else:
            print('Error: Invalid input')

        rospy.spin()

    def currentPosition(self):
        rospy.Subscriber('/turtle1/pose', Pose, self.poseCallback)

    def poseCallback(self, pose):
        self.x_pos = pose.x
        self.y_pos = pose.y
        self.theta = pose.theta
        
        # Get initial position before moving for distance calculation
        if self.velo.linear.x == 0.0:
            self.x0 = pose.x
            self.y0 = pose.y

    def Distance(self, des_x, des_y):
        return sqrt(pow(des_x - self.x_pos, 2) + pow(des_y - self.y_pos, 2))
    
    def move(self, distance):
        self.currentPosition()
        self.velo.linear.x = 1
        
        # While loop for moving distance
        while self.Distance(self.x0, self.y0) <= distance:
            pub.publish(self.velo)
            rate.sleep()
            self.currentPosition()
        self.velo.linear.x = 0
        pub.publish(self.velo)

    def Goal(self, goal_x, goal_y):
        goal = True
        while goal == True:
            self.currentPosition()
            if self.Distance(goal_x, goal_y) < 0.1:
                goal = False
            else:
                self.velo.linear.x = 1.2*self.Distance(goal_x, goal_y)
                self.velo.angular.z = 4*(atan2(goal_y - self.y_pos, goal_x - self.x_pos) - self.theta)
                pub.publish(self.velo)
                rate.sleep()
        self.velo.linear.x = 0
        self.velo.angular.z = 0
        pub.publish(self.velo)

    def desiredOrientation(self, desired_angle):
        self.currentPosition()
        ang_diff = desired_angle - radians2degrees*self.theta
        if ang_diff > 0:
            clockwise = bool(0)
            self.rotate(fabs(ang_diff), clockwise)
        elif ang_diff < 0:
            clockwise = bool(1)
            self.rotate(fabs(ang_diff), clockwise)
        else:
            print('At desired angle')
    
    def rotate(self, inputted_angle, clockwise):
        # Rotation decision
        if clockwise:
            self.velo.angular.z = -0.5
        else:
            self.velo.angular.z = 0.5
        
        t0 = rospy.get_time()
        rotation = True
        while rotation == True:
            pub.publish(self.velo)
            t1 = rospy.get_time()
            current_angle = fabs(self.velo.angular.z)*(t1 - t0)
            rate.sleep()
            if radians2degrees*current_angle >= inputted_angle + 0.5:
                rotation = False

        self.velo.angular.z = 0
        pub.publish(self.velo)

    def spiralClean(self):
        self.velo.angular.z = 4
        r = 0.5
        while True:
            r += 0.5
            self.velo.linear.x = r
            pub.publish(self.velo)
            rate.sleep()
            self.currentPosition()
            print(self.x_pos, self.y_pos)
            if self.x_pos >= 10 or self.y_pos >= 10:
                print('Spiral cleaning finished')
                break
        self.velo.linear.x = 0
        pub.publish(self.velo)


try:
    rospy.init_node('turtle_cleaner')
    pub = rospy.Publisher('/turtle1/cmd_vel', Twist, queue_size=10)
    rate = rospy.Rate(20)
    degrees2radians = pi/180
    radians2degrees = 180/pi
    Cleaner()
except rospy.ROSInterruptException:
    pass