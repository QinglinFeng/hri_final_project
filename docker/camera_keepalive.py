#!/usr/bin/env python3
"""Subscribe to Pepper's front camera and keep the latest frame available.

Saves the most recent frame to /workspace/latest_frame.jpg on every update. Run this
before naoqi_driver so the converter never enters idle/reset state.
"""

import rospy  # pylint: disable=import-error
from sensor_msgs.msg import Image  # pylint: disable=import-error

SAVE_PATH = "/workspace/latest_frame.ppm"
_frame_count = 0


def callback(msg: Image) -> None:  # pylint: disable=missing-function-docstring
    global _frame_count  # pylint: disable=global-statement
    # Save as PPM (no extra libraries needed)
    with open(SAVE_PATH, "wb") as f:
        f.write(f"P6\n{msg.width} {msg.height}\n255\n".encode())
        data = bytearray(msg.data)
        if msg.encoding == "bgr8":
            for i in range(0, len(data), 3):
                data[i], data[i + 2] = data[i + 2], data[i]
        f.write(bytes(data))
    _frame_count += 1
    if _frame_count == 1:
        rospy.loginfo(
            "[camera_keepalive] First frame received (%dx%d) — camera is live!",
            msg.width,
            msg.height,
        )
    elif _frame_count % 50 == 0:
        rospy.loginfo("[camera_keepalive] %d frames received", _frame_count)


rospy.init_node("camera_keepalive", anonymous=True)
rospy.Subscriber(
    "/naoqi_driver/camera/front/image_raw",
    Image,
    callback,
    queue_size=1,
)
rospy.loginfo("[camera_keepalive] Waiting for camera frames...")
rospy.spin()
