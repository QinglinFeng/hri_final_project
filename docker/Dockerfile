FROM --platform=linux/amd64 ros:noetic

# Install naoqi_driver dependencies and Python packages
RUN apt-get update && apt-get install -y \
    ros-noetic-naoqi-driver \
    ros-noetic-naoqi-bridge-msgs \
    python3-pip \
    python3-requests \
    && rm -rf /var/lib/apt/lists/*

# Source ROS automatically in every shell
RUN echo "source /opt/ros/noetic/setup.bash" >> /root/.bashrc

CMD ["bash"]
