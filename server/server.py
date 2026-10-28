import asyncio
import json

from websockets.asyncio.server import serve

PORT = 8765

XR_ORIGIN = (0.0, 0.0, 0.0)

def to_robot(pose):
    x, y, z = pose["position"]
    qx, qy, qz, qw = pose["orientation"]
    position = (-z + XR_ORIGIN[0], -x + XR_ORIGIN[1], y + XR_ORIGIN[2])
    return position, (-qz, -qx, qy, qw)

def to_xr(position, orientation):
    x, y, z = (p - o for p, o in zip(position, XR_ORIGIN))
    qx, qy, qz, qw = orientation
    return {"position": [-y, z, -x], "orientation": [-qy, qz, -qx, qw]}

class Arm:
    def move_camera_to(self, position, orientation):
        # TODO: clamp to the reachable workspace, solve IK, send to the arm controller with speed limits
        self.target = position, orientation

    def stop(self):
        # TODO: hold the current position
        pass

    def camera_pose(self):
        # TODO: forward kinematics from joint encoders, or ZED SDK positional tracking
        return self.target


async def handle(ws, arm):
    try:
        async for message in ws:
            arm.move_camera_to(*to_robot(json.loads(message)))
            await ws.send(json.dumps(to_xr(*arm.camera_pose())))
    finally:
        arm.stop()


async def main():
    arm = Arm()
    async with serve(lambda ws: handle(ws, arm), "0.0.0.0", PORT) as server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
