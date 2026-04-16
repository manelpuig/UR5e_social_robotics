## UB custom Docker-based ROS2 Humble UR5eenvironment

We have designed a University of Barcelona custom Docker-based ROS 2 Humble environment to simplify student access to ROS 2 and ensure platform-independent workflows in robotics courses.


**PC-ubuntu/linux** Configure properly the `docker-compose.yaml`

- Open a terminal in `~/UR5e_social_robotics/Documentation/Files/Docker` and run:
    ````bash
    xhost +local:root            # only in case of Host Ubuntu to allow X11 for Docker 
    docker compose up
    ````
**PC-windows** Configure properly the `docker-compose.yaml`

- Open a terminal in `~/UR5e_social_robotics/Documentation/Files/Docker` and run:
    ````bash
    docker compose up
    ````

- In Host VScode you can `attach VScode`. You can also connect with container typing:
    ```bash
    docker exec -it pc_humble bash
    code .  # to open VSCode inside the container
    ```
- Clone your ws in `/root/`
- Verify in container **.bashrc** to have:
    ```bash
    source /opt/ros/humble/setup.bash
    source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash
    source /root/UR5e_social_robotics/install/setup.bash
    cd /root/UR5e_social_robotics
    ```
You are ready to work inside the container and to connect to the robot hardware within ROS2 Humble on Docker!

- To stop the container, open a new terminal on Host in `~/UR5e_social_robotics/Documentation/Files/Docker` and run:
    ```bash
    docker compose down
    ```
- To see the Images and Containers:
    ```bash
    docker ps -a               # containers
    docker images              # images
    ```
- To modify the `Dockerfile`, build and push to Docker Hub, you can follow the instructions:
    ```bash
    docker build -t manelpuig/ros2-humble-ub-ur5e:latest .
    docker login
    docker push manelpuig/ros2-humble-ub-ur5e:latest
    ```
- Note that:
    - Dockerfile0: Base installation without 3D cameras
    - Dockerfile: Full installation with ORBBEC and Intel Realsense 3D Cameras

# 3D cameras

You will have to install Udev rules on Host once:
- Realsense D435
````bash
cd /tmp
wget https://raw.githubusercontent.com/IntelRealSense/librealsense/master/config/99-realsense-libusb.rules
sudo cp 99-realsense-libusb.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
````
- Orbbec Gemini2
````bash
git clone https://github.com/orbbec/OrbbecSDK_ROS2.git
cd OrbbecSDK_ROS2
sudo bash scripts/install_udev_rules.sh
````