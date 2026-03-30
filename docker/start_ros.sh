#!/bin/bash
# Builds the Docker image (first time only) and starts the ROS container.
# Run from the project root: ./docker/start_ros.sh <PEPPER_IP>

PEPPER_IP=${1:-128.237.235.109}
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
IMAGE_NAME="hri-ros-noetic"

echo "==> Building Docker image (only needed once)..."
docker build --platform linux/amd64 -t "$IMAGE_NAME" "$PROJECT_DIR/docker/"

echo "==> Starting ROS container with Pepper IP: $PEPPER_IP"
docker run -it --rm \
    --platform linux/amd64 \
    --name hri-ros \
    --network host \
    -v "$PROJECT_DIR:/workspace" \
    -v "$PROJECT_DIR/docker/boot_config.json:/opt/ros/noetic/share/naoqi_driver/share/boot_config.json:ro" \
    -e PEPPER_IP="$PEPPER_IP" \
    "$IMAGE_NAME" \
    bash -c "
        source /opt/ros/noetic/setup.bash && \
        echo '==> Starting roscore...' && \
        roscore &
        sleep 3 && \
        echo '==> Starting camera keepalive subscriber...' && \
        python3 /workspace/docker/camera_keepalive.py &
        sleep 1 && \
        echo '==> Launching naoqi_driver...' && \
        roslaunch naoqi_driver naoqi_driver.launch nao_ip:=$PEPPER_IP
    "
