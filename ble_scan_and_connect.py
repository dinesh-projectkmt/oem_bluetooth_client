import time
import asyncio
from bleak import BleakScanner, BleakClient

bluetooth_device_name = "OOM_CARDIO"
oom_serial_number = "KE121062500004"

async def scan_ble_devices():
    print("🔍 Scanning for BLE devices (1 second)...")
    devices = await BleakScanner.discover(timeout=1, return_adv=True)

    for address, (device, adv_data) in devices.items():
        if device.name == bluetooth_device_name:
            print(f"✅ Device found: {device.name} at {address}")
            print(adv_data.manufacturer_data)

            for company_id, data_bytes in adv_data.manufacturer_data.items():
               print(f"Company ID: {company_id}")
               print(f"Raw bytes: {data_bytes}")

                # Now you can decode
               raw_serial = int.from_bytes(data_bytes[0:2], 'big')
               raw_year = int.from_bytes(data_bytes[2:3], 'big')
               raw_month = int.from_bytes(data_bytes[3:4], 'big')
               raw_day = int.from_bytes(data_bytes[4:5], 'big')
               raw_version = int.from_bytes(data_bytes[5:6], 'big')
               oom_serial_gen = f"KE{raw_version:01d}{raw_day:02d}{raw_month:02d}{raw_year:02d}{raw_serial:05d}"
               print(oom_serial_gen)

               if(oom_serial_number == oom_serial_gen):
                   print("Device Found, Trying to connect")
                   await connect_and_discover(device.name, address)                

            return device

    print("❌ Device not found.")

async def connect_and_discover(device_name, device_address):
    print(f"🔗 Connecting to {device_name} at {device_address}...")
    async with BleakClient(device_address) as client:
        if client.is_connected:
            print(f"✅ Connected to {device_name}!")
            await discover_services_and_characteristics(client)
        else:
            print("❌ Failed to connect.")

async def discover_services_and_characteristics(client):
    print("🔍 Discovering services and characteristics:")
    for service in client.services:
        # print(f"\nService: {service.uuid} | {service.description}")
        for char in service.characteristics:
            props = ', '.join(char.properties)
            # print(f"  Characteristic: {char.uuid} | {char.description} | Properties: [{props}]")
            
            if(service.uuid == "0000180a-0000-1000-8000-00805f9b34fb"):
                if(char.uuid == "00002a24-0000-1000-8000-00805f9b34fb"):
                    await read_characteristic(client, char.uuid)
                if(char.uuid == "00002a26-0000-1000-8000-00805f9b34fb"):
                    await read_characteristic(client, char.uuid)
            if(service.uuid == "0000180d-0000-1000-8000-00805f9b34fb"):
                if 'notify' in char.properties or 'indicate' in char.properties:

                    if(char.uuid == "00001801-0000-1000-8000-00805f9b34fb"):
                        print(f"🔔 Enabling notifications on {char.uuid} under {service.uuid}")
                        await write_characteristic(client, char.uuid, bytes.fromhex("0004190615016883CA00"))
                        await asyncio.sleep(0.2)
                        await enable_notifications(client, char.uuid)
                    if(char.uuid == "00001802-0000-1000-8000-00805f9b34fb"):
                        # print("data writteed")
                        await write_characteristic(client, char.uuid, bytes.fromhex("010000"))

async def read_characteristic(client, characteristic_uuid):
    try:
        data = await client.read_gatt_char(characteristic_uuid)
        print(f"✅ Data read from {characteristic_uuid}: {data.decode('utf-8').strip()}")
        return data

    except Exception as e:
        print(f"❌ Failed to read from {characteristic_uuid}: {e}")
        return None


async def write_characteristic(client, characteristic_uuid, data_to_write):
    try:
        print(f"✏️ Writing to {characteristic_uuid}: {data_to_write}")
        await client.write_gatt_char(characteristic_uuid, data_to_write)
        print(f"✅ Write successful to {characteristic_uuid}")
        await asyncio.sleep(0.5)
    except Exception as e:
        print(f"❌ Failed to write to {characteristic_uuid}: {e}")
        
def notification_handler(sender, data):
    try:
        decoded = data.decode('utf-8').strip()
        print(f"🔔 Notification from {sender}: {decoded}")
    except:
        # Fallback to hex if data is not UTF-8
        print(f"🔔 Notification from {sender}: {(data.hex())}")

async def enable_notifications(client, characteristic_uuid):
    try:
        await client.start_notify(characteristic_uuid, notification_handler)
        print(f"✅ Notifications enabled on {characteristic_uuid}")
    except Exception as e:
        print(f"❌ Failed to enable notifications: {e}")


async def main():
    await scan_ble_devices()

    # Keep the event loop alive to continue receiving notifications
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())