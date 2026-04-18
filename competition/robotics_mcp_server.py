"""
Robotics MCP Server - Component Database and Recommendation Tools
==================================================================
Session 5: The Challenge - Robotic Chef Platform

This MCP server provides tools for searching robotic components, sensors,
and actuators, as well as recommending complete platforms for specific tasks.
All data is stored inline for self-contained operation.

Originally developed in Session 2 (Robotics Agent), included here as a
self-contained copy so Session 5 works independently.
"""

import json
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Robotics Platform Builder")

# ---------------------------------------------------------------------------
# Inline Component Database
# ---------------------------------------------------------------------------

COMPONENTS = [
    {
        "id": "COMP-001",
        "name": "6-DOF Industrial Robot Arm",
        "category": "robot_arm",
        "description": "Six degree-of-freedom articulated robot arm with 5kg payload capacity. Suitable for pick-and-place, assembly, and precise manipulation tasks.",
        "specifications": {
            "degrees_of_freedom": 6,
            "payload_kg": 5,
            "reach_mm": 850,
            "repeatability_mm": 0.02,
            "max_speed_deg_per_sec": 250,
            "weight_kg": 28,
            "power_watts": 500,
        },
        "suitable_tasks": ["pick and place", "stirring", "pouring", "assembly", "food handling"],
        "price_range": "$$$$",
        "interfaces": ["ROS2", "Modbus TCP", "EtherCAT"],
    },
    {
        "id": "COMP-002",
        "name": "4-DOF SCARA Robot Arm",
        "category": "robot_arm",
        "description": "Four degree-of-freedom SCARA arm optimised for fast, precise horizontal movements. Ideal for pick-and-place and dispensing.",
        "specifications": {
            "degrees_of_freedom": 4,
            "payload_kg": 3,
            "reach_mm": 600,
            "repeatability_mm": 0.01,
            "max_speed_deg_per_sec": 400,
            "weight_kg": 18,
            "power_watts": 300,
        },
        "suitable_tasks": ["pick and place", "dispensing", "packaging", "sorting"],
        "price_range": "$$$",
        "interfaces": ["ROS2", "RS-485", "EtherCAT"],
    },
    {
        "id": "COMP-003",
        "name": "7-DOF Collaborative Robot Arm",
        "category": "robot_arm",
        "description": "Seven degree-of-freedom collaborative robot arm with built-in torque sensors for safe human-robot interaction. Excellent for kitchen environments.",
        "specifications": {
            "degrees_of_freedom": 7,
            "payload_kg": 7,
            "reach_mm": 1000,
            "repeatability_mm": 0.03,
            "max_speed_deg_per_sec": 180,
            "weight_kg": 22,
            "power_watts": 400,
            "collision_detection": True,
            "force_limited": True,
        },
        "suitable_tasks": ["cooking", "food handling", "stirring", "pouring", "human collaboration"],
        "price_range": "$$$$",
        "interfaces": ["ROS2", "gRPC", "REST API"],
    },
    {
        "id": "COMP-004",
        "name": "Compact Mobile Base (Omnidirectional)",
        "category": "mobile_base",
        "description": "Omnidirectional mobile base with mecanum wheels for navigating tight kitchen spaces. Supports up to 50kg payload.",
        "specifications": {
            "drive_type": "mecanum",
            "max_speed_m_per_sec": 1.0,
            "payload_kg": 50,
            "footprint_cm": {"length": 60, "width": 50},
            "battery_hours": 8,
            "weight_kg": 25,
            "charging_time_hours": 2,
        },
        "suitable_tasks": ["kitchen navigation", "transport", "multi-station operation"],
        "price_range": "$$$",
        "interfaces": ["ROS2", "CAN bus"],
    },
    {
        "id": "COMP-005",
        "name": "Stationary Pedestal Mount",
        "category": "mobile_base",
        "description": "Heavy-duty stationary pedestal for fixed workstation deployment. Provides a stable base for robot arms.",
        "specifications": {
            "mount_diameter_mm": 200,
            "height_adjustable": True,
            "height_range_mm": {"min": 700, "max": 1200},
            "max_payload_kg": 80,
            "weight_kg": 35,
            "footprint_cm": {"diameter": 45},
        },
        "suitable_tasks": ["fixed workstation", "cooking station", "food prep station"],
        "price_range": "$$",
        "interfaces": ["standard flange ISO 9409"],
    },
    {
        "id": "COMP-006",
        "name": "Central Processing Controller",
        "category": "controller",
        "description": "Industrial-grade embedded controller with real-time OS, GPU acceleration for vision processing, and multiple I/O interfaces.",
        "specifications": {
            "processor": "ARM Cortex-A78 (8-core)",
            "ram_gb": 16,
            "gpu": "integrated AI accelerator (8 TOPS)",
            "storage_gb": 256,
            "os": "Ubuntu 22.04 RT",
            "io_ports": ["8x USB 3.0", "4x Ethernet", "2x CAN", "16x GPIO"],
            "power_watts": 45,
        },
        "suitable_tasks": ["motion planning", "vision processing", "multi-agent coordination", "real-time control"],
        "price_range": "$$$",
        "interfaces": ["ROS2", "EtherCAT", "CAN bus", "Modbus"],
    },
    {
        "id": "COMP-007",
        "name": "Safety PLC Module",
        "category": "controller",
        "description": "Dedicated safety programmable logic controller for monitoring emergency stops, safety zones, and compliance with food-safety regulations.",
        "specifications": {
            "safety_level": "SIL 3 / PLe",
            "response_time_ms": 5,
            "digital_inputs": 24,
            "digital_outputs": 16,
            "safety_functions": ["emergency stop", "speed monitoring", "zone monitoring", "force limiting"],
            "power_watts": 15,
        },
        "suitable_tasks": ["safety monitoring", "emergency stop", "compliance", "zone control"],
        "price_range": "$$",
        "interfaces": ["PROFIsafe", "CIP Safety", "FSoE"],
    },
    {
        "id": "COMP-008",
        "name": "Aluminium Extrusion Frame (Kitchen Station)",
        "category": "frame",
        "description": "Modular aluminium extrusion frame system designed for building custom kitchen workstations. Food-safe anodised finish.",
        "specifications": {
            "material": "6063-T5 aluminium",
            "profile_mm": "40x40",
            "max_station_size_cm": {"length": 200, "width": 80, "height": 150},
            "max_load_kg": 200,
            "finish": "anodised (food-safe)",
            "modular": True,
        },
        "suitable_tasks": ["workstation construction", "equipment mounting", "kitchen layout"],
        "price_range": "$$",
        "interfaces": ["T-slot connectors", "angle brackets"],
    },
    {
        "id": "COMP-009",
        "name": "Stainless Steel Hygienic Frame",
        "category": "frame",
        "description": "316L stainless steel frame system for food-grade environments. Fully washdown-rated and resistant to corrosion.",
        "specifications": {
            "material": "316L stainless steel",
            "ip_rating": "IP69K",
            "max_load_kg": 300,
            "finish": "electropolished",
            "food_grade": True,
            "washdown_rated": True,
        },
        "suitable_tasks": ["food-grade workstation", "hygienic environment", "commercial kitchen"],
        "price_range": "$$$",
        "interfaces": ["bolted connections", "sanitary clamps"],
    },
    {
        "id": "COMP-010",
        "name": "48V Li-Ion Battery Pack",
        "category": "power",
        "description": "High-capacity lithium-ion battery pack for mobile robotic platforms. Hot-swappable with built-in BMS.",
        "specifications": {
            "voltage_v": 48,
            "capacity_ah": 30,
            "energy_wh": 1440,
            "weight_kg": 12,
            "charging_time_hours": 2.5,
            "cycle_life": 2000,
            "bms": True,
            "hot_swappable": True,
        },
        "suitable_tasks": ["mobile platform power", "autonomous operation", "backup power"],
        "price_range": "$$$",
        "interfaces": ["Anderson connector", "CAN bus BMS"],
    },
    {
        "id": "COMP-011",
        "name": "Industrial Power Supply Unit (PSU)",
        "category": "power",
        "description": "Regulated 48V DC power supply for stationary robotic systems. Redundant design with power factor correction.",
        "specifications": {
            "input_voltage": "100-240V AC",
            "output_voltage_v": 48,
            "max_current_a": 20,
            "power_watts": 960,
            "efficiency_percent": 94,
            "redundant": True,
        },
        "suitable_tasks": ["stationary platform power", "fixed installation"],
        "price_range": "$$",
        "interfaces": ["IEC C14 input", "terminal block output"],
    },
    {
        "id": "COMP-012",
        "name": "Dual-Arm Torso Platform",
        "category": "robot_arm",
        "description": "Dual-arm humanoid torso with two 6-DOF arms mounted on a rotating waist. Designed for bimanual manipulation tasks.",
        "specifications": {
            "arms": 2,
            "degrees_of_freedom_per_arm": 6,
            "waist_rotation_deg": 350,
            "payload_per_arm_kg": 4,
            "reach_per_arm_mm": 750,
            "repeatability_mm": 0.05,
            "weight_kg": 55,
            "power_watts": 800,
        },
        "suitable_tasks": ["bimanual tasks", "complex cooking", "simultaneous operations", "human-like manipulation"],
        "price_range": "$$$$$",
        "interfaces": ["ROS2", "custom SDK"],
    },
]

SENSORS = [
    {
        "id": "SENS-001",
        "name": "RGB-D Stereo Camera",
        "type": "vision",
        "description": "High-resolution depth camera for 3D object recognition, ingredient identification, and workspace monitoring.",
        "specifications": {
            "resolution": "1920x1080 RGB + 1280x720 depth",
            "frame_rate_fps": 30,
            "depth_range_m": {"min": 0.2, "max": 10.0},
            "field_of_view_deg": {"horizontal": 87, "vertical": 58},
            "depth_accuracy_mm": 2,
            "interface": "USB 3.0",
            "power_watts": 4,
        },
        "suitable_tasks": ["object recognition", "ingredient detection", "workspace monitoring", "quality inspection"],
    },
    {
        "id": "SENS-002",
        "name": "Thermal Imaging Camera",
        "type": "temperature",
        "description": "Infrared thermal camera for non-contact temperature monitoring of food, cookware, and cooking surfaces.",
        "specifications": {
            "resolution": "320x240",
            "temperature_range_c": {"min": -20, "max": 400},
            "accuracy_c": 2,
            "frame_rate_fps": 15,
            "field_of_view_deg": {"horizontal": 57, "vertical": 44},
            "interface": "USB 2.0",
            "power_watts": 2,
        },
        "suitable_tasks": ["temperature monitoring", "cooking progress", "safety monitoring", "heat distribution"],
    },
    {
        "id": "SENS-003",
        "name": "K-Type Thermocouple Probe",
        "type": "temperature",
        "description": "High-accuracy contact temperature probe for direct food temperature measurement. Food-safe stainless steel construction.",
        "specifications": {
            "temperature_range_c": {"min": -50, "max": 500},
            "accuracy_c": 0.5,
            "response_time_ms": 200,
            "probe_material": "316 stainless steel",
            "probe_length_mm": 150,
            "food_safe": True,
            "interface": "analog (amplified)",
            "power_watts": 0.1,
        },
        "suitable_tasks": ["food temperature", "oil temperature", "oven calibration", "safety verification"],
    },
    {
        "id": "SENS-004",
        "name": "6-Axis Force/Torque Sensor",
        "type": "force",
        "description": "Precision force/torque sensor for mounting between robot arm and end-effector. Enables compliant manipulation and force feedback.",
        "specifications": {
            "axes": 6,
            "force_range_n": {"fx_fy": 100, "fz": 200},
            "torque_range_nm": {"tx_ty": 5, "tz": 5},
            "resolution_n": 0.05,
            "resolution_nm": 0.001,
            "sample_rate_hz": 1000,
            "overload_protection": True,
            "interface": "EtherCAT",
            "power_watts": 3,
        },
        "suitable_tasks": ["force control", "compliant manipulation", "kneading", "stirring", "cutting feedback"],
    },
    {
        "id": "SENS-005",
        "name": "Capacitive Proximity Sensor Array",
        "type": "proximity",
        "description": "Array of capacitive proximity sensors for detecting objects and ingredients at close range, including liquids and non-metallic items.",
        "specifications": {
            "sensing_range_mm": {"min": 0, "max": 30},
            "resolution_mm": 0.5,
            "sensors_in_array": 8,
            "can_detect": ["metals", "plastics", "liquids", "food items"],
            "response_time_ms": 5,
            "interface": "I2C",
            "power_watts": 0.5,
        },
        "suitable_tasks": ["object detection", "level sensing", "collision avoidance", "ingredient detection"],
    },
    {
        "id": "SENS-006",
        "name": "2D LiDAR Scanner",
        "type": "lidar",
        "description": "Compact 2D LiDAR for navigation, obstacle detection, and workspace mapping in kitchen environments.",
        "specifications": {
            "range_m": 25,
            "angular_resolution_deg": 0.25,
            "scan_rate_hz": 20,
            "field_of_view_deg": 360,
            "accuracy_mm": 30,
            "interface": "Ethernet",
            "power_watts": 8,
        },
        "suitable_tasks": ["navigation", "obstacle avoidance", "mapping", "workspace monitoring"],
    },
    {
        "id": "SENS-007",
        "name": "9-DOF IMU (Inertial Measurement Unit)",
        "type": "imu",
        "description": "High-precision inertial measurement unit for orientation tracking, tilt detection, and motion estimation.",
        "specifications": {
            "axes": 9,
            "accelerometer_range_g": 16,
            "gyroscope_range_dps": 2000,
            "magnetometer_range_ut": 4900,
            "sample_rate_hz": 400,
            "interface": "SPI / I2C",
            "power_watts": 0.1,
        },
        "suitable_tasks": ["orientation tracking", "tilt detection", "motion estimation", "vibration monitoring"],
    },
    {
        "id": "SENS-008",
        "name": "Load Cell (Precision Weighing)",
        "type": "force",
        "description": "High-precision load cell for ingredient weighing and portion control. Food-grade stainless steel.",
        "specifications": {
            "capacity_kg": 10,
            "resolution_g": 0.1,
            "accuracy_percent": 0.02,
            "material": "stainless steel (food-grade)",
            "overload_capacity_percent": 150,
            "interface": "analog (HX711 amplifier)",
            "power_watts": 0.05,
        },
        "suitable_tasks": ["ingredient weighing", "portion control", "recipe precision", "quality control"],
    },
    {
        "id": "SENS-009",
        "name": "Time-of-Flight Distance Sensor",
        "type": "proximity",
        "description": "Compact laser-based distance sensor for precise height and level measurement.",
        "specifications": {
            "range_mm": {"min": 10, "max": 4000},
            "accuracy_mm": 1,
            "measurement_rate_hz": 50,
            "field_of_view_deg": 25,
            "interface": "I2C",
            "power_watts": 0.3,
        },
        "suitable_tasks": ["level measurement", "height detection", "fill monitoring", "distance measurement"],
    },
    {
        "id": "SENS-010",
        "name": "Multi-Spectral Food Quality Sensor",
        "type": "vision",
        "description": "Near-infrared spectral sensor for assessing food freshness, doneness, and composition without contact.",
        "specifications": {
            "wavelength_range_nm": {"min": 400, "max": 1700},
            "spectral_channels": 16,
            "measurement_time_ms": 100,
            "interface": "USB 2.0",
            "power_watts": 2,
            "can_detect": ["moisture content", "fat content", "doneness level", "freshness"],
        },
        "suitable_tasks": ["food quality", "doneness detection", "freshness assessment", "composition analysis"],
    },
]

ACTUATORS = [
    {
        "id": "ACT-001",
        "name": "Adaptive Parallel Gripper",
        "type": "gripper",
        "description": "Two-finger adaptive gripper with soft silicone pads. Suitable for handling a wide variety of food items, utensils, and cookware.",
        "specifications": {
            "grip_force_n": {"min": 1, "max": 100},
            "stroke_mm": 110,
            "finger_material": "food-grade silicone over aluminium",
            "grip_speed_mm_per_sec": 150,
            "weight_kg": 0.9,
            "food_safe": True,
            "interface": "Modbus RTU",
            "power_watts": 20,
        },
        "suitable_tasks": ["food handling", "utensil grasping", "pan holding", "ingredient placement"],
    },
    {
        "id": "ACT-002",
        "name": "Soft Robotic Gripper",
        "type": "gripper",
        "description": "Pneumatic soft gripper with three compliant fingers. Excellent for handling delicate food items without damage.",
        "specifications": {
            "grip_force_n": {"min": 0.5, "max": 30},
            "finger_count": 3,
            "finger_material": "food-grade silicone",
            "actuation": "pneumatic",
            "pressure_bar": {"min": 0, "max": 2},
            "weight_kg": 0.3,
            "food_safe": True,
            "interface": "pneumatic valve (I2C controller)",
            "power_watts": 5,
        },
        "suitable_tasks": ["delicate food handling", "egg handling", "fruit picking", "sushi assembly"],
    },
    {
        "id": "ACT-003",
        "name": "Peristaltic Pump",
        "type": "pump",
        "description": "Food-grade peristaltic pump for precise liquid dispensing. No contact between pump mechanism and fluid.",
        "specifications": {
            "flow_rate_ml_per_min": {"min": 1, "max": 500},
            "accuracy_percent": 1,
            "tubing_material": "food-grade silicone",
            "tubing_inner_diameter_mm": 6,
            "max_viscosity_cp": 5000,
            "reversible": True,
            "interface": "PWM / RS-485",
            "power_watts": 15,
        },
        "suitable_tasks": ["liquid dispensing", "sauce pouring", "oil dispensing", "batter dispensing"],
    },
    {
        "id": "ACT-004",
        "name": "Precision Dispensing Nozzle",
        "type": "nozzle",
        "description": "Electronically controlled dispensing nozzle for precise placement of sauces, batters, and liquids.",
        "specifications": {
            "orifice_diameter_mm": {"min": 0.5, "max": 5},
            "flow_control": "servo-actuated needle valve",
            "dispensing_accuracy_ml": 0.1,
            "max_temperature_c": 120,
            "material": "316 stainless steel",
            "food_safe": True,
            "interface": "PWM",
            "power_watts": 8,
        },
        "suitable_tasks": ["sauce dispensing", "decoration", "precise pouring", "batter application"],
    },
    {
        "id": "ACT-005",
        "name": "Motorised Stirring Tool",
        "type": "stirrer",
        "description": "Attachable motorised stirring end-effector with interchangeable paddles for various stirring tasks.",
        "specifications": {
            "speed_rpm": {"min": 10, "max": 600},
            "torque_nm": 2.5,
            "paddle_types": ["whisk", "spatula", "spoon", "flat paddle"],
            "material": "food-grade stainless steel and silicone",
            "max_temperature_c": 200,
            "food_safe": True,
            "interface": "RS-485",
            "power_watts": 30,
        },
        "suitable_tasks": ["stirring", "whisking", "folding", "mixing", "emulsification"],
    },
    {
        "id": "ACT-006",
        "name": "Rotary Cutting Tool",
        "type": "cutter",
        "description": "Motorised rotary blade for slicing, dicing, and precision cutting of ingredients.",
        "specifications": {
            "blade_diameter_mm": 80,
            "speed_rpm": {"min": 100, "max": 3000},
            "blade_material": "food-grade stainless steel",
            "cutting_depth_mm": 30,
            "safety_guard": True,
            "food_safe": True,
            "interface": "RS-485",
            "power_watts": 50,
        },
        "suitable_tasks": ["slicing", "dicing", "cutting", "portioning"],
    },
    {
        "id": "ACT-007",
        "name": "Ultrasonic Cutting Blade",
        "type": "cutter",
        "description": "Ultrasonic vibrating blade for clean, precise cuts through soft and sticky foods without deformation.",
        "specifications": {
            "frequency_khz": 40,
            "blade_length_mm": 150,
            "blade_material": "titanium alloy",
            "cutting_speed_mm_per_sec": 50,
            "power_watts": 35,
            "food_safe": True,
            "interface": "RS-485",
        },
        "suitable_tasks": ["sushi cutting", "cake slicing", "bread cutting", "delicate portioning"],
    },
    {
        "id": "ACT-008",
        "name": "Tool Changer (Quick-Release)",
        "type": "gripper",
        "description": "Automatic tool changer enabling the robot to switch between different end-effectors (grippers, tools, nozzles) without human intervention.",
        "specifications": {
            "payload_kg": 10,
            "change_time_sec": 2,
            "tool_stations": 6,
            "locking_mechanism": "pneumatic",
            "repeatability_mm": 0.01,
            "weight_kg": 1.2,
            "interface": "EtherCAT + pneumatic",
            "power_watts": 10,
        },
        "suitable_tasks": ["tool switching", "multi-task operations", "flexible manufacturing"],
    },
]

# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def search_components(category: str = "", task: str = "") -> str:
    """
    Search for robotic components by category and/or task suitability.

    Args:
        category: Component category to filter by (e.g. 'robot_arm', 'mobile_base',
                  'controller', 'frame', 'power'). Leave empty for all categories.
        task: Task keyword to search for in suitable_tasks (e.g. 'cooking', 'navigation').
              Leave empty for all tasks.
    """
    results = []
    for comp in COMPONENTS:
        cat_match = not category or category.lower() in comp["category"].lower()
        task_match = not task or any(
            task.lower() in t.lower() for t in comp["suitable_tasks"]
        )
        if cat_match and task_match:
            results.append(
                {
                    "id": comp["id"],
                    "name": comp["name"],
                    "category": comp["category"],
                    "description": comp["description"],
                    "suitable_tasks": comp["suitable_tasks"],
                    "price_range": comp["price_range"],
                }
            )

    return json.dumps(
        {"query": {"category": category, "task": task}, "results_count": len(results), "components": results},
        indent=2,
    )


@mcp.tool()
def search_sensors(sensor_type: str = "", task: str = "") -> str:
    """
    Search for sensors by type and/or task suitability.

    Args:
        sensor_type: Sensor type to filter by (e.g. 'vision', 'temperature', 'force',
                     'proximity', 'lidar', 'imu'). Leave empty for all types.
        task: Task keyword to search for (e.g. 'temperature monitoring', 'object recognition').
              Leave empty for all tasks.
    """
    results = []
    for sensor in SENSORS:
        type_match = not sensor_type or sensor_type.lower() in sensor["type"].lower()
        task_match = not task or any(
            task.lower() in t.lower() for t in sensor["suitable_tasks"]
        )
        if type_match and task_match:
            results.append(
                {
                    "id": sensor["id"],
                    "name": sensor["name"],
                    "type": sensor["type"],
                    "description": sensor["description"],
                    "suitable_tasks": sensor["suitable_tasks"],
                }
            )

    return json.dumps(
        {"query": {"sensor_type": sensor_type, "task": task}, "results_count": len(results), "sensors": results},
        indent=2,
    )


@mcp.tool()
def search_actuators(actuator_type: str = "", task: str = "") -> str:
    """
    Search for actuators and end-effectors by type and/or task suitability.

    Args:
        actuator_type: Actuator type to filter by (e.g. 'gripper', 'pump', 'nozzle',
                       'stirrer', 'cutter'). Leave empty for all types.
        task: Task keyword to search for (e.g. 'food handling', 'stirring', 'cutting').
              Leave empty for all tasks.
    """
    results = []
    for act in ACTUATORS:
        type_match = not actuator_type or actuator_type.lower() in act["type"].lower()
        task_match = not task or any(
            task.lower() in t.lower() for t in act["suitable_tasks"]
        )
        if type_match and task_match:
            results.append(
                {
                    "id": act["id"],
                    "name": act["name"],
                    "type": act["type"],
                    "description": act["description"],
                    "suitable_tasks": act["suitable_tasks"],
                }
            )

    return json.dumps(
        {"query": {"actuator_type": actuator_type, "task": task}, "results_count": len(results), "actuators": results},
        indent=2,
    )


@mcp.tool()
def get_component_details(component_id: str) -> str:
    """
    Get full details and specifications for a specific component, sensor, or actuator.

    Args:
        component_id: The unique ID of the item (e.g. 'COMP-001', 'SENS-003', 'ACT-005')
    """
    component_id = component_id.upper().strip()

    # Search all databases
    for db in [COMPONENTS, SENSORS, ACTUATORS]:
        for item in db:
            if item["id"] == component_id:
                return json.dumps(item, indent=2)

    # Build list of all valid IDs
    all_ids = (
        [c["id"] for c in COMPONENTS]
        + [s["id"] for s in SENSORS]
        + [a["id"] for a in ACTUATORS]
    )
    return json.dumps(
        {
            "error": f"Component '{component_id}' not found.",
            "available_ids": all_ids,
        },
        indent=2,
    )


@mcp.tool()
def recommend_platform(task_description: str) -> str:
    """
    Recommend a set of suitable components, sensors, and actuators for a described task.
    Returns categorised recommendations with reasoning.

    Args:
        task_description: A description of the robotic task (e.g. 'a robot that can
                         make pasta carbonara including boiling, frying, and plating')
    """
    task_lower = task_description.lower()

    # Score components by keyword overlap with task description
    def score_item(item):
        score = 0
        searchable_text = (
            item.get("description", "").lower()
            + " "
            + " ".join(item.get("suitable_tasks", []))
        )
        # Check for keyword matches
        keywords = task_lower.split()
        for kw in keywords:
            if kw in searchable_text:
                score += 1
        # Bonus for direct task matches
        for task in item.get("suitable_tasks", []):
            if any(kw in task.lower() for kw in keywords):
                score += 2
        return score

    # Score and rank each category
    scored_components = sorted(
        [(score_item(c), c) for c in COMPONENTS], key=lambda x: -x[0]
    )
    scored_sensors = sorted(
        [(score_item(s), s) for s in SENSORS], key=lambda x: -x[0]
    )
    scored_actuators = sorted(
        [(score_item(a), a) for a in ACTUATORS], key=lambda x: -x[0]
    )

    # Select top recommendations
    rec_components = [
        {"id": c["id"], "name": c["name"], "relevance_score": s, "category": c["category"]}
        for s, c in scored_components[:4]
        if s > 0
    ]
    rec_sensors = [
        {"id": s["id"], "name": s["name"], "relevance_score": sc, "type": s["type"]}
        for sc, s in scored_sensors[:5]
        if sc > 0
    ]
    rec_actuators = [
        {"id": a["id"], "name": a["name"], "relevance_score": sc, "type": a["type"]}
        for sc, a in scored_actuators[:4]
        if sc > 0
    ]

    recommendation = {
        "task_description": task_description,
        "recommended_components": rec_components,
        "recommended_sensors": rec_sensors,
        "recommended_actuators": rec_actuators,
        "notes": [
            "Use get_component_details(id) to get full specifications for any recommended item.",
            "Consider combining multiple actuators via a tool changer for versatility.",
            "Ensure all food-contact components are rated food-safe.",
            "A safety PLC is recommended for any system operating near humans or hot surfaces.",
        ],
    }

    return json.dumps(recommendation, indent=2)


# ---------------------------------------------------------------------------
# Import guard for running as MCP server
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
