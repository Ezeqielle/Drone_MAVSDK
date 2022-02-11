#!/usr/bin/env python3

from __future__ import absolute_import
import asyncio
from mavsdk import System

async def run():
    # Init the drone
    drone = System()
    await drone.connect(system_address="udp://:14540")

    # Connect to drone and get system informations
    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected():
            info = await drone.info.get_version()
            print(f"Drone discovered with UUID: {state.uuid}")
            print(f"Firmware version: {info.firmware_version}")
            break
    
    # Start calibrating
    print("-- Starting gyroscope calibration")
    async for progress_data in drone.calibration.calibrate_gyro():
        print(progress_data)
    print("-- Gyroscope calibration finished")

    print("-- Starting accelerometer calibration")
    async for progress_data in drone.calibration.calibrate_accelerometer():
        print(progress_data)
    print("-- Accelerometer calibration finished")

    print("-- Starting magnetometer calibration")
    async for progress_data in drone.calibration.calibrate_magnetometer():
        print(progress_data)
    print("-- Magnetometer calibration finished")

    print("-- Starting board level horizon calibration")
    async for progress_data in drone.calibration.calibrate_level_horizon():
        print(progress_data)
    print("-- Board level calibration finished")

    # Calibrating home point
    print("Waiting for drone to have a GPS fix...")
    async for gps_info in drone.telemetry.in_air_info():
        if gps_info.in_air and gps_info.has_gps_fix:
            print("-- Starting home point calibration")
            async for progress_data in drone.calibration.calibrate_home_point():
                print(progress_data)
            print("-- Home point calibration finished")
            break
    
    # Arming
    print("-- Arming")
    await drone.action.arm()
    print("-- Armed")

    # Taking off
    print("-- Taking off")
    await drone.action.takeoff()
    await asyncio.sleep(5)
    print("-- Taking off finished")
    print("-- Dronne is flying")

    # Go to a point
    print("-- Going to a point")
    fly_altitude = absolute_altitude + 10.0 # 10 meters above the ground
    await drone.action.go_location(0, 0, fly_altitude, 0)

    # Landing
    print("-- Landing")
    await drone.action.land()
    


if __name__ == "_main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
