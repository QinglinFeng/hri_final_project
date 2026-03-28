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

import requests
import rospy
import actionlib
from naoqi_bridge_msgs.msg import SpeechWithFeedbackAction, SpeechWithFeedbackGoal
from sensor_msgs.msg import CompressedImage
from std_msgs.msg import String

SERVER_URL = "http://localhost:5000"


class PepperNode(object):
    """ROS node that connects Pepper to the HRI experiment API server."""

    def __init__(self, server_url):
        rospy.init_node("pepper_hri_node", anonymous=False)
        self._server_url = server_url
        self._latest_image_msg = None

        # ── Subscribe to Pepper's front camera ────────────────────────────
        # naoqi_driver publishes compressed images by default
        rospy.Subscriber(
            "/naoqi_driver/camera/front/image_raw/compressed",
            CompressedImage,
            self._on_image,
            queue_size=1,
        )

        # ── TTS action client ──────────────────────────────────────────────
        self._tts_client = actionlib.SimpleActionClient(
            "/naoqi_driver/speech",
            SpeechWithFeedbackAction,
        )
        rospy.loginfo("Waiting for TTS action server...")
        self._tts_client.wait_for_server(timeout=rospy.Duration(10.0))
        rospy.loginfo("TTS action server ready.")

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

        # CompressedImage.data is already bytes
        image_b64 = base64.b64encode(bytes(self._latest_image_msg.data)).decode("utf-8")
        # Format is e.g. "jpeg" from "image/jpeg"
        fmt = self._latest_image_msg.format.split("/")[-1].strip()

        try:
            resp = requests.post(
                self._server_url + "/perceive",
                json={"image": image_b64, "extension": fmt},
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
        """Send text to Pepper's TTS via the action server."""
        goal = SpeechWithFeedbackGoal()
        goal.say = text
        self._tts_client.send_goal(goal)
        self._tts_client.wait_for_result(timeout=rospy.Duration(15.0))
        rospy.loginfo("Pepper said: %s", text)

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
