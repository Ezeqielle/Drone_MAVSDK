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

    # Get the battery informations
    async for battery in drone.telemetry.battery_info():
        print(f"Battery: {battery.percentage}%")
        if battery.percentage < 20:
            print("Battery is low, shutting down")
            await drone.action.set_piloting_mode(piloting_mode="landing")
            await drone.action.landing()
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

    # Calibrating home altitude
    print("Fetching amsl altitude at home point")
    async for terrain_info in drone.telemetry.home():
        absolute_altitude = terrain_info.absolute_altitude_m
        print(f"-- Home altitude: {terrain_info.altitude_amsl}")
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

    # Is drone flying?
    async for in_air_info in drone.telemetry.in_air_info():
        if in_air_info.in_air:
            print("-- Drone is flying")
            break

    # Go to a point
    print("-- Going to a point")
    fly_altitude = absolute_altitude + 10.0 # 10 meters above the ground
    await drone.action.go_location(0, 0, fly_altitude, 0)

    # Landing
    print("-- Landing")
    await drone.action.land()

    # Is drone landed?
    async for in_air_info in drone.telemetry.in_air_info():
        if not in_air_info.in_air:
            print("-- Drone is landed")
            break

    # Last position point
    print("-- Last position point")
    async for gps_info in drone.telemetry.gps_info():
        print(f"Latitude: {gps_info.latitude}")
        print(f"Longitude: {gps_info.longitude}")
        print(f"Altitude: {gps_info.altitude}")

    # Disarming
    print("-- Disarming")
    await drone.action.disarm()
    print("-- Disarmed")
    


if __name__ == "_main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())