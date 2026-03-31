#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ROS 1 node for Pepper robot integration.

Runs on the laptop alongside the ROS master. Bridges between:
  - Pepper's camera (via naoqi_driver) and the API server /perceive endpoint
  - The API server /turn endpoint and Pepper's TTS (via naoqi_driver)

Prerequisites:
  - ROS 1 Noetic (or Melodic) with naoqi_driver installed
  - naoqi_driver connected to Pepper:
      roslaunch naoqi_driver naoqi_driver.launch nao_ip:=<PEPPER_IP>
  - API server running:
      source .venv/bin/activate && python -m hri_final_project.api_server --subject <id>

Usage:
    source /opt/ros/noetic/setup.bash
    python pepper_ros_node.py --server http://192.168.1.42:5000
"""

import argparse
import base64
import struct
import zlib

import requests
import rospy
from sensor_msgs.msg import Image
from std_msgs.msg import String


def _encode_png(width, height, rgb_data):
    """Encode raw RGB bytes as a PNG (stdlib only, no Pillow needed)."""

    def chunk(tag, data):
        c = tag + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    ihdr = chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    raw = b"".join(b"\x00" + rgb_data[y * width * 3:(y + 1) * width * 3] for y in range(height))
    idat = chunk(b"IDAT", zlib.compress(raw))
    iend = chunk(b"IEND", b"")
    return b"\x89PNG\r\n\x1a\n" + ihdr + idat + iend

SERVER_URL = "http://localhost:5000"


class PepperNode(object):
    """ROS node that connects Pepper to the HRI experiment API server."""

    def __init__(self, server_url):
        rospy.init_node("pepper_hri_node", anonymous=False)
        self._server_url = server_url
        self._latest_image_msg = None

        # ── Subscribe to Pepper's front camera ────────────────────────────
        # naoqi_driver publishes uncompressed rgb8 images
        rospy.Subscriber(
            "/naoqi_driver/camera/front/image_raw",
            Image,
            self._on_image,
            queue_size=1,
        )

        # ── TTS publisher (simple String topic) ───────────────────────────
        self._speech_pub = rospy.Publisher(
            "/speech",
            String,
            queue_size=5,
        )
        rospy.sleep(0.5)  # let publisher register

        # ── Animation/gesture publisher ────────────────────────────────────
        # Publishes a tag name to trigger Pepper's built-in tagged animations.
        # Common tags: "question", "thinking", "nod", "happy", "explain"
        self._gesture_pub = rospy.Publisher(
            "/naoqi_driver/animation_player/run_tag",
            String,
            queue_size=5,
        )

        rospy.loginfo("Pepper HRI node started. API server: %s", self._server_url)

    def _on_image(self, msg):
        """Cache the latest camera image."""
        self._latest_image_msg = msg

    def _capture_and_perceive(self):
        """Send the latest camera image to /perceive and return the response."""
        if self._latest_image_msg is None:
            rospy.logwarn("No camera image received yet.")
            return None

        msg = self._latest_image_msg
        rgb = bytes(msg.data)
        # naoqi_driver publishes rgb8; convert bgr8 if needed
        if msg.encoding == "bgr8":
            arr = bytearray(rgb)
            for i in range(0, len(arr), 3):
                arr[i], arr[i + 2] = arr[i + 2], arr[i]
            rgb = bytes(arr)

        png_bytes = _encode_png(msg.width, msg.height, rgb)
        image_b64 = base64.b64encode(png_bytes).decode("utf-8")

        try:
            resp = requests.post(
                self._server_url + "/perceive",
                json={"image": image_b64, "extension": "png"},
                timeout=15,
            )
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            rospy.logerr("Perception request failed: %s", e)
            return None

    def _send_turn(self, utterance):
        """Send teacher utterance to /turn and return robot response text."""
        try:
            resp = requests.post(
                self._server_url + "/turn",
                json={"utterance": utterance},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", ""), data.get("session_active", True)
        except requests.RequestException as e:
            rospy.logerr("Turn request failed: %s", e)
            return "", True

    def _gesture(self, tag):
        """Trigger a Pepper built-in animation by tag name.

        Useful tags:
          "question"  — head tilt + hand raise (used when querying)
          "thinking"  — hand on chin (used while processing)
          "nod"       — head nod (used when acknowledging a label)
          "happy"     — arms up briefly (used at session end)
        """
        rospy.sleep(0.1)  # let TTS start before gesture
        self._gesture_pub.publish(String(data=tag))

    def _speak(self, text):
        """Send text to Pepper's TTS via the /speech topic."""
        self._speech_pub.publish(String(data=text))
        rospy.loginfo("Pepper said: %s", text)
        # Wait roughly for speech to finish (avg ~120 words/min)
        word_count = len(text.split())
        rospy.sleep(max(1.5, word_count * 0.5))

    def run(self):
        """Main interaction loop."""
        rospy.loginfo("Starting experiment loop. Press Ctrl+C to quit.")

        while not rospy.is_shutdown():
            # ── Step 1: capture and perceive the current object ───────────
            input("\n[Press ENTER when the object is in view]")
            perceived = self._capture_and_perceive()
            if perceived is None:
                rospy.logwarn("Perception failed. Try again.")
                continue

            print(
                "[Perceived]  top: {color_top}, {shape_top}, {size_top}"
                "  |  bottom: {color_bottom}, {shape_bottom}, {size_bottom}".format(
                    **perceived
                )
            )

            # ── Step 1b: optional perception correction ────────────────────
            correction = input(
                "Correct? ENTER=accept  or  <color> <shape> <size> / <color> <shape> <size>: "
            ).strip()
            if correction:
                parts = [p.strip().split() for p in correction.split("/")]
                # Also accept 6 space-separated tokens with no slash
                if "/" not in correction:
                    tokens = correction.split()
                    if len(tokens) == 6:
                        correction = " ".join(tokens[:3]) + " / " + " ".join(tokens[3:])
                        parts = [p.strip().split() for p in correction.split("/")]
                if len(parts) == 2 and len(parts[0]) == 3 and len(parts[1]) == 3:
                    fix = {
                        "color_top": parts[0][0], "shape_top": parts[0][1],
                        "size_top": parts[0][2],
                        "color_bottom": parts[1][0], "shape_bottom": parts[1][1],
                        "size_bottom": parts[1][2],
                    }
                    try:
                        resp = requests.post(
                            self._server_url + "/correct", json=fix, timeout=5
                        )
                        resp.raise_for_status()
                        perceived = resp.json()
                        print(
                            "[Corrected]  top: {color_top}, {shape_top}, {size_top}"
                            "  |  bottom: {color_bottom}, {shape_bottom},"
                            " {size_bottom}".format(**perceived)
                        )
                    except requests.RequestException as e:
                        rospy.logerr("Correction request failed: %s", e)
                else:
                    print("[Warning] Invalid format — keeping original perception.")

            # ── Step 2: experimenter types the teacher's utterance ─────────
            utterance = input("Teacher says: ").strip()
            if not utterance:
                continue

            # ── Step 3: get robot response from API server ─────────────────
            self._gesture("thinking")
            response_text, session_active = self._send_turn(utterance)
            if not response_text:
                continue

            # ── Step 4: Pepper gestures + speaks the response ─────────────
            if "replace" in response_text.lower():
                # Robot is asking a query
                self._gesture("question")
            elif "thank you" in response_text.lower() and not session_active:
                # End of session
                self._gesture("happy")
            else:
                # Acknowledgement or answer
                self._gesture("nod")

            self._speak(response_text)

            if not session_active:
                rospy.loginfo("Session ended. Moving to next session.")


def main():
    parser = argparse.ArgumentParser(description="Pepper ROS 1 node for HRI experiment")
    parser.add_argument(
        "--server",
        default="http://localhost:5000",
        help="API server URL (default: http://localhost:5000)",
    )
    # rospy uses remapping args; strip them before parsing
    args, _ = parser.parse_known_args()

    global SERVER_URL
    SERVER_URL = args.server

    node = PepperNode(server_url=args.server)
    node.run()


if __name__ == "__main__":
    main()
