import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QComboBox, QLabel, QPushButton, QSpinBox, QMessageBox,QTextBrowser
from PySide6.QtUiTools import QUiLoader
from  PySide6.QtCore import QTimer
import serial
import struct
import crcmod
import serial.tools
import serial.tools.list_ports

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # UI 파일 로드
        loader = QUiLoader()
        self.ui = loader.load("C:\DEV\Code\Python\motor_new\lift_increase.ui")
        self.setFixedSize(430,270)

        #스핀박스
        self.sp_rpm = self.ui.findChild(QSpinBox, "sp_rpm")

        # 콤보박스
        self.cb_speed = self.ui.findChild(QComboBox, "cb_speed")
        # self.cb_rpm = self.ui.findChild(QComboBox, "cb_rpm")
        self.cb_port = self.ui.findChild(QComboBox, "cb_port")

        # 버튼
        self.pb_open = self.ui.findChild(QPushButton, "pb_open")
        self.pb_close = self.ui.findChild(QPushButton, "pb_close")
        self.pb_set = self.ui.findChild(QPushButton, "pb_set")
        self.pb_up = self.ui.findChild(QPushButton, "pb_up")
        self.pb_down = self.ui.findChild(QPushButton, "pb_down")
        self.pb_stop = self.ui.findChild(QPushButton, "pb_stop")
        self.pb_reset = self.ui.findChild(QPushButton, "pb_reset")
        self.pb_zero = self.ui.findChild(QPushButton, "pb_zero")
        self.pb_set_cancle = self.ui.findChild(QPushButton, "pb_set_cancle")

        # 라벨
        self.lb_power = self.ui.findChild(QLabel, "lb_power")
        self.lb_locate = self.ui.findChild(QLabel, "lb_locate")
        self.lb_move = self.ui.findChild(QLabel, "lb_move")
        self.lb_brake = self.ui.findChild(QLabel, "lb_brake")
        self.lb_rpm = self.ui.findChild(QLabel, "lb_rpm")

        #텍스트브라우저
        self.tb_info = self.ui.findChild(QTextBrowser, "tb_info")

        # 기본 설정
        self.lb_power.setText("OFF")
        self.lb_locate.setText("정지")
        self.lb_move.setText("0")
        self.lb_brake.setText("ON")
        self.lb_rpm.setText("0")

        # 기본 변수 설정
        self.brk_cnt : int = 1
        self.set_cnt : int = 0
        self.con_cnt : int = 0
        self.run_move : int = 0
        self.up_down : int = 0
        self.max : int = 395
        self.zero_cnt : int = 0

        # 버튼 연결
        self.pb_open.clicked.connect(self.open)
        self.pb_close.clicked.connect(self.close)
        self.pb_set.clicked.connect(self.rpm_set)
        self.pb_up.clicked.connect(self.up)
        self.pb_down.clicked.connect(self.down)
        self.pb_stop.clicked.connect(self.stop)
        self.pb_zero.clicked.connect(self.zero_set)
        self.pb_set_cancle.clicked.connect(self.set_false)

        portlist = serial.tools.list_ports.comports()
        i = 0
        for port_info in portlist:
            i+=1
            self.cb_port.insertItem(i, port_info.device)

        baurdrate_list = [115200]

        for i, baurdrate_info in enumerate(baurdrate_list):
            self.cb_speed.insertItem(i, str(baurdrate_info))

        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.movement)  # 1초마다 label의 텍스트를 변경합니다.
        self.ui.show()

    ### 함수 영역
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

    def open(self):
        """
        그저 시리얼 연결
        """
        port = self.cb_port.currentText()
        buard = int(self.cb_speed.currentText())
        self.ser = serial.Serial(port, buard, timeout=0.5,parity="N")
        try:
            if(self.ser):
                self.motor_on()
                self.lb_power.setText("ON")
                self.con_cnt = 1
                self.pb_open.setEnabled(False)
                self.cb_port.setEnabled(False)
                self.cb_speed.setEnabled(False)
                self.pb_close.setEnabled(True)
            else:
                print("연결실패")
        except Exception as e:
            self.tb_info(f"연결 실패 : {e}")

    def close(self):
        if(self.ser.is_open == True):
            self.ser.close()
            self.lb_power.setText("OFF")
            self.pb_close.setEnabled(False)
            self.pb_open.setEnabled(True)
        else:
            self.tb_info.setPlainText("이미 닫혀있는 포트 입니다.")

    
    def _make_msg(self,list_msg : list[int]) -> bytes:
        msg = struct.pack(">BBHH", list_msg[0],list_msg[1],list_msg[2],list_msg[3])
        crc16 = crcmod.predefined.mkPredefinedCrcFun('modbus')
        crc = crc16(msg)
        msg += struct.pack('<H',crc)
        return msg
    
    
    def motor_on(self):
        on_msg = [1,6,120,1]
        self.to_byte(on_msg)
        print("모터 ON")

    def rpm_zero(self):
        zero_message = [1,6,121,0]
        self.to_byte(zero_message)

    def up(self):
        if self.brk_cnt == 1:
            self.unlock_brake()
        up_msg = [0x1,0x6,0x0079,self.set_rpm]
        _tf_list = self.to_byte(up_msg)
        if(_tf_list != []):
            self.up_down = 1
    
    def down(self):
        if self.brk_cnt == 1:
            self.unlock_brake()
        _set_rpm = self.tohex(-(self.set_rpm))
        up_msg = [0x1,0x6,0x0079,_set_rpm]
        _tf_list = self.to_byte(up_msg)
        if(_tf_list != []):
            self.up_down = -1

    def stop(self):
        self.rpm_zero()
        motor_stop = [1,6,120,0x0101]
        tf_list = self.to_byte(motor_stop)
        if(tf_list != []):
            self.lb_brake.setText("ON")
            self.brk_cnt = 1
            self.up_down = 0        
    
    def rpm_state(self):
        """
        그저 모터 상태
        """
        rpm_state_msg = [0x1,0x4,0x3,0x1]
        tf_list = self.to_byte(rpm_state_msg)
        if tf_list != []:
            print(tf_list)
            if tf_list[3] > 0:
                manus_val = hex(tf_list[4]) + (hex(tf_list[3])[2:])
                minus_rpm = (manus_val) - 65536
                self.lb_rpm.setText(str(minus_rpm))
            else:
                self.lb_rpm.setText(str(tf_list[4]))   
            
    def rpm_set(self):
        self.set_cnt = 1
        self.set_rpm = self.sp_rpm.value()
        self.sp_rpm.isReadOnly(False)
        self.pb_set.setEnabled(False)
        self.pb_set_cancle.setEnabled(True)

    def set_false(self):
        self.set_cnt = 0
        self.pb_set.setEnabled(True)
        self.pb_set_cancle.setEnabled(False)
        self.set_rpm = 0


    def unlock_brake(self):
        """
        브레이크 푸는 함수
        """
        unlock_msg = [0x1,0x6,120,0x0100]
        _tf_list : list = self.to_byte(unlock_msg)
        if(_tf_list != []):
            self.lb_brake.setText("OFF")

    # 16진수를 음수로
    def tohex(self,value : int):
        conv = (value + (1 << 16)) % (1 << 16)
        conv = hex(conv)
        return int(conv, 16)
    
    def movement(self):
        self.rpm_state()
        speed : float = 6.6
        if self.zero_cnt == 1: # 원점 셋을 하면
            if self.run_move  < 0: # 이동거리가 0이면
                self.pb_up.setEnabled(True) # 업버튼 선택 불가
            if abs(self.run_move) < self.max - 1:
                self.pb_down.setEnabled(True)
            if self.up_down == 1: # up 이면
                if self.run_move < 0:
                    self.run_move += speed * (self.set_rpm / 100)
                    self.lb_move.setText(str(round(self.run_move,2)))
                elif self.run_move + 13.2 >=0:
                    while True:
                        self.stop()
                        if self.brk_cnt == 1:
                            self.run_move = 1
                            self.lb_move.setText(self.run_move)
                            self.pb_up.setEnabled(False) # 업버튼 선택 불가
                            break
                    
            elif self.up_down == -1:
                if abs(self.run_move) < self.max:
                    self.run_move -= speed * (self.set_rpm / 100)
                    self.lb_move.setText(str(round(self.run_move,2)))
                elif abs(self.run_move) - 13.2 < self.max:
                    while True:
                        self.stop()
                        if self.brk_cnt == 1:
                            self.run_move = -(self.max - 1)
                            self.lb_move.setText(self.run_move)
                            self.pb_down.setEnabled(False) # 업버튼 선택 불가
                            self.pb_up.setEnabled(True) # 업버튼 선택 불가
                            break

    def zero_set(self):
        self.run_move = 0
        self.lb_move.setText('0')
        self.zero_cnt = 1
        self.pb_up.setEnabled(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())