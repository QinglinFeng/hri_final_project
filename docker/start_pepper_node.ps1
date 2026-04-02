# Runs the pepper_ros_node.py inside the already-running ROS container.
# Run from the project root: .\docker\start_pepper_node.ps1
# Requires start_ros.ps1 to be running first.

param(
    [string]$ApiServer = "http://host.docker.internal:5000"
)

Write-Host "==> Attaching Pepper ROS node to hri-ros container (API server: $ApiServer)"
docker exec -it hri-ros bash -c "source /opt/ros/noetic/setup.bash && pip3 install requests --quiet && python3 /workspace/pepper_ros_node.py --server $ApiServer"
