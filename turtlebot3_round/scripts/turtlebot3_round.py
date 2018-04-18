#!/usr/bin/env python

# Copyright (c) 2011, Willow Garage, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the Willow Garage, Inc. nor the names of its
#      contributors may be used to endorse or promote products derived from
#       this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import rospy

from geometry_msgs.msg import Twist

import sys, select, termios, tty

msg = """
Control Your Turtlebot3!
---------------------------
Moving around:
        w
   a    s    d
        x

w/x : increase/decrease velocity
a/d : increase/decrease radius
space key, s : force stop
r: start

Starting speed: circle of 10cm radius in 10 seconds
Minimum radius: 10 cms (also starting radius)
Maximum radius: 50 cms
CTRL-C to quit
"""

def getKey():
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

def vels(target_linear_vel, target_angular_vel):
    return "currently:\tlinear vel %s\t angular vel %s " % (target_linear_vel,target_angular_vel)

if __name__=="__main__":
    settings = termios.tcgetattr(sys.stdin)

    velstep = 2 * 3.1416 * 0.25 / 10
    radstep = 0.01
    radius = 0.1

    rospy.init_node('turtlebot3_round')
    pub = rospy.Publisher('/cmd_vel', Twist, queue_size=5)

    status = 0
    target_linear_vel = 0
    target_angular_vel = 0
    control_linear_vel = 0
    control_angular_vel = 0
    try:
        print msg
        while not rospy.is_shutdown():
            key = getKey()
            if key == 'w' :
                target_angular_vel = target_angular_vel + velstep
                target_linear_vel = target_angular_vel * radius
                status = status + 1
                print vels(target_linear_vel,target_angular_vel)
            elif key == 'x' :
                target_angular_vel = target_angular_vel - velstep
                target_linear_vel = target_angular_vel * radius
                status = status + 1
                print vels(target_linear_vel,target_angular_vel)
            elif key == 'a' :
                target_linear_vel = target_linear_vel * (radius - radstep) / radius
                radius = radius - radstep
                status = status + 1
                print vels(target_linear_vel,target_angular_vel)
            elif key == 'd' :
                target_linear_vel = target_linear_vel * (radius + radstep) / radius
                radius = radius + radstep
                status = status + 1
                print vels(target_linear_vel,target_angular_vel)
            elif key == ' ' or key == 's' :
                target_linear_vel   = 0
                control_linear_vel  = 0
                target_angular_vel  = 0
                control_angular_vel = 0
                print vels(0, 0)
            elif key == 'r' :
                radius = 0.1
                target_angular_vel = 2 * 3.1416 * radius
                target_linear_vel = target_angular_vel * radius
            elif status == 14 :
                print msg
                status = 0
            else:
                if (key == '\x03'):
                    break

            if target_linear_vel > control_linear_vel:
                control_linear_vel = min( target_linear_vel, control_linear_vel + (0.01/4.0) )
            else:
                control_linear_vel = target_linear_vel

            if target_angular_vel > control_angular_vel:
                control_angular_vel = min( target_angular_vel, control_angular_vel + (0.1/4.0) )
            else:
                control_angular_vel = target_angular_vel

            twist = Twist()
            twist.linear.x = control_linear_vel; twist.linear.y = 0; twist.linear.z = 0
            twist.angular.x = 0; twist.angular.y = 0; twist.angular.z = control_angular_vel
            pub.publish(twist)

    except:
        print e

    finally:
        twist = Twist()
        twist.linear.x = 0; twist.linear.y = 0; twist.linear.z = 0
        twist.angular.x = 0; twist.angular.y = 0; twist.angular.z = 0
        pub.publish(twist)

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
