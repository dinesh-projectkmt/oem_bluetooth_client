oom_live_packet = "6a07150ced0404007107140cf60404004007150c59050300a606150cb90504007406150cee0504004f06110c02060400ea05150c7f060400c905150ca30604009105170ca10603006905150cf40604003d05160c220703000b05160ccc0604005204150c6f0804004c03140c720904005902160c5e0a0300ef01150c450a0300f001150c640a0400cb01160c8d0a0300b201140ca30a03008601150cc10a04005f01150ce70a03000b01160c330b04000801150c3a0b0400eb00150c580b0400a900160c920b04000000019842d2f17b0000900020050000ff002c0101ffff0000000031c0c1000100000000000000000000000000000000"

ecg_data_packet = oom_live_packet[0:400]
epoch_time = int.from_bytes(bytes.fromhex(oom_live_packet)[200:208], byteorder='big')  # or 'big'
trigger_event = int.from_bytes(bytes.fromhex(oom_live_packet)[208:209], byteorder='big')  # or 'big'

int_x_position = int.from_bytes(bytes.fromhex(oom_live_packet)[209:211], byteorder='big')
int_y_position = int.from_bytes(bytes.fromhex(oom_live_packet)[211:213], byteorder='big')
int_z_position = int.from_bytes(bytes.fromhex(oom_live_packet)[213:215], byteorder='big')

battery = int.from_bytes(bytes.fromhex(oom_live_packet)[218:219], byteorder='big')
Lead_1 = int.from_bytes(bytes.fromhex(oom_live_packet)[219:220], byteorder='big')
Lead_2 = int.from_bytes(bytes.fromhex(oom_live_packet)[220:221], byteorder='big')
Lead_version = int.from_bytes(bytes.fromhex(oom_live_packet)[221:222], byteorder='big')
signal_rssi = int.from_bytes(bytes.fromhex(oom_live_packet)[229:230], byteorder='big', signed=True)


print(epoch_time)