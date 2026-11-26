"""Add a configurable cylinder at coordinates in the table frame."""
import math
import time
import rclpy
from geometry_msgs.msg import Pose
from moveit_msgs.msg import CollisionObject
from shape_msgs.msg import SolidPrimitive
from tf2_ros import Buffer, TransformListener
import tf2_geometry_msgs
from ur5e_gesture_control.scene_common import SceneNode, run_scene

CYLINDER_ID = 'gesture_test_cylinder'


class CylinderNode(SceneNode):
    def __init__(self):
        super().__init__('gesture_cylinder_scene')
        for name, value in [('x_cm', -5.0), ('y_cm', -39.0),
                            ('height_cm', 25.0), ('radius_cm', 3.5)]:
            self.declare_parameter(name, value)
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

    def make_object(self):
        x, y, height, radius = [float(self.get_parameter(n).value) for n in
                                ('x_cm', 'y_cm', 'height_cm', 'radius_cm')]
        if not all(math.isfinite(v) for v in (x, y, height, radius)) or height <= 0 or radius <= 0:
            raise ValueError('Coordinates must be finite and dimensions positive')
        # Convert once into base_link, so the world object remains fixed even
        # after the temporary gesture launch stops publishing its TF.
        deadline = time.monotonic() + 10.0
        while rclpy.ok() and time.monotonic() < deadline:
            if self.tf_buffer.can_transform('base_link', 'table', rclpy.time.Time()):
                transform = self.tf_buffer.lookup_transform('base_link', 'table', rclpy.time.Time())
                break
            rclpy.spin_once(self, timeout_sec=0.1)
        else:
            raise RuntimeError('TF base_link <- table unavailable; start scene_table first')
        pose = Pose()
        pose.position.x = x / 100.0
        pose.position.y = y / 100.0
        pose.position.z = height / 200.0
        pose.orientation.w = 1.0
        obj = CollisionObject()
        obj.id = CYLINDER_ID
        obj.header.frame_id = 'base_link'
        shape = SolidPrimitive()
        shape.type = SolidPrimitive.CYLINDER
        shape.dimensions = [height / 100.0, radius / 100.0]
        obj.primitives.append(shape)
        obj.primitive_poses.append(tf2_geometry_msgs.do_transform_pose(pose, transform))
        obj.operation = CollisionObject.ADD
        self.get_logger().info(f'Cylinder in table frame: x={x:g} cm, y={y:g} cm, height={height:g} cm, radius={radius:g} cm')
        return obj


def main(args=None):
    run_scene(CylinderNode, CYLINDER_ID, {CYLINDER_ID}, (0.9, 0.2, 0.1, 1.0), args)
