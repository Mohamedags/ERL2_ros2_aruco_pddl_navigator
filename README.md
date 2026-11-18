# ERL2: ROS 2 ArUco Marker Mission with PlanSys2 and Nav2

An autonomous ROS 2 mission for the Experimental Robotics Laboratory course (Assignment 2). A mobile robot explores a set of waypoints, detects ArUco markers with OpenCV, records them in the PlanSys2 knowledge base, and then generates a second PDDL plan that visits the markers in ascending ID order and visually servos onto each one.

## Project Overview

The mission runs in two phases, coordinated by a central controller node.

1. **Phase 1: Exploration**
   * The robot navigates to the predefined waypoints `wp1` through `wp4`.
   * At each waypoint it executes a **search** action: a 360° rotation while scanning for ArUco markers.
   * The camera's clipping range is limited to 8 m so that markers at other waypoints are not detected from the current one.
   * Each detected marker is written into the PlanSys2 knowledge base as a PDDL predicate, `(marker_at id wp)`.

2. **Phase 2: Ordered Processing**
   * When exploration is complete, the controller retrieves all detected markers.
   * It sorts them by ID, lowest to highest.
   * It builds a new PDDL problem with a `(next_id ?prev ?curr)` chain that enforces this order, and generates a new plan.
   * For each marker, the robot navigates to its waypoint and runs **visual servoing** until the marker is centered in the camera frame.

## Tech Stack

* **ROS 2** (Jazzy or Humble)
* **PlanSys2**: PDDL-based high-level planning and action dispatching
* **Nav2**: autonomous navigation and path planning
* **Gazebo Harmonic**: simulation
* **OpenCV / ArUco**: marker detection and image processing
* **C++**: action nodes and controller

## Repository Structure

```
ERL2_ros2_aruco_pddl_navigator
├── planner_pkg/                 # plansys_interface: controller, PDDL domain/problem, action nodes
├── robot_model_and_simulation/  # assign2: robot URDF/SDF, Gazebo world, spawn launch files
├── ros2_navigation/             # Nav2 configuration, map, localization and navigation launch files
└── .gitignore
```

## Architecture

### 1. Controller Node (`get_plan_and_execute`)
The high-level coordinator. It initializes the PlanSys2 clients, requests the exploration plan, monitors execution, and switches to the Phase 2 plan once exploration finishes. It does not use the standard PlanSys2 Executor Client, which allows reactive, callback-driven execution.

### 2. Action Nodes
These nodes implement the PDDL actions with `plansys2::ActionExecutorClient`.

* **`move_action_node`**
  * Maps PDDL waypoints (e.g. `wp1`) to map coordinates.
  * Sends goals to Nav2 through the `NavigateToPose` action.
  * Handles navigation failures and uses lazy initialization.

* **`search_waypoint_node`**
  * Rotates the robot through `cmd_vel` to scan the area.
  * Detects ArUco markers with OpenCV.
  * Updates the PDDL problem instance with `(marker_at id wp)` on each detection.
  * Shows a live camera feed with detection overlays.

* **`process_action_node`**
  * Requires the robot to be at the correct waypoint, enforced by the PDDL preconditions.
  * Uses a proportional controller (visual servoing) to rotate the robot until the marker is centered.
  * Holds the target (green circle) for 5 seconds before completing the action.

## PDDL Domain

The domain defines three durative actions:

1. **`move`**: moves the robot between waypoints.
2. **`search_waypoint`**: rotates in place to find markers at the current waypoint.
3. **`process_marker`**: centers the camera on a marker. Processing order is enforced by the `(next_id ?prev ?curr)` chain that the controller generates at runtime.

## Installation & Build

### Prerequisites

Install ROS 2, PlanSys2, Nav2, and OpenCV:

```bash
sudo apt install ros-$ROS_DISTRO-plansys2-*
sudo apt install ros-$ROS_DISTRO-nav2-*
sudo apt install ros-$ROS_DISTRO-opencv-*
```

### Clone and Build

```bash
mkdir -p ros2_ws/src
cd ros2_ws/src
git clone https://github.com/Mohamedags/ERL2_ros2_aruco_pddl_navigator.git
cd ..
colcon build
source install/setup.bash
```

## Usage

Each step runs in its own terminal. Wait for each stage to finish starting before launching the next one.

**1. Simulation and robot (terminal 1)**

```bash
ros2 launch assign2 spawn_robot.launch.py
```

Wait a few seconds. The RViz configuration uses `map` as its fixed frame, which is not available until localization is running.

**2. Localization (terminal 2)**

```bash
ros2 launch ros2_navigation localization.launch.py
```

Wait until the map has loaded.

**3. Navigation (terminal 3)**

```bash
ros2 launch ros2_navigation navigation.launch.py
```

**4. PlanSys2 action nodes (terminal 4)**

Start this once the Nav2 action server is up.

```bash
ros2 launch plansys_interface distributed_actions_3.launch.py
```

**5. Mission controller (terminal 5)**

```bash
ros2 run plansys_interface get_plan_and_execute
```

## Expected Behavior

1. The robot visits `wp1` to `wp4` and scans at each one. Detected markers appear in the camera overlay.
2. Once exploration ends, the controller logs the detected markers and the Phase 2 plan.
3. The robot visits the markers in ascending ID order and centers on each one for 5 seconds.


## Authors

- AGUENAROUS Mohamed
