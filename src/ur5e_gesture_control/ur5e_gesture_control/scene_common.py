"""Independent, temporary planning-scene objects."""
import signal
import rclpy
from moveit_msgs.msg import CollisionObject, ObjectColor, PlanningScene, PlanningSceneComponents
from moveit_msgs.srv import ApplyPlanningScene, GetPlanningScene
from rclpy.node import Node
from rclpy.signals import SignalHandlerOptions


class SceneNode(Node):
    def __init__(self, name):
        super().__init__(name)
        self.declare_parameter('remove_only', False)
        self.apply_client = self.create_client(ApplyPlanningScene, '/apply_planning_scene')
        self.get_client = self.create_client(GetPlanningScene, '/get_planning_scene')

    def call(self, client, request):
        if not client.wait_for_service(timeout_sec=10.0):
            raise RuntimeError(f'Service unavailable: {client.srv_name}')
        future = client.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=10.0)
        if not future.done() or future.exception() is not None:
            raise RuntimeError(f'Service failed or timed out: {client.srv_name}')
        return future.result()

    def existing(self):
        request = GetPlanningScene.Request()
        request.components.components = PlanningSceneComponents.WORLD_OBJECT_NAMES
        return {o.id for o in self.call(self.get_client, request).scene.world.collision_objects}

    def apply(self, obj, rgba=None):
        scene = PlanningScene()
        scene.is_diff = True
        scene.world.collision_objects.append(obj)
        if rgba is not None:
            color = ObjectColor()
            color.id = obj.id
            color.color.r, color.color.g, color.color.b, color.color.a = rgba
            scene.object_colors.append(color)
        request = ApplyPlanningScene.Request()
        request.scene = scene
        if not self.call(self.apply_client, request).success:
            raise RuntimeError('MoveIt rejected the scene update')

    def remove(self, object_id):
        obj = CollisionObject()
        obj.id = object_id
        obj.header.frame_id = 'base_link'
        obj.operation = CollisionObject.REMOVE
        self.apply(obj)


def run_scene(node_class, object_id, conflicts, rgba, args=None):
    rclpy.init(args=args, signal_handler_options=SignalHandlerOptions.NO)
    stopped = False

    def stop(_signum, _frame):
        nonlocal stopped
        stopped = True

    old_int = signal.signal(signal.SIGINT, stop)
    old_term = signal.signal(signal.SIGTERM, stop)
    node = None
    owns_object = False
    failed = False
    try:
        node = node_class()
        if node.get_parameter('remove_only').value:
            node.remove(object_id)
            node.get_logger().info(f'Removed {object_id}, if present.')
        else:
            found = node.existing().intersection(conflicts)
            if found:
                raise RuntimeError(f'Conflicting scene objects: {sorted(found)}')
            obj = node.make_object()
            owns_object = True
            node.apply(obj, rgba)
            node.get_logger().info(f'Added {object_id}. Press Ctrl+C to remove it.')
            while rclpy.ok() and not stopped:
                rclpy.spin_once(node, timeout_sec=0.2)
    except Exception as exc:
        failed = True
        if node:
            node.get_logger().error(str(exc))
        else:
            print(f'Scene error: {exc}')
    finally:
        if node and owns_object:
            try:
                node.remove(object_id)
                node.get_logger().info(f'Removed {object_id}.')
            except Exception as exc:
                failed = True
                node.get_logger().error(f'Could not remove {object_id}: {exc}')
        if node:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
        signal.signal(signal.SIGINT, old_int)
        signal.signal(signal.SIGTERM, old_term)
    if failed:
        raise SystemExit(1)
