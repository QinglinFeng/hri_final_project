#!/usr/bin/env python3
"""Simple keyboard teleop for Pepper using stdin (no X display needed)."""
import sys
import tty
import termios
import rospy
from geometry_msgs.msg import Twist

SPEED = 0.3
TURN = 0.5

HELP = """
Pepper Teleop
---------------------------
   u    i    o
   j    k    l
   m    ,    .

i/,  : forward/backward
j/l  : turn left/right
u/o  : move diagonally
k    : stop
q    : quit
"""

BINDINGS = {
    "i": (1, 0),
    ",": (-1, 0),
    "j": (0, 1),
    "l": (0, -1),
    "u": (1, 1),
    "o": (1, -1),
    "m": (-1, 1),
    ".": (-1, -1),
    "k": (0, 0),
}


def get_key(fd: int) -> str:
    return sys.stdin.read(1)


def main() -> None:
    rospy.init_node("teleop_simple", anonymous=True)
    pub = rospy.Publisher("/cmd_vel", Twist, queue_size=1)

    print(HELP)

    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        while True:
            key = get_key(fd)
            if key == "q":
                break
            twist = Twist()
            if key in BINDINGS:
                lin, ang = BINDINGS[key]
                twist.linear.x = lin * SPEED
                twist.angular.z = ang * TURN
            pub.publish(twist)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
        # Send stop on exit
        pub.publish(Twist())
        print("\nStopped.")


if __name__ == "__main__":
    main()
