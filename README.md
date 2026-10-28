# raspicat_slam_navigation
Raspberry Pi CatでSLAMやナビゲーションを行うためのROS 2パッケージです。

## Requirements
- Raspberry Pi Cat
  - Raspberry Pi
    - Raspberry Pi 4 Model B
  - Linux OS
    - [Ubuntu Server 22.04](https://ubuntu.com/download/raspberry-pi)
  - Device Driver
    - [rt-net/RaspberryPiMouse](https://github.com/rt-net/RaspberryPiMouse)
  - ROS 2
    - [Humble Hawksbill](https://docs.ros.org/en/humble/Installation.html)

- Remote PC
  - Linux OS
    - [Ubuntu Desktop 22.04](https://ubuntu.com/download/desktop)
  - ROS 2
    - [Humble Hawksbill](https://docs.ros.org/en/humble/Installation.html)

## Installation
### Source Build
#### Raspberry Pi 4

```sh
# パッケージのダウンロード
cd ~/catkin_ws/src
git clone -b ros2 https://github.com/rt-net/raspicat_slam_navigation.git
git clone -b ros2 https://github.com/rt-net/raspicat_description.git
git clone -b ros2 https://github.com/rt-net/raspicat_ros.git
git clone -b $ROS_DISTRO-devel https://github.com/rt-net/raspimouse2
```

```sh
# 依存パッケージのインストール
rosdep update
rosdep install -r -y -i --from-paths raspicat* raspimouse*
```

```sh
# ビルド＆インストール
cd ~/catkin_ws
colcon build --symlink-install
source ~/catkin_ws/install/setup.bash
```
#### Remote PC

```sh
# パッケージのダウンロード
cd ~/catkin_ws/src
git clone -b ros2 https://github.com/rt-net/raspicat_slam_navigation.git
git clone -b ros2 https://github.com/rt-net/raspicat_description.git
git clone -b ros2 https://github.com/rt-net/raspicat_ros.git
```

```sh
# 依存パッケージのインストール
rosdep update
rosdep install -r -y -i --from-paths raspicat* raspimouse*
```

```sh
# ビルド＆インストール
cd ~/catkin_ws
colcon build --symlink-install
source ~/catkin_ws/install/setup.bash
```

## Package Overview
### raspicat_slam

SLAMを行うためのパッケージです。

このパッケージでは、以下のROS 2パッケージを使用してSLAMを実行することができます。
* [slam_toolbox](https://github.com/SteveMacenski/slam_toolbox)

### raspicat_navigation

ナビゲーションを行うためのパッケージです。

このパッケージでは、以下のROS 2パッケージを使用してナビゲーションを実行することができます。
* [navigation2](https://github.com/ros-planning/navigation2)

## Usage

> このフォーク（[wadajun8/raspicat_slam_navigation](https://github.com/wadajun8/raspicat_slam_navigation) の `vlm_kidnapping_detect` ブランチ）では、本家の `raspicat_nav2.launch.py` の代わりに用途別の launch ファイルを使います。一覧と引数は [raspicat_navigation/README.md](raspicat_navigation/README.md) を参照してください。

### Simulation
#### SLAM
* Slam Toolbox
```
ros2 launch raspicat_gazebo raspicat_with_iscas_museum.launch.py
ros2 launch raspicat_slam raspicat_slam_toolbox.launch.py
ros2 launch raspicat_bringup teleop.launch.py teleop:=joy
ros2 service call /motor_power std_srvs/SetBool '{data: true}'
```

#### Navigation
* Navigation 2（AMCL 版。emcl2 版は `raspicat_nav2_sim_emcl2.launch.py`）
```
ros2 launch raspicat_gazebo raspicat_with_iscas_museum.launch.py
ros2 launch raspicat_navigation sim_nav2.launch.py
ros2 service call /motor_power std_srvs/SetBool '{data: true}'
```
AMCL 版は、RViz の「2D Pose Estimate」で初期位置を入れるまで Nav2 が active になりません。

### Actual machine
#### SLAM
* Slam Toolbox
##### Raspberry Pi 4
```
ros2 launch raspicat raspicat.launch.py
```
##### Remote PC
```
ros2 launch raspicat_slam raspicat_slam_toolbox.launch.py
ros2 launch raspicat_bringup teleop.launch.py teleop:=joy
ros2 service call /motor_power std_srvs/SetBool '{data: true}'
```

#### Navigation
* Navigation 2
##### Raspberry Pi 4
```
ros2 launch raspicat raspicat.launch.py
```
##### Remote PC
```
ros2 launch raspicat_navigation tsudanuma_2_19.launch.py   # 地図ごとの launch（一覧は raspicat_navigation/README.md）
ros2 service call /motor_power std_srvs/SetBool '{data: true}'
```

## License
(C) 2020-2023 RT Corporation

各ファイルはライセンスがファイル中に明記されている場合、そのライセンスに従います。特に明記されていない場合は、Apache License, Version 2.0に基づき公開されています。  
ライセンスの全文は[LICENSE](./LICENSE)または[https://www.apache.org/licenses/LICENSE-2.0](https://www.apache.org/licenses/LICENSE-2.0)から確認できます。

※このソフトウェアは基本的にオープンソースソフトウェアとして「AS IS」（現状有姿のまま）で提供しています。本ソフトウェアに関する無償サポートはありません。  
バグの修正や誤字脱字の修正に関するリクエストは常に受け付けていますが、それ以外の機能追加等のリクエストについては社内のガイドラインを優先します。
