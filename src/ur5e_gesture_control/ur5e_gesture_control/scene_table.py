"""Publish the classroom table TF and add a temporary table collision box."""
from geometry_msgs.msg import Pose, TransformStamped
from moveit_msgs.msg import CollisionObject
from shape_msgs.msg import SolidPrimitive
from tf2_ros import StaticTransformBroadcaster
from ur5e_gesture_control.scene_common import SceneNode, run_scene

TABLE_ID = 'gesture_test_table'


class TableNode(SceneNode):
    def __init__(self):
        super().__init__('gesture_table_scene')

    def make_object(self):
        # The transform remains available while the table node is running.
        self.broadcaster = StaticTransformBroadcaster(self)
        transform = TransformStamped()
        transform.header.stamp = self.get_clock().now().to_msg()
        transform.header.frame_id = 'base_link'
        transform.child_frame_id = 'table'
        transform.transform.rotation.z = 1.0
        transform.transform.rotation.w = 0.0
        self.broadcaster.sendTransform(transform)

        obj = CollisionObject()
        obj.id = TABLE_ID
        obj.header.frame_id = 'base_link'
        box = SolidPrimitive()
        box.type = SolidPrimitive.BOX
        box.dimensions = [1.0, 1.0, 0.05]
        pose = Pose()
        pose.position.z = -0.025
        pose.orientation.w = 1.0
        obj.primitives.append(box)
        obj.primitive_poses.append(pose)
        obj.operation = CollisionObject.ADD
        return obj


def main(args=None):
    run_scene(TableNode, TABLE_ID, {TABLE_ID, 'ur5e_test_scene_table'},
              (0.55, 0.55, 0.55, 1.0), args)
