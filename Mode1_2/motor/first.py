from pymodbus.client import ModbusSerialClient
import logging
import time

# 로깅 설정
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)



client = ModbusSerialClient(
  method = 'rtu'
  ,port='COM11'
  ,baudrate=115200
  ,parity = 'N'
  ,timeout=1
  )

connection = client.connect()

if(connection):
    print('연결 성공')
    # 전원 On
    registers = client.write_register(address=120, value=1, slave=1)
    time.sleep(2)

    # # em blake off
    # registers = client.write_register(address=120, value=0x0300, slave=1)
else:
    print("연결 실패")

client.close()