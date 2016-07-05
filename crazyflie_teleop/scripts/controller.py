#!/usr/bin/env python

import rospy
from sensor_msgs.msg import Joy
from crazyflie_driver.srv import UpdateParams
from std_srvs.srv import Empty

class Controller():
    def __init__(self, use_controller, joy_topic):
        rospy.wait_for_service('update_params')
        rospy.loginfo("found update_params service")
        self._update_params = rospy.ServiceProxy('update_params', UpdateParams)

        rospy.loginfo("waiting for emergency service")
        rospy.wait_for_service('emergency')
        rospy.loginfo("found emergency service")
        self._emergency = rospy.ServiceProxy('emergency', Empty)

        if use_controller:
            rospy.loginfo("waiting for land service")
            rospy.wait_for_service('land')
            rospy.loginfo("found land service")
            self._land = rospy.ServiceProxy('land', Empty)

            rospy.loginfo("waiting for takeoff service")
            rospy.wait_for_service('takeoff')
            rospy.loginfo("found takeoff service")
            self._takeoff = rospy.ServiceProxy('takeoff', Empty)
        else:
            self._land = None
            self._takeoff = None

        # subscribe to the joystick at the end to make sure that all required
        # services were found
        self._buttons = None
        rospy.Subscriber(joy_topic, Joy, self._joyChanged)

    def _joyChanged(self, data):
        for i in range(0, len(data.buttons)):
            if self._buttons == None or data.buttons[i] != self._buttons[i]:
                if i == 0 and data.buttons[i] == 1 and self._land != None:
                    self._land()
                if i == 1 and data.buttons[i] == 1:
                    self._emergency()
                if i == 2 and data.buttons[i] == 1 and self._takeoff != None:
                    self._takeoff()
                if i == 4 and data.buttons[i] == 1:
                    rospy.set_param("wheels/state", 2)
                    rospy.set_param("wheels/pwm_1", 230)
                    rospy.set_param("wheels/pwm_2", 230)
                elif i == 5 and data.buttons[i] == 1:
                    rospy.set_param("wheels/state", 1)
                    rospy.set_param("wheels/pwm_1", 230)
                    rospy.set_param("wheels/pwm_2", 230)
                elif i == 6 and data.buttons[i] == 1:
                    rospy.set_param("wheels/state", 3)
                    rospy.set_param("wheels/pwm_1", 230)
                    rospy.set_param("wheels/pwm_2", 230)
                elif i == 7 and data.buttons[i] == 1:
                    rospy.set_param("wheels/state", 4)
                    rospy.set_param("wheels/pwm_1", 230)
                    rospy.set_param("wheels/pwm_2", 230)
                else:
                    rospy.set_param("wheels/state", 0)
                    rospy.set_param("wheels/pwm_1", 0)
                    rospy.set_param("wheels/pwm_2", 0)
                self._update_params(["wheels/state"])
                self._update_params(["wheels/pwm_1"])
                self._update_params(["wheels/pwm_2"])

        self._buttons = data.buttons

if __name__ == '__main__':
    rospy.init_node('crazyflie_demo_controller', anonymous=True)
    use_controller = rospy.get_param("~use_crazyflie_controller", False)
    joy_topic = rospy.get_param("~joy_topic", "joy")
    controller = Controller(use_controller, joy_topic)
    rospy.spin()