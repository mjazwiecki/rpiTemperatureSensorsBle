import DeviceClient
import datetime
from ruuvitag_sensor.ruuvi import RuuviTagSensor
import json
import subprocess
import time
from ast import literal_eval

##########################################
# START: Azure IoT Hub settings
KEY = ""
HUB = ""
DEVICE_NAME = ""
# END: Azure IoT Hub settings
###########################################

device = DeviceClient.DeviceClient(HUB, DEVICE_NAME, KEY)
device.create_sas(600)

ruuvi_macs = ['AA:BB:CC:DD:EE:FF', 'AA:BB:CC:DD:EE:FF']
xiaomi_macs = ['AA:BB:CC:DD:EE:FF', 'AA:BB:CC:DD:EE:FF']

#####################
# ruuvitag section
#####################
timeout_in_sec = 30
datas = RuuviTagSensor.get_data_for_sensors(ruuvi_macs, timeout_in_sec)

for mac in ruuvi_macs:

    try:
        r = datas[mac]
        data={"humidity": float(r['humidity']), "temperature": float(r['temperature']), "batteryVoltage": float(r['battery']/1000), "timestamp": int(time.time()), "mac": r['mac']}

        f = open("data.txt", "a")
        f.write(str(data))
        f.write("\n")
        f.close
    except KeyError:
        print("Cannot fetch data for RuuviTag with MAC " + str(mac)+ ". Skipping.")

#####################
# xiaomi section
#####################

for mac in xiaomi_macs:
    output=subprocess.check_output('python3 /home/pi/<proper_folder_here>/LYWSD03MMC.py -d ' + \
                                   mac + ' -r -deb -b -c 1 --callback ./dumpOutputToFile.sh', shell=True)


#####################
# read from a queue and send
#####################

# check how many lines in queue
f=open("data.txt", "r")
lines=f.readlines()
liness = lines.copy() # duplicate lines
f.close()

data = []
i = 0
while i < len(lines):
        # xiaomi
        if lines[i][:10] == "sensorname":
                part=lines[i].split(" ")
                x_weatherdata={"humidity": float(part[3]), "temperature": float(part[2]), "batteryLevel": float(part[5]), "timestamp": int(part[6]), "mac": part[1].replace(':', '').lower()}
                x_encode_weatherdata=json.dumps(x_weatherdata, indent=1).encode('utf-8')
                if device.send(x_encode_weatherdata) == 204:
                        e = lines[i]
                        print("Message sent to IoT Hub: " + str(x_encode_weatherdata))
                        liness.remove(e)
                        print("and removed from the queue. \n")
        # ruuvitag
        if lines[i][0] == "{": 
                data_dict = literal_eval(lines[i])
                r_encode_weatherdata = json.dumps(data_dict, indent=1).encode('utf-8')
                if device.send(r_encode_weatherdata) == 204:
                        e = lines[i]
                        print("Message sent to IoT Hub: " + str(r_encode_weatherdata))
                        liness.remove(e)
                        print("and removed from the queue. \n")
        i += 1

# remove all successfully sent lines
new_file=open("data.txt", "w+")
for line in liness:
    new_file.write(line)
new_file.close()
#done removing
print("cleaning the queue.")
