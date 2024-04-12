import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QComboBox, QLabel, QPushButton, QSpinBox, QMessageBox,QTextBrowser
from PySide6.QtUiTools import QUiLoader
from PySide6.QtSerialPort import QSerialPortInfo
from pymodbus.client import ModbusSerialClient
import time
import logging
from  PySide6.QtCore import QTimer
import re
speeeed : int = 0

# 로깅을 다른 곳에 출력해주는 핸들러
class QTextBrowserLogger(logging.Handler):
    logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    def __init__(self,label):
        super(QTextBrowserLogger,self).__init__()
        self.label = label
    # 오버라이딩, 출력을 도와줌
    def emit(self,record):
        if(re.findall('SEND:',record.message)):
            self.order = record.message[18:21]
        elif(re.findall('RECV:',record.message)):
            self.label.setText(self.state_to_speed(record.message,self.order))

    def state_to_speed(self,message : str, order : str):
        list_message : list = message.split(" ")
        if(len(list_message) < 6):
            return
        if(list_message[2] == '0x4' and order == "0x3"):
            str_rpm =  list_message[4] + list_message[5][2:]
            int_rpm = int(str_rpm,16)
            if int_rpm >= 62536:
                int_rpm = 65536 % int_rpm
            return str(int_rpm) if str(int_rpm) else "0"
            
    def error_to_message(self,message : str, order : str):
        list_message : list = message.split(" ")
        if(len(list_message) < 6):
            pass
        else:
            if(list_message[2] == '0x4' and order == "0x1"):
                error_value = {
                    '0x0' : '알람 없음',
                    '0x1' : '저전압 검술',
                    '0x2' : '과전류',
                    '0x3' : '홀센서 이상',
                    '0x4' : '과부하 지속',
                    '0x5' : '파라미터 에러',
                    '0x7' : '과 온도 검출',
                    '0x8' : '모터 발진 검출',
                    '0x9' : '모터 구속 검출',
                    '0xA' : '전류센서 오류'
                }
                return error_value.get(list_message[5],"")
        
        # 16진수를 음수로
    def tohex(self,value : int):
        conv = (value + (1 << 16)) % (1 << 16)
        conv = hex(conv)
        return int(conv, 16)



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


        log_handler = QTextBrowserLogger(self.lb_rpm)
        logging.getLogger().addHandler(log_handler)

        # 비활성화 부분
        self.pb_close.setEnabled(False)

        # 브레이크 카운트
        self.brake_cnt : int = 1
        # 이동거리
        self.move_cnt : int = 0
        # 작동 여부
        self.running_cnt : int = 0
        # 연결 카운터
        self.conn_cnt : int = 0
        # RPM set 카운터
        self.set_cnt : int = 0

        # 기본 설정
        self.lb_power.setText("OFF")
        self.lb_locate.setText("정지")
        self.lb_move.setText(f"{self.move_cnt}mm")
        self.lb_brake.setText("ON")

        # 버튼 연결
        self.pb_open.clicked.connect(self.open)
        self.pb_close.clicked.connect(self.close)
        self.pb_set.clicked.connect(self.rpm_set)
        self.pb_up.clicked.connect(self.up)
        self.pb_down.clicked.connect(self.down)
        self.pb_stop.clicked.connect(self.stop)
        self.pb_reset.clicked.connect(self.aram_reset)
        self.pb_zero.clicked.connect(self.zero_set)
        self.pb_set_cancle.clicked.connect(self.set_false)


        # QSpinBox sp = QSpinBox()
        # sp.setDisplayIntegerBase

        portlist = QSerialPortInfo.availablePorts()

        for i, port_info in enumerate(portlist):
            self.cb_port.insertItem(i, port_info.portName())

        baurdrate_list = [115200]

        for i, baurdrate_info in enumerate(baurdrate_list):
            self.cb_speed.insertItem(i, str(baurdrate_info))

        # self.timer = QTimer(self)
        # self.timer.start(1000)
        # self.timer.timeout.connect(self.runnung)  # 1초마다 label의 텍스트를 변경합니다.
        # MainWindow 윈도우 표시
        self.ui.show()

    # 계속 돌고 있는 함수
    def runnung(self):
        state_run = self.client.read_input_registers(0x3,count=1,slave=1)
        # 최대 거리
        max_movement = 370
        min_speed = 6.6
        if (self.move_cnt < max_movement):
            self.pb_up.setEnabled(True)

        elif(self.move_cnt > -max_movement):
            self.pb_down.setEnabled(True)

        if(self.running_cnt == 1):
            self.lb_locate.setText("작동 중....")
            self.move_cnt += min_speed * (self.set_rpm/100)
            self.lb_move.setText(str(round(self.move_cnt,1))+"mm")
            if(self.move_cnt > 370):
                print("over")
                self.stop()
                self.pb_up.setEnabled(False)
                
        elif(self.running_cnt == -1):
            self.lb_locate.setText("작동 중....")
            self.move_cnt -= min_speed * (self.set_rpm/100)
            self.lb_move.setText(str(round(self.move_cnt,1))+"mm")
            if(self.move_cnt < -370):
                print("over")
                self.stop()
                self.pb_down.setEnabled(False)


            


    def break_value(self):
        if(self.brake_cnt == 1):
            self.lb_brake.setText("ON")
        else:
            self.lb_brake.setText("OFF")



    # 16진수를 음수로
    def tohex(self,value : int):
        conv = (value + (1 << 16)) % (1 << 16)
        conv = hex(conv)
        return int(conv, 16)
    
    def open(self):
        str_port = self.cb_port.currentText()
        int_buard = int(self.cb_speed.currentText())
        self.client = ModbusSerialClient(port=str_port, framer='rtu',baudrate=int_buard)
        try:
            con = self.client.connect()
            if(con == True):
                reg = self.client.write_register(address=120, value=1, slave=1)
                self.lb_power.setText("ON")
                self.conn_cnt = 1
                # QLabel lb = QLabel()
                # lb.setText
                self.pb_open.setEnabled(False)
                self.cb_port.setEnabled(False)
                self.cb_speed.setEnabled(False)
                self.pb_close.setEnabled(True)
        except Exception as e:
            print(e)

    def close(self):
        self.client.close()
        reg = self.client.write_register(address=120, value=0, slave=1)
        self.lb_power.setText("OFF")
        self.conn_cnt = 0

    def up(self):
        if(self.conn_cnt == 0):
            return
        elif(self.set_cnt == 0):
            return # 나중에 수정
        if(self.brake_cnt == 1):
            self.brake_cnt = 0
            self.break_value()
            off = self.client.write_register(address=120, value=0x0100, slave = 1)
        self.running_cnt = 1
        reg = self.client.write_register(address=121, value=self.set_rpm, slave=1)
    
    def down(self):
        if(self.conn_cnt == 0):
            return
        elif(self.set_cnt == 0):
            return # 나중에 수정
        if(self.brake_cnt == 1):
            self.brake_cnt = 0
            self.break_value()
            off = self.client.write_register(address=120, value=0x0100, slave = 1)
        self.down_set_rpm = -(self.set_rpm)
        print(self.down_set_rpm)
        down_rpm = self.tohex(self.down_set_rpm)
        reg = self.client.write_register(address=121, value=down_rpm, slave=1)
        self.running_cnt = -1
        # 여기까지
    
    def stop(self):
        if(self.conn_cnt == 0):
            return
        elif(self.set_cnt == 0):
            return # 나중에 수정
        time.sleep(0.5)
        reg = self.client.write_register(address=121,value=0,slave=1)
        self.lb_locate.setText("정지")
        time.sleep(0.5)
        stop = self.client.write_register(address=120, value=0x0101, slave = 1)
        self.running_cnt = 0
        self.brake_cnt = 1
        self.break_value()
    
    def rpm_set(self):
        self.set_cnt = 1
        self.set_rpm = self.sp_rpm.value()
        self.sp_rpm.isReadOnly()
        self.pb_set.setEnabled(False)
        self.pb_set_cancle.setEnabled(True)


    def zero_set(self):
        # self.move_cnt = 0
        # self.lb_move.setText("0mm")
        off = self.client.write_register(address=121, value=1000, slave = 1)


    def set_false(self):
        self.set_cnt = 0
        self.pb_set.setEnabled(True)
        self.pb_set_cancle.setEnabled(False)
        self.set_rpm = 0
    
    def aram_reset(self):
        # state = self.client.read_input_registers(0x1,count=1,slave=1)
        state_run = self.client.read_input_registers(0x3,count=1,slave=1)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())


# 1번 알람 리셋 기능 추가
# 현재 속도 및 이동거리 표기