import os
import subprocess
import time
import signal
from datetime import datetime, timedelta

# Set your wireless interface and target directory
interface = "wlan1"
target_dir = "/home/pi/project/sniff1/"

def stop_monitor_mode():
    subprocess.run(["sudo", "airmon-ng", "stop", mon_interface])

# Put the wireless interface into monitor mode
subprocess.run(["sudo", "airmon-ng", "start", interface])

# Set the monitor interface variable
mon_interface = "wlan1"  # Replace this with the monitor interface name displayed after the previous command.

# Calculate the end time
duration = 900
start_time = time.time()
try:
    # Loop until the time is up
    while time.time() - start_time < duration:
        #timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"sniff.csv"
        filepath = os.path.join(target_dir, filename)

        kill_wpa_sup = subprocess.Popen("ps ax | grep 'wpa_supplicant -B -c/etc/wpa_supplicant/wpa_supplicant-wlan1.conf -iwlan1'", shell=True, stdout=subprocess.PIPE)
        for i in kill_wpa_sup.stdout:
          pid = i.decode('utf-8').split()[0]
          a = subprocess.Popen('sudo kill -9 '+pid, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # Run airodump-ng for 1 second and save the data to a CSV file
        p = subprocess.Popen(["sudo", "airodump-ng", "wlan1" ,"--write", "sniff", "--output-format", "csv","--write-interval", "5"])
        time.sleep(5)
        kill_sniff = subprocess.Popen('ps ax | grep airodump', shell=True, stdout=subprocess.PIPE)
        for i in kill_sniff.stdout:
          pid = i.decode('utf-8').split()[0]
          a = subprocess.Popen('sudo kill -9 '+pid, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except KeyboardInterrupt:
    print("Interrupt received, stopping airodump-ng and cleaning up...")
    stop_monitor_mode()

else:
    # Stop monitor mode
    stop_monitor_mode()
