#!/bin/bash
# Runs the pepper_ros_node.py inside the already-running ROS container.
# Run from the project root: ./docker/start_pepper_node.sh
# Requires start_ros.sh to be running first.

API_SERVER=${1:-http://host.docker.internal:5000}

echo "==> Attaching Pepper ROS node to hri-ros container (API server: $API_SERVER)"
docker exec -it hri-ros bash -c "
    source /opt/ros/noetic/setup.bash && \
    pip3 install requests --quiet && \
    python3 /workspace/pepper_ros_node.py --server $API_SERVER
"
