#!/usr/bin/env python3
"""Quick test: grab one frame from Pepper's front camera via ROS and save it."""

import rospy  # pylint: disable=import-error
from sensor_msgs.msg import Image  # pylint: disable=import-error

rospy.init_node("grab_test", anonymous=True)
print("Waiting for camera frame on /naoqi_driver/camera/front/image_raw ...")
msg = rospy.wait_for_message(
    "/naoqi_driver/camera/front/image_raw",
    Image,
    timeout=10,
)

print(f"Encoding: {msg.encoding}, size: {msg.width}x{msg.height}")

data = bytearray(msg.data)
# Only swap R/B if encoding is bgr8
if msg.encoding == "bgr8":
    for i in range(0, len(data), 3):
        data[i], data[i + 2] = data[i + 2], data[i]

with open("/workspace/test_frame.ppm", "wb") as f:
    f.write(f"P6\n{msg.width} {msg.height}\n255\n".encode())
    f.write(bytes(data))

print("Saved to /workspace/test_frame.ppm")
print("Open it on your Mac with: open test_frame.ppm")
