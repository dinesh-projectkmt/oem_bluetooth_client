import asyncio
import paho.mqtt.client as mqtt
from bleak import BleakScanner, BleakClient
import json
import time

bluetooth_device_name = "OOM_CARDIO"
oom_serial_number = "KE121062500004"
web_patient_id = "67c6de22a69621459c6ae07e"

BROKER = "oomcardiodev.projectkmt.com"      # replace with your broker
PORT = 1884                       # default port for non-TLS
TOPIC = "oom/ecg/rawData/67c6de22a69621459c6ae07e"            # replace with your topic
USERNAME = "kmt"        # replace with your MQTT username
PASSWORD = "Kmt123"        # replace with your MQTT password

# Callback when connection is established
async def on_connect(client, userdata, flags, rc):
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

write_once = False

# Notification handler
def notification_handler(sender, data):   
    try:
        live_ecg_json["data"] = data.hex()[0:400]
        live_ecg_json["dateTime"] = int.from_bytes(bytes.fromhex(data.hex())[200:208], byteorder='big')  # or 'big'
        live_ecg_json["patient"] = web_patient_id

        Lead_1 = int.from_bytes(bytes.fromhex(data.hex())[219:220], byteorder='big')
        Lead_2 = int.from_bytes(bytes.fromhex(data.hex())[220:221], byteorder='big')

        if(Lead_1 == 0 and Lead_2 == 0):
            Lead = 0
        else:
            Lead = 1

        live_ecg_json["leadDetection"] = Lead

        live_ecg_json["trigger"] = int.from_bytes(bytes.fromhex(data.hex())[208:209], byteorder='big')

        if(int.from_bytes(bytes.fromhex(data.hex())[221:222], byteorder='big') == 255):
            ecgVersion = 2
        else:
            ecgVersion = 5

        live_ecg_json["ecgVersion"] = ecgVersion
        print(live_ecg_json)
        # print(f"🔔 Notification from {sender}: {data.hex()}")
    except:
        live_ecg_json["data"] = data.hex()[0:400]
        live_ecg_json["dateTime"] = int.from_bytes(bytes.fromhex(data.hex())[200:208], byteorder='big')  # or 'big'
        live_ecg_json["patient"] = web_patient_id

        Lead_1 = int.from_bytes(bytes.fromhex(data.hex())[219:220], byteorder='big')
        Lead_2 = int.from_bytes(bytes.fromhex(data.hex())[220:221], byteorder='big')

        if(Lead_1 == 0 and Lead_2 == 0):
            Lead = 0
        else:
            Lead = 1

        live_ecg_json["leadDetection"] = Lead

        live_ecg_json["trigger"] = int.from_bytes(bytes.fromhex(data.hex())[208:209], byteorder='big')

        if(int.from_bytes(bytes.fromhex(data.hex())[221:222], byteorder='big') == 255):
            ecgVersion = 2
        else:
            ecgVersion = 5

        live_ecg_json["ecgVersion"] = ecgVersion
        mqttclient.publish("ecg/rawData/"+web_patient_id, json.dumps(live_ecg_json))
        print(live_ecg_json)
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
                            await write_characteristic(client, char.uuid, bytes.fromhex("0004190615016883CA00"))
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

# Entry point
async def main():
    await scan_ble_devices()

    # # Start listening loo
    while True:
        await asyncio.sleep(1)  # Keep the loop alive for notifications

if __name__ == "__main__":
    asyncio.run(main())
