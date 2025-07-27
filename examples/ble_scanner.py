import asyncio
from bleak import BleakScanner

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
                   print("serial number matched, we can try to connect oom patch")

            return device

    print("❌ Device not found.")


def main():
    asyncio.run(scan_ble_devices())

if __name__ == "__main__":
    main()