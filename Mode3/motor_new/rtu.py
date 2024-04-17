import crcmod.predefined
import struct
import serial

class rtu_motor():

    def to_byte(self,address):
        reg_data : list = []
        send_message = self._make_msg(address)
        self.ser.write(send_message)
        if(self.ser.readable()):
            recv = self.ser.readline()
            for _ in recv:
                reg_data.append(_)
            if(len(reg_data) >= 7):
                print("성공")
                print(reg_data)
            return reg_data

    def open(self,port:str,baurd:int):
        """
        그저 시리얼 연결
        """
        self.ser = serial.Serial(port, baurd,timeout=1,parity="N")
        if(self.ser):
            print("연결성공")
        else:
            print("연결실패")


    def close(self):
        self.ser.close()
        if(self.ser.is_open()):
            print("실패")
        else:
            print("연결 종료")

    
    def _make_msg(self,list_msg : list[int]) -> bytes:
        """
        리스트 형태로 메세지를 받아 bytes로 전달
        """
        msg = struct.pack(">BBHH", list_msg[0],list_msg[1],list_msg[2],list_msg[3])
        crc16 = crcmod.predefined.mkPredefinedCrcFun('modbus')
        crc = crc16(msg)
        msg += struct.pack('<H',crc)
        return msg
    
    
    def motor_on(self):
        """
        그저 모터 ON
        """
        on_msg = [1,6,120,1]
        self.to_byte(on_msg)
        print("모터 ON")

    def up(self):
        up_msg = [0x1,0x6,0x0079,100]
        self.to_byte(up_msg)
        print(up_msg[3])
    
    def down(self):
        return
    
    def stop(self):
        return    
    
    def rpm_state(self):
        """
        그저 모터 상태
        """
        rpm_state_msg = [0x1,0x4,0x3,0x1]
        self.to_byte(rpm_state_msg)
        print("현재 속도")
            

    def rpm_set(self):
        return

# 제어용 화면 하나 더 만들기
# 기존에 함수만 사용하면 되서 어려운 일은 없을 듯

a = rtu_motor()
a.open("COM3",115200)
a.motor_on()
a.up()
a.rpm_state()