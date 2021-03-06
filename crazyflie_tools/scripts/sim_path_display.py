#!/usr/bin/env python

#Node for displaying path from the path planner
#author: Sarah Pohorecky - spohorec@mit.edu

#ARGUMENTS: cf_num (corresponding simulated Crazyflie number)

import rospy
import tf

import sys

from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Path

from planner.msg import HiPathTime
from map_maker import map_maker_helper as map_helper

#---------

class MakePath: #Gets Crazyflie's desired path from planner 
	def __init__(self,nodes_map,cf_num):
		print "Initializing converter..."
		rospy.Subscriber("/si_planner/time_path_topic",HiPathTime,self._convert_path) #This needs to be changed if you aren't using si_planner
		self.nodes_map = nodes_map
		self.cf_num = cf_num
		self.path = []
		print "Initialized..."

	def _convert_path(self,data):
			#print "Converting path..."
			if int(data.ID) == int(self.cf_num):
				self.path = []
				nodes = data.path
				for i in range(len(nodes)):
					self.path.append(self.nodes_map[nodes[i]][0]) #gets waypoint coordinates from node number

class PathDisplay():

	def __init__(self,out_topic,cf_num):

		self.cf_num = cf_num
		self.out_topic = out_topic

		#Gets node map from map_maker
		self.node_map = map_helper.map_maker_client('/send_complex_map')[0]

		self.mkpath = MakePath(self.node_map, self.cf_num) #generates path from current planned path

		#--------------------------------------------------------

		#Inits. Path message with a pose of (0,0,0,0,0,0,1)
		#So publisher doesn't freak out with no data
		self.path_msg = Path()
		self.path_msg.header.stamp = rospy.Time.now()
		self.path_msg.header.seq = 0
		self.path_msg.header.frame_id = "/world"

		self.init_pose = PoseStamped()
		self.init_pose.header.seq = 0
		self.init_pose.header.stamp = rospy.Time.now()
		self.init_pose.header.frame_id = "/world"
		self.init_pose.pose.position.x = 0
		self.init_pose.pose.position.y = 0
		self.init_pose.pose.position.z = 0
		
		yaw = 0
		quaternion = tf.transformations.quaternion_from_euler(0, 0, yaw)
		
		self.init_pose.pose.orientation.x = quaternion[0]
		self.init_pose.pose.orientation.y = quaternion[1]
		self.init_pose.pose.orientation.z = quaternion[2]
		self.init_pose.pose.orientation.w = quaternion[3]

		self.path_msg.poses.append(self.init_pose)

		#--------------------------------------------------------

		self.pub = rospy.Publisher(self.out_topic,Path,queue_size=10)

		#Makes and publishes paths while running
		r = rospy.Rate(30)
		while not rospy.is_shutdown():
			self.make_path()
			self.pub_path()
			r.sleep()

	#makes all the coordinates from generated path into Path() message
	def make_path(self):
		self.path_msg.poses = []
		for coord in self.mkpath.path:
			pose = PoseStamped()
			pose.header.stamp = rospy.Time.now()
			pose.header.frame_id = "/world"
			pose.pose.position.x = coord[0]
			pose.pose.position.y = coord[1]
			pose.pose.position.z = coord[2]
			self.path_msg.poses.append(pose)


	def pub_path(self):
		self.path_msg.header.stamp = rospy.Time.now()
		self.pub.publish(self.path_msg)

if __name__ == '__main__':
	rospy.init_node("sim_path_display")
	cf_num = sys.argv[1]
	display_pose = PathDisplay("d_path",cf_num)
	

