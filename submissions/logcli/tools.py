from pymavlink import mavutil
import time
import threading

master = mavutil.mavlink_connection('udp:127.0.0.1:14553')
# Wait a heartbeat before sending commands
master.wait_heartbeat()
last_pwm = 1500
curr_height_cm = 0

height_reached_flag = False  

master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,
    0,
    mavutil.mavlink.MAVLINK_MSG_ID_DISTANCE_SENSOR,
    100000,  # 100ms = 10Hz
    0, 0, 0, 0, 0
)

def arm():
  master.mav.command_long_send(
      master.target_system,
      master.target_component,
      mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
      0,
      1, 0, 0, 0, 0, 0, 0)
  print("Arming command sent, waiting for confirmation.....")
  start_time = time.time()
  while not master.motors_armed():
    if time.time() - start_time > 10:  # Timeout after 10 seconds
        print("Failed to arm: Timeout")
        return False  
    time.sleep(1)
    master.recv_match(type='HEARTBEAT', blocking=True)  # Ensure fresh status

  print("Armed successfully!")
  return True  # Return True if armed


def disarm():
  master.mav.command_long_send(
      master.target_system,
      master.target_component,
      mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
      0,
      0, 0, 0, 0, 0, 0, 0)
  print("Disarming command sent, waiting for confirmation.....")


def height_reached():
    """Returns True if height >= 3m, otherwise False."""
    return height_reached_flag

def monitor_height():
    
    """Continuously monitors height from the rangefinder."""
    global height_reached_flag
    global curr_height
    while True :
        msg = master.recv_match(type='DISTANCE_SENSOR', blocking=True, timeout=1)
        if msg:
            height = msg.current_distance / 100.0  # Convert cm to meters
            # print(f"Height: {height:.2f} meters")

            if height >= 2.6:
                height_reached_flag = True
                print("3 meter height reached")
            
            curr_height = msg.current_distance  # Convert meters to cm

            if height_reached_flag and (curr_height < 25):
              print("Can disarm")
              disarm()
              disarm()
              print("Disarming the drone")
              # completed = False
              print("Motors disarmed successfully!")

        else:
            print("Waiting for distance sensor data...")  # Debugging output
        time.sleep(0.1)

# Start the monitoring thread
height_thread = threading.Thread(target=monitor_height, daemon=True)
height_thread.start()


def set_mode(mode):
    """Set the flight mode and verify it."""
    if mode not in master.mode_mapping():
        print(f'Unknown mode: {mode}')
        print('Try:', list(master.mode_mapping().keys()))
        # sys.exit(1)

    mode_id = master.mode_mapping()[mode]

    master.mav.set_mode_send(
        master.target_system,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_id
    )

    start_time = time.time()
    while time.time() - start_time < 10:  # 10 seconds timeout
        msg = master.recv_match(type='HEARTBEAT', blocking=True, timeout=1)
        if msg:
            current_mode = msg.custom_mode
            print(current_mode)
            if current_mode == mode_id:
                print(f"Mode successfully changed to {mode}")
                return mode
        print("Waiting for mode change confirmation...")

    print(f"Timeout: Mode change to {mode} was not confirmed.")

def set_rc_channel_pwm(channel_id, pwm=1500):
    """ Set RC channel pwm value
    Args:
        channel_id (TYPE): Channel ID
        pwm (int, optional): Channel pwm value 1100-1900
    """
    if channel_id < 1 or channel_id > 18:
        print("Channel does not exist.")
        return

    # Mavlink 2 supports up to 18 channels:
    # https://mavlink.io/en/messages/common.html#RC_CHANNELS_OVERRIDE
    rc_channel_values = [65535 for _ in range(18)]
    rc_channel_values[channel_id - 1] = pwm
    master.mav.rc_channels_override_send(
        master.target_system,                # target_system
        master.target_component,             # target_component
        *rc_channel_values)                  # RC channel list, in microseconds.


time.sleep(2)

if(set_mode('LOITER') == 'LOITER'):
  time.sleep(2)
  set_rc_channel_pwm(3, 991)
  set_rc_channel_pwm(3, 991)
  if(arm()):
    time.sleep(2)
    start_time = time.time()
    while time.time() - start_time < 70:
      if time.time() - start_time < 8:
        last_pwm = 1715
        if height_reached():
          print("Height reached")
          last_pwm = 1505
          print("Hovering from RNGFND")
        set_rc_channel_pwm(3, last_pwm)
      else:
         if time.time() - start_time > 40:
        # if(set_mode('LAND') == 'LAND'):
          set_rc_channel_pwm(3, 1355)
          print("Landing") 
         else:
          set_rc_channel_pwm(3, 1505)
          print("Hovering from else")
      
      time.sleep(0.1)
      
      # master.motors_disarmed_wait()
      # height_thread.join(5)

  else:
    print("Failed to arm")


  