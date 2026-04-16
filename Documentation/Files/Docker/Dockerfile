FROM osrf/ros:humble-desktop-full

# Fix expired ROS 2 GPG key (avoid GPG errors in apt)
RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
    -o /usr/share/keyrings/ros2-latest-archive-keyring.gpg

# Extra packages: graphics + tools + ROS 2 add-ons
RUN apt-get update && apt-get install -y --no-install-recommends \
    # X11 graphical support
    x11-apps \
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    libglu1-mesa \
    mesa-utils \
    libqt5x11extras5 \
    libxkbcommon-x11-0 \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxtst6 \
    \
    # Dev tools
    build-essential \
    cmake \
    python3-colcon-common-extensions \
    python3-pip \
    python3-rosdep \
    unzip \
    git \
    iputils-ping \
    \
    # ROS 2 add-ons
    ros-humble-rviz2 \
    ros-humble-joint-state-publisher \
    ros-humble-joint-state-publisher-gui \
    ros-humble-gazebo-ros-pkgs \
    ros-humble-gazebo-plugins \
    ros-humble-gazebo-ros2-control \
    ros-humble-nav2-bringup \
    ros-humble-nav2-simple-commander \
    ros-humble-tf-transformations \
    ros-humble-cartographer-ros \
    ros-humble-teleop-twist-keyboard \
    ros-humble-rmw-cyclonedds-cpp \
    ros-humble-rosbridge-server \
    \
    # Gazebo Classic (Gazebo 11)
    gazebo \
    libgazebo-dev \
    \
    # MoveIt 2
    ros-humble-moveit \
    ros-humble-moveit-visual-tools \
    ros-humble-moveit-servo \
    \
    # Universal Robots
    ros-humble-ur-description \
    ros-humble-ur-moveit-config \
    ros-humble-ur-robot-driver \
    \
    # ros2_control core
    ros-humble-ros2-control \
    ros-humble-ros2-controllers \
    \
    && rm -rf /var/lib/apt/lists/*

# rosdep init (safe if already initialized)
RUN rosdep init || true && rosdep update

# Add Microsoft GPG key and VS Code APT repository (no Snap)
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends wget gpg apt-transport-https; \
    \
    wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg; \
    install -D -o root -g root -m 644 microsoft.gpg /usr/share/keyrings/microsoft.gpg; \
    rm -f microsoft.gpg; \
    \
    printf "Types: deb\nURIs: https://packages.microsoft.com/repos/code\nSuites: stable\nComponents: main\nArchitectures: amd64\nSigned-By: /usr/share/keyrings/microsoft.gpg\n" \
      > /etc/apt/sources.list.d/vscode.sources; \
    \
    apt-get update; \
    apt-get install -y --no-install-recommends code; \
    rm -rf /var/lib/apt/lists/*
# Orbbec Gemini 2 camera support (ROS 2 Humble binary driver)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-humble-orbbec-camera \
    ros-humble-orbbec-description \
    ros-humble-image-transport \
    ros-humble-image-transport-plugins \
    ros-humble-compressed-image-transport \
    ros-humble-camera-info-manager \
    ros-humble-image-publisher \
    ros-humble-diagnostic-updater \
    ros-humble-diagnostic-msgs \
    ros-humble-statistics-msgs \
    ros-humble-xacro \
    ros-humble-backward-ros \
    libgflags-dev \
    libgoogle-glog-dev \
    nlohmann-json3-dev \
    libdw-dev \
    libssl-dev \
    libusb-1.0-0-dev \
    mesa-utils \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Intel RealSense D435/D435i camera support (ROS 2 Humble)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-humble-realsense2-camera \
    ros-humble-realsense2-description \
    ros-humble-image-transport \
    ros-humble-camera-info-manager \
    ros-humble-diagnostic-updater \
    git \
    cmake \
    build-essential \
    pkg-config \
    libssl-dev \
    libusb-1.0-0-dev \
    libudev-dev \
    libgtk-3-dev \
    libglfw3-dev \
    libgl1-mesa-dev \
    libglu1-mesa-dev \
    ca-certificates \
    usbutils \
    v4l-utils \
    && rm -rf /var/lib/apt/lists/*

# Build librealsense from source with RSUSB backend
RUN mkdir -p /opt/realsense-src && \
    cd /opt/realsense-src && \
    git clone https://github.com/IntelRealSense/librealsense.git && \
    cd librealsense && \
    ./scripts/setup_udev_rules.sh && \
    mkdir build && cd build && \
    cmake .. \
      -DCMAKE_BUILD_TYPE=Release \
      -DFORCE_RSUSB_BACKEND=ON \
      -DBUILD_EXAMPLES=true \
      -DBUILD_GRAPHICAL_EXAMPLES=false && \
    make -j"$(nproc)" && \
    make install && \
    ldconfig && \
    cd / && rm -rf /opt/realsense-src
    
# Default ROS 2 environment in bashrc (+ optional /ws overlay if mounted)
RUN echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc 
    
CMD ["bash"]
