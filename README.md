# Lab 3: Object Detection and Autonomous Palletizing

## Overview
This project integrates computer vision with robotic manipulation using the **Dobot Magician Lite**. The goal is to detect, classify, and sort objects autonomously using a custom **YOLO** model.

## Objectives
* Apply real-time object detection using **YOLOv8**.
* Control the Dobot Magician Lite via the **pydobot2** library.
* Perform automated sorting:
    * **Food items** -> Placed in **Pallet A**.
    * **Vehicle items** -> Placed in **Pallet B**.

## Setup
1. **Hardware**: Dobot Magician Lite with a suction cup and end-effector mounted camera.
2. **Software**: Install dependencies using:
   ```bash
   pip install -r requirements.txt
