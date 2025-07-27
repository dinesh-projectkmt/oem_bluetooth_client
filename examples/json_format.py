import time
import json

oom_live_packet = "6a07150ced0404007107140cf60404004007150c59050300a606150cb90504007406150cee0504004f06110c02060400ea05150c7f060400c905150ca30604009105170ca10603006905150cf40604003d05160c220703000b05160ccc0604005204150c6f0804004c03140c720904005902160c5e0a0300ef01150c450a0300f001150c640a0400cb01160c8d0a0300b201140ca30a03008601150cc10a04005f01150ce70a03000b01160c330b04000801150c3a0b0400eb00150c580b0400a900160c920b04000000019842d2f17b0000900020050000ff002c0101ffff0000000031c0c1000100000000000000000000000000000000"
patient_id = "67c6de22a69621459c6ae07e"

# Create a blank JSON structure
blank_json = {
    "dateTime": int(time.time() * 1000),  # current timestamp in milliseconds
    "data": "",                           # empty ECG data
    "patient": "",                        # blank patient ID
    "leadDetection": 0,                   # default value
    "trigger": False,                     # default value
    "ecgVersion": 0                       # default version
}

blank_json["data"] = oom_live_packet[0:400]
blank_json["dateTime"] = int.from_bytes(bytes.fromhex(oom_live_packet)[200:208], byteorder='big')  # or 'big'
blank_json["patient"] = patient_id

Lead_1 = int.from_bytes(bytes.fromhex(oom_live_packet)[219:220], byteorder='big')
Lead_2 = int.from_bytes(bytes.fromhex(oom_live_packet)[220:221], byteorder='big')

if(Lead_1 == 0 and Lead_2 == 0):
    Lead = 0
else:
    Lead = 1

blank_json["leadDetection"] = Lead

blank_json["trigger"] = int.from_bytes(bytes.fromhex(oom_live_packet)[208:209], byteorder='big')

if(int.from_bytes(bytes.fromhex(oom_live_packet)[221:222], byteorder='big') == 255):
    ecgVersion = 2
else:
    ecgVersion = 5

blank_json["ecgVersion"] = ecgVersion

# int_x_position = int.from_bytes(bytes.fromhex(oom_live_packet)[209:211], byteorder='big')
# int_y_position = int.from_bytes(bytes.fromhex(oom_live_packet)[211:213], byteorder='big')
# int_z_position = int.from_bytes(bytes.fromhex(oom_live_packet)[213:215], byteorder='big')
# battery = int.from_bytes(bytes.fromhex(oom_live_packet)[218:219], byteorder='big')

# Lead_version = int.from_bytes(bytes.fromhex(oom_live_packet)[221:222], byteorder='big')
# signal_rssi = int.from_bytes(bytes.fromhex(oom_live_packet)[229:230], byteorder='big', signed=True)


# Print the JSON as a string
print(json.dumps(blank_json, indent=2))
