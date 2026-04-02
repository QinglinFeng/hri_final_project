# Builds the Docker image (first time only) and starts the ROS container.
# Run from the project root: .\docker\start_ros.ps1 <PEPPER_IP>

param(
    [string]$PepperIP = "128.237.235.109"
)

$ImageName = "hri-ros-noetic"
$ProjectDir = Split-Path -Parent $PSScriptRoot

Write-Host "==> Building Docker image (only needed once)..."
docker build --platform linux/amd64 -t $ImageName "$ProjectDir\docker"

Write-Host "==> Starting ROS container with Pepper IP: $PepperIP"
docker run -it --rm `
    --platform linux/amd64 `
    --name hri-ros `
    --add-host=host.docker.internal:host-gateway `
    -p 11311:11311 `
    -v "${ProjectDir}:/workspace" `
    -v "${ProjectDir}/docker/boot_config.json:/opt/ros/noetic/share/naoqi_driver/share/boot_config.json:ro" `
    -e PEPPER_IP="$PepperIP" `
    $ImageName `
    bash -c "source /opt/ros/noetic/setup.bash && echo '==> Starting roscore...' && roscore & sleep 3 && echo '==> Starting camera keepalive subscriber...' && python3 /workspace/docker/camera_keepalive.py & sleep 1 && echo '==> Launching naoqi_driver...' && roslaunch naoqi_driver naoqi_driver.launch nao_ip:=$PepperIP"
