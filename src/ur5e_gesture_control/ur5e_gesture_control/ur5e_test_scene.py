"""Add a temporary table and cylinder to the shared MoveIt planning scene."""
import signal

import rclpy
from geometry_msgs.msg import Pose
from moveit_msgs.msg import CollisionObject, PlanningScene, PlanningSceneComponents
from moveit_msgs.srv import ApplyPlanningScene, GetPlanningScene
from rclpy.node import Node
from rclpy.signals import SignalHandlerOptions
from shape_msgs.msg import SolidPrimitive


TABLE_ID = 'gesture_test_table'
CYLINDER_ID = 'gesture_test_cylinder'
OBJECT_IDS = (TABLE_ID, CYLINDER_ID)
# The original test-scene table occupies the same space as this table.
OTHER_TABLE_ID = 'ur5e_test_scene_table'


class TestScene(Node):
    def __init__(self):
        super().__init__('gesture_test_scene')
        self.declare_parameter('remove_only', False)
        self.apply_client = self.create_client(ApplyPlanningScene, '/apply_planning_scene')
        self.get_client = self.create_client(GetPlanningScene, '/get_planning_scene')

    def call(self, client, request):
        if not client.wait_for_service(timeout_sec=10.0):
            raise RuntimeError(f'Service unavailable: {client.srv_name}')
        future = client.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=10.0)
        if not future.done():
            raise RuntimeError(f'Service timed out: {client.srv_name}')
        if future.exception() is not None:
            raise RuntimeError(f'Service failed: {future.exception()}')
        return future.result()

    def existing_objects(self):
        request = GetPlanningScene.Request()
        request.components.components = PlanningSceneComponents.WORLD_OBJECT_NAMES
        result = self.call(self.get_client, request)
        return {obj.id for obj in result.scene.world.collision_objects}

    def apply(self, objects):
        # Send a diff: do not replace the rest of the planning scene.
        scene = PlanningScene()
        scene.is_diff = True
        scene.world.collision_objects = objects
        request = ApplyPlanningScene.Request()
        request.scene = scene
        if not self.call(self.apply_client, request).success:
            raise RuntimeError('MoveIt rejected the planning scene update')

    def add_objects(self):
        table = CollisionObject()
        table.header.frame_id = 'base_link'
        table.id = TABLE_ID
        box = SolidPrimitive()
        box.type = SolidPrimitive.BOX
        box.dimensions = [1.0, 1.0, 0.05]
        table_pose = Pose()
        table_pose.position.z = -0.025
        table_pose.orientation.w = 1.0
        table.primitives.append(box)
        table.primitive_poses.append(table_pose)
        table.operation = CollisionObject.ADD

        cylinder = CollisionObject()
        cylinder.header.frame_id = 'base_link'
        cylinder.id = CYLINDER_ID
        shape = SolidPrimitive()
        shape.type = SolidPrimitive.CYLINDER
        # Cylinder dimensions are [height, radius] in metres.
        shape.dimensions = [0.50, 0.035]
        cylinder_pose = Pose()
        # Trial position closer to home_start than to approach_handshake.
        # Validate both endpoint configurations against the cylinder in RViz.
        cylinder_pose.position.x = 0.05
        cylinder_pose.position.y = 0.39
        cylinder_pose.position.z = 0.25
        cylinder_pose.orientation.w = 1.0
        cylinder.primitives.append(shape)
        cylinder.primitive_poses.append(cylinder_pose)
        cylinder.operation = CollisionObject.ADD
        self.apply([table, cylinder])

    def remove_objects(self):
        objects = []
        for object_id in OBJECT_IDS:
            obj = CollisionObject()
            obj.header.frame_id = 'base_link'
            obj.id = object_id
            obj.operation = CollisionObject.REMOVE
            objects.append(obj)
        self.apply(objects)


def main(args=None):
    # Leave ROS running on Ctrl+C until the scene removal is acknowledged.
    rclpy.init(args=args, signal_handler_options=SignalHandlerOptions.NO)
    stopped = False

    def stop(_signum, _frame):
        nonlocal stopped
        stopped = True

    old_int = signal.signal(signal.SIGINT, stop)
    old_term = signal.signal(signal.SIGTERM, stop)
    node = None
    owns_objects = False
    failed = False
    try:
        node = TestScene()
        if node.get_parameter('remove_only').value:
            node.remove_objects()
            node.get_logger().info('Removed the gesture test objects, if present.')
        else:
            conflicts = node.existing_objects().intersection((*OBJECT_IDS, OTHER_TABLE_ID))
            if conflicts:
                raise RuntimeError(f'Test objects already exist: {sorted(conflicts)}')
            # A timed-out add may still have succeeded, so always try cleanup.
            owns_objects = True
            node.add_objects()
            node.get_logger().info('Table and cylinder added. Press Ctrl+C to remove them.')
            while rclpy.ok() and not stopped:
                rclpy.spin_once(node, timeout_sec=0.2)
    except Exception as exc:
        failed = True
        if node:
            node.get_logger().error(str(exc))
        else:
            print(f'Test scene failed: {exc}')
    finally:
        if node and owns_objects:
            try:
                node.remove_objects()
                node.get_logger().info('Removed the gesture test objects.')
            except Exception as exc:
                failed = True
                node.get_logger().error(f'Could not remove test objects: {exc}')
        if node:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
        signal.signal(signal.SIGINT, old_int)
        signal.signal(signal.SIGTERM, old_term)
    if failed:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
