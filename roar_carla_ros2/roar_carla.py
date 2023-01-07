# Copyright 2023 michael. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from ackermann_msgs.msg import AckermannDriveStamped
from carla_msgs.msg import CarlaEgoVehicleControl
from nav_msgs.msg import Odometry
from typing import Optional


class CarlaVehicleControlNode(Node):
    def __init__(self):
        super().__init__("carla_vehicle_control_node")
        self.publisher_ = self.create_publisher(
            CarlaEgoVehicleControl, "/carla/ego_vehicle/vehicle_control_cmd", 10
        )
        self.ackermann_sub = self.create_subscription(
            AckermannDriveStamped,
            "/local_planner/control",
            self.onAckermannCmdReceived,
            10,
        )
        self.odom_sub = self.create_subscription(
            Odometry, "/carla/ego_vehicle/odometry", self.onOdomReceived, 10
        )
        self.declare_parameter("loop_rate", 0.05)
        loop_rate = self.get_parameter("loop_rate").get_parameter_value().double_value
        self.get_logger().info(f"Loop rate: {loop_rate}")
        self.timer = self.create_timer(loop_rate, self.sendCmd)
        self.odom: Optional[Odometry] = None
        self.ackermann_msg: Optional[AckermannDriveStamped] = None

    def sendCmd(self):
        if self.odom == None or self.ackermann_msg == None:
            return

        # assume upper pipeline will send how much to turn
        steering = self.calcSteering(self.ackermann_msg.drive.steering_angle, 0)
        throttle = self.calcThrottle(
            self.ackermann_msg.drive.speed, self.odom.twist.twist.linear.x
        )
        control_msg: CarlaEgoVehicleControl = CarlaEgoVehicleControl()
        control_msg.header.frame_id = "ego_vehicle"
        control_msg.header.stamp = self.get_clock().now().to_msg()
        control_msg.steer = float(steering)
        control_msg.throttle = float(throttle)
        control_msg.gear = 1
        if throttle < 0:
            # we might want to reconsider this behavior
            control_msg.reverse = True
        control_msg.throttle = float(self.clamp(abs(throttle), 0, 1))
        self.publisher_.publish(control_msg)

    def calcSteering(self, desired, actual) -> float:
        # TODO: write PID loop here
        return self.clamp(desired, -1, 1)

    def calcThrottle(self, desired, actual) -> float:
        # TODO: write PID loop here
        output = 0.3
        output = self.clamp(output, -1, 1)
        return output

    def onOdomReceived(self, msg: Odometry):
        self.odom = msg

    def onAckermannCmdReceived(self, msg: AckermannDriveStamped):
        self.ackermann_msg = msg

    def destroy_node(self) -> bool:
        import time

        control_msg: CarlaEgoVehicleControl = CarlaEgoVehicleControl()
        control_msg.header.frame_id = "ego_vehicle"
        control_msg.header.stamp = self.get_clock().now().to_msg()
        control_msg.steer = 0.0
        control_msg.gear = 1
        control_msg.throttle = 0.0
        control_msg.hand_brake = True

        num_tries = 5
        for i in range(num_tries):
            self.get_logger().info(f"Stopping vehicle before quitting: {i}/{num_tries}")
            self.publisher_.publish(control_msg)
            time.sleep(0.1)
        return super().destroy_node()

    @staticmethod
    def clamp(n, minn, maxn):
        return max(min(maxn, float(n)), minn)


def main(args=None):
    rclpy.init(args=args)

    try:
        node = CarlaVehicleControlNode()
        rclpy.spin(node)

    except Exception as e:
        print(e)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
