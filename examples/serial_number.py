serial_number = "KE121112300001"
print(serial_number)

oom_version = int(serial_number[2:3])
oom_day = int(serial_number[3:5])
oom_month = int(serial_number[6:8])
oom_year = int(serial_number[9:11])
oom_serial_num = int(serial_number[12:16])

print(oom_version)
print(oom_day)
print(oom_month)
print(oom_year)
print(oom_serial_num)
