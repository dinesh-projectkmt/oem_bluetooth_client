import asyncio
import paho.mqtt.client as mqtt
from bleak import BleakScanner, BleakClient
import json
import time
import matplotlib.pyplot as plt
import csv
import os
import struct

bluetooth_device_name = "OOM_CARDIO"
oom_serial_number = "KE315072500099"
web_patient_id = "67c6de22a69621459c6ae07e"

BROKER = "oomcardiodev.projectkmt.com"      # replace with your broker
PORT = 1884                       # default port for non-TLS
TOPIC = "oom/ecg/rawData/67c6de22a69621459c6ae07e"            # replace with your topic
USERNAME = "kmt"        # replace with your MQTT username
PASSWORD = "Kmt123"        # replace with your MQTT password

mqtt_client = mqtt.Client()

# Callback when connection is established
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected successfully to MQTT Broker!")
        # client.subscribe(TOPIC)
        # print(f"✅ Subscribed to topic: {TOPIC}")
    else:
        print(f"❌ Failed to connect, return code {rc}")

live_ecg_json = {
    "dateTime": int(time.time() * 1000),  # current timestamp in milliseconds
    "data": "",                           # empty ECG data
    "patient": "",                        # blank patient ID
    "leadDetection": 0,                   # default value
    "trigger": False,                     # default value
    "ecgVersion": 0                       # default version
}

live_ecg_data = {
    "epochTime": 0,
    "Lead_I": "",
    "Lead_II": "",
    "V1": "",
    "V2": "",
    "V3": "",
    "V4": "",
    "V5": "",
    "V6": ""
}

# Buffer to store 10 seconds of data
ecg_data_buffer = []
start_time = None
save_duration = 10  # in seconds
stop_notifications_flag = False
write_once = False

file_path = "new_square.csv"

data_buffer = []

header = ["epochTime", "Lead_I", "Lead_II", "V1", "V2", "V3", "V4", "V5", "V6"]

# Notification handler
def notification_handler(sender, data):
    global start_time, ecg_data_buffer, stop_notifications_flag
    if stop_notifications_flag:
        return
    # try:
    # print(len(data))
    # print("data = ")
    # print(data)
    if start_time is None:
        start_time = time.time()
        file_exists = os.path.isfile(file_path)
        with open(file_path, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=header)
            if not file_exists:
                writer.writeheader()
    current_time = time.time()
    if current_time - start_time <= save_duration:
        live_ecg_json["data"] = data.hex()[0:498] # [0:400]
        live_ecg_json["dateTime"] = int.from_bytes(bytes.fromhex(data.hex())[208:216], byteorder='big')  # or 'big' [200:208]
        live_ecg_json["patient"] = web_patient_id
        # print("live ecg json data")
        # print(live_ecg_json["data"])
        # Lead_1 = int.from_bytes(bytes.fromhex(data.hex())[219:220], byteorder='big')
        # Lead_2 = int.from_bytes(bytes.fromhex(data.hex())[220:221], byteorder='big')
        # all_data = [(data[i] << 8) | data[i+1] for i in range(0, len(data) - 1, 2)]
        # all_data = [(data[i+1] << 8) | data[i] for i in range(0, len(data) - 1, 2)]
        all_data = list(struct.unpack('<' + 'h' * (len(data) // 2), data))
        # print("all_data")
        # print(all_data)
        lead1 = all_data[0:13]
        lead2 = all_data[13:26] # lead1 -> 0:13
        v1 = all_data[26:39]
        v2 = all_data[39:52]
        v3 = all_data[52:65]
        v4 = all_data[65:78]
        v5 = all_data[78:91]
        v6 = all_data[91:104]
        for i in range(8):
            live_ecg_data["epochTime"] = live_ecg_json["dateTime"]
            live_ecg_data["Lead_I"] = lead1[i]
            live_ecg_data["Lead_II"] = lead2[i]
            live_ecg_data["V1"] = v1[i]
            live_ecg_data["V2"] = v2[i]
            live_ecg_data["V3"] = v3[i]
            live_ecg_data["V4"] = v4[i]
            live_ecg_data["V5"] = v5[i]
            live_ecg_data["V6"] = v6[i]
            # print(live_ecg_data)
            # data_buffer.append(live_ecg_data)
            with open(file_path, mode = 'a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=header)
                writer.writerow(live_ecg_data)
    else:
        stop_notifications_flag = True
        print("⏱️ Done collecting 10 seconds of data.")
        # read_csv_and_plot("Lead_II", file_path)
        # plot_ecg_from_csv(file_path, "Lead_II")
        plot_all_ecg_leads(file_path)
        
        # file_exists = os.path.isfile(file_path)
        # with open(file_path, mode='w', newline='') as file:
        #     writer = csv.DictWriter(file, fieldnames=header)
        #     # if not file_exists:
        #     writer.writeheader()
        #     writer.writerows(data_buffer)
            # for entry in data_buffer:
            #     writer.writerow(entry)
        # save_to_csv()
        # read_csv_and_plot("V6")
    # except:
    #     live_ecg_json["data"] = data.hex()[0:400]
    #     live_ecg_json["dateTime"] = int.from_bytes(bytes.fromhex(data.hex())[200:208], byteorder='big')  # or 'big'
    #     live_ecg_json["patient"] = web_patient_id

    #     Lead_1 = int.from_bytes(bytes.fromhex(data.hex())[219:220], byteorder='big')
    #     Lead_2 = int.from_bytes(bytes.fromhex(data.hex())[220:221], byteorder='big')

    #     # all_data = [data[i:i+2] for i in range(0, 400)]
    #     all_data = [(data[i] << 8) | data[i+1] for i in range(0, len(data) - 1, 2)]

    #     if(Lead_1 == 0 and Lead_2 == 0):
    #         Lead = 0
    #     else:
    #         Lead = 1

    #     live_ecg_json["leadDetection"] = Lead

    #     live_ecg_json["trigger"] = int.from_bytes(bytes.fromhex(data.hex())[208:209], byteorder='big')

    #     if(int.from_bytes(bytes.fromhex(data.hex())[221:222], byteorder='big') == 255):
    #         ecgVersion = 2
    #     else:
    #         ecgVersion = 5

    #     live_ecg_json["ecgVersion"] = ecgVersion
        # mqttclient.publish("oom/ecg/rawData/" + web_patient_id, json.dumps(live_ecg_json))
        # print(live_ecg_json)
# Enable notifications
async def enable_notifications(client, characteristic_uuid):
    try:
        await client.start_notify(characteristic_uuid, notification_handler)
        print(f"✅ Notifications enabled on {characteristic_uuid}")
    except Exception as e:
        print(f"❌ Failed to enable notifications: {e}")

# Read characteristic
async def read_characteristic(client, characteristic_uuid):
    try:
        data = await client.read_gatt_char(characteristic_uuid)
        print(f"✅ Data read from {characteristic_uuid}: {data.decode('utf-8').strip()}")
        return data
    except Exception as e:
        print(f"❌ Failed to read from {characteristic_uuid}: {e}")
        return None

# Write characteristic
async def write_characteristic(client, characteristic_uuid, data_to_write):
    global write_once
    try:
        print(f"✏️ Writing to {characteristic_uuid}: {data_to_write}")
        await client.write_gatt_char(characteristic_uuid, data_to_write)
        print(f"✅ Write successful to {characteristic_uuid}")

        if not write_once:
            await asyncio.sleep(0.5)
        else:
            while True:
                await asyncio.sleep(1)

    except Exception as e:
        print(f"❌ Failed to write to {characteristic_uuid}: {e}")

# Discover and act on services
async def discover_services_and_characteristics(client):
    global write_once
    print("🔍 Discovering services and characteristics...")

    for service in client.services:
        for char in service.characteristics:
            props = ', '.join(char.properties)

            # Device Info service
            if service.uuid == "0000180a-0000-1000-8000-00805f9b34fb":
                if char.uuid == "00002a24-0000-1000-8000-00805f9b34fb":
                    await read_characteristic(client, char.uuid)
                if char.uuid == "00002a26-0000-1000-8000-00805f9b34fb":
                    await read_characteristic(client, char.uuid)

            # Heart Rate / Custom service
            if service.uuid == "0000180d-0000-1000-8000-00805f9b34fb":
                if 'notify' in char.properties or 'indicate' in char.properties:
                    if char.uuid == "00001801-0000-1000-8000-00805f9b34fb":
                        if not write_once:
                            await write_characteristic(client, char.uuid, bytes.fromhex("006319070F03688DCAD0")) #0004190615016883CA00
                            await asyncio.sleep(0.2)
                            await enable_notifications(client, char.uuid)

                    if char.uuid == "00001802-0000-1000-8000-00805f9b34fb":
                        if not write_once:
                            write_once = True
                            await write_characteristic(client, char.uuid, bytes.fromhex("010000"))

# Connect and discover
async def connect_and_discover(device_name, device_address):
    print(f"🔗 Connecting to {device_name} at {device_address}...")
    async with BleakClient(device_address) as client:
        if client.is_connected:
            print(f"✅ Connected to {device_name}")
            await discover_services_and_characteristics(client)
        else:
            print("❌ Failed to connect.")

# Scan for devices
async def scan_ble_devices():
    while True:
        print("🔍 Scanning for BLE devices (1 second)...")
        devices = await BleakScanner.discover(timeout=1, return_adv=True)

        for address, (device, adv_data) in devices.items():
            if device.name == bluetooth_device_name:
                print(f"✅ Device found: {device.name} at {address}")
                print(f"🔧 Manufacturer Data: {adv_data.manufacturer_data}")

                for company_id, data_bytes in adv_data.manufacturer_data.items():
                    print(f"Company ID: {company_id}")
                    print(f"Raw bytes: {data_bytes}")

                    try:
                        raw_serial = int.from_bytes(data_bytes[0:2], 'big')
                        raw_year = int.from_bytes(data_bytes[2:3], 'big')
                        raw_month = int.from_bytes(data_bytes[3:4], 'big')
                        raw_day = int.from_bytes(data_bytes[4:5], 'big')
                        raw_version = int.from_bytes(data_bytes[5:6], 'big')

                        oom_serial_gen = f"KE{raw_version:01d}{raw_day:02d}{raw_month:02d}{raw_year:02d}{raw_serial:05d}"
                        print(f"🔢 Generated Serial: {oom_serial_gen}")

                        if oom_serial_number == oom_serial_gen:
                            print("🎯 Device matched! Connecting...")
                            await connect_and_discover(device.name, address)
                            return

                    except Exception as e:
                        print(f"⚠️ Failed to parse manufacturer data: {e}")

        print("❌ Target device not found.")

def save_to_csv(filename="ecg_data4.csv"):
    if not ecg_data_buffer:
        print("⚠️ No data to save.")
        return

    file_exists = os.path.isfile(filename)
    
    with open(filename, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=header)
        if not file_exists:
            writer.writeheader()
        for entry in ecg_data_buffer:
            writer.writerow(entry)

    print(f"💾 Data saved to {filename}")

def read_csv_and_plot(lead_name="V6", filename="ecg_data4.csv"):
    if not os.path.exists(filename):
        print(f"❌ File '{filename}' not found.")
        return

    all_samples = []

    with open(filename, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            hex_str = row[lead_name]

            try:
                # 2 bytes per sample = 4 hex characters per sample
                samples = [
                    int(hex_str[i:i+4], 16) if int(hex_str[i:i+4], 16) < 0x8000
                    else int(hex_str[i:i+4], 16) - 0x10000
                    for i in range(0, len(hex_str), 4)
                ]
                all_samples.extend(samples)
            except Exception as e:
                print(f"⚠️ Error decoding data row: {e}")

    if not all_samples:
        print("⚠️ No valid samples found to plot.")
        return

    # Plot
    plt.figure(figsize=(14, 4))
    plt.plot(all_samples, label=lead_name, linewidth=1)
    plt.title(f"ECG Plot for {lead_name}")
    plt.xlabel("Sample Index")
    plt.ylabel("Amplitude (signed 16-bit)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

import csv
import matplotlib.pyplot as plt

def plot_ecg_from_csv(csv_file_path, lead_name):
    """
    Reads ECG data from a CSV file and plots the selected lead
    using sample index on the x-axis.

    Parameters:
        csv_file_path (str): Path to the CSV file.
        lead_name (str): One of ["Lead_I", "Lead_II", "V1", "V2", "V3", "V4", "V5", "V6"]

    Raises:
        ValueError: If the lead name is not in the header.
    """
    lead_values = []

    with open(csv_file_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        if lead_name not in reader.fieldnames:
            raise ValueError(f"'{lead_name}' not found in CSV headers.")

        for row in reader:
            try:
                lead_values.append(int(row[lead_name]))
            except ValueError:
                continue  # Skip rows with invalid data

    # X-axis: sample index
    x = list(range(len(lead_values)))

    # Plotting
    plt.figure(figsize=(10, 4))
    plt.plot(x, lead_values, linewidth=1.0)
    plt.title(f"ECG Plot - {lead_name}")
    plt.xlabel("Sample Index")
    plt.ylabel("Amplitude (int16)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_all_ecg_leads(csv_file_path):
    """
    Reads ECG data from a CSV file and plots each lead on a separate graph.
    """
    lead_names = ["Lead_I", "Lead_II", "V1", "V2", "V3", "V4", "V5", "V6"]
    ecg_data = {lead: [] for lead in lead_names}

    # Read data
    with open(csv_file_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            for lead in lead_names:
                try:
                    ecg_data[lead].append(int(row[lead]))
                except (ValueError, KeyError):
                    continue  # skip rows with invalid or missing values

    # Plot each lead separately
    for lead in lead_names:
        plt.figure(figsize=(10, 4))
        plt.plot(ecg_data[lead], linewidth=1.0)
        plt.title(f"ECG Lead: {lead}")
        plt.xlabel("Sample Index")
        plt.ylabel("Amplitude (int16)")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

def mqtt_thread_function():
    # mqtt_client = mqtt.Client()
    mqtt_client.username_pw_set(USERNAME, PASSWORD)
    mqtt_client.on_connect = on_connect
    mqtt_client.connect(BROKER, PORT, 60)
    mqtt_client.loop_forever()  # Blocking call in a thread

async def main():
    # loop = asyncio.get_event_loop()
    # loop.run_in_executor(None, mqtt_thread_function)  # ✅ don't await it

    await scan_ble_devices()
    # read_csv_and_plot("Lead_II", file_path)
    # plot_ecg_from_csv(file_path, "Lead_I")    
    while True:
        await asyncio.sleep(1)  # keep loop alive

if __name__ == "__main__":
    asyncio.run(main())
