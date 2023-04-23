import os
import subprocess
import time
import sys

def wait(seconds):
    print("Waiting...", end="")
    for i in range(seconds):
        time.sleep(1)
        sys.stdout.write(".")
        sys.stdout.flush()
    print("\n")

# Check if at least one .ovpn file is present in the directory
def check_ovpn_files(path):
    ovpn_files = [f for f in os.listdir(path) if f.endswith('.ovpn')]
    if len(ovpn_files) == 0:
        print("No .ovpn files found in directory")
        return False
    else:
        print("At least one .ovpn file is present in the directory")
        return ovpn_files

# Check if OpenVPN is installed
def check_openvpn():
    try:
        subprocess.check_call(['openvpn', '--version'])
        print("OpenVPN is installed..")
        return True
    except subprocess.CalledProcessError:
        print("OpenVPN is not installed")
        return False

# Connect to each .ovpn file and test connection speed
def connect_and_test_speed(path, ovpn_files):
    speeds = {}
    for file in ovpn_files:
        try:
            output = subprocess.check_output(['sudo', 'openvpn', os.path.join(path, file)], stderr=subprocess.STDOUT)
            output = output.decode('utf-8')
            # Extract the speed from the output
            start_index = output.find('Speed=') + 6
            end_index = output.find('Mbits/s', start_index)
            speed = float(output[start_index:end_index])
            speeds[file] = speed
            # Disconnect from the VPN
            subprocess.call(['sudo', 'killall', 'openvpn'])
        except subprocess.CalledProcessError as e:
            print(f"Error connecting to {file}: {e}")
    return speeds

# Select the .ovpn file with the fastest speed
def select_fastest_speed(speeds):
    if len(speeds) == 0:
        print("No .ovpn files were tested")
        return None
    else:
        fastest_speed = max(speeds.values())
        for file, speed in speeds.items():
            if speed == fastest_speed:
                print(f"{file} has the fastest connection speed ({speed} Mbits/s)")
                return file

if __name__ == '__main__':
    path = '/etc/openvpn/'
    ovpn_files = check_ovpn_files(path)
    if ovpn_files:
        openvpn_installed = check_openvpn()
        wait(3)
        if openvpn_installed:
            speeds = connect_and_test_speed(path, ovpn_files)
            fastest_file = select_fastest_speed(speeds)
            if fastest_file:
                # Connect to the fastest .ovpn file
                subprocess.call(['sudo', 'openvpn', os.path.join(path, fastest_file)])
