import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QComboBox, QLabel, QPushButton, QTextBrowser, QMessageBox, QTextEdit, QLineEdit
from PySide6.QtUiTools import QUiLoader
from PySide6.QtSerialPort import QSerialPortInfo
from pymodbus.client import ModbusSerialClient

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # UI 파일 로드
        loader = QUiLoader()
        self.ui = loader.load("C:\DEV\Code\Python\motor\lift.ui")
        self.setFixedSize(430,270)
        



        # 콤보박스
        self.cb_speed = self.ui.findChild(QComboBox, "cb_speed")
        self.cb_rpm = self.ui.findChild(QComboBox, "cb_rpm")
        self.cb_port = self.ui.findChild(QComboBox, "cb_port")

        # 버튼
        self.pb_open = self.ui.findChild(QPushButton, "pb_open")
        self.pb_close = self.ui.findChild(QPushButton, "pb_close")
        self.pb_set = self.ui.findChild(QPushButton, "pb_set")
        self.pb_up = self.ui.findChild(QPushButton, "pb_up")
        self.pb_down = self.ui.findChild(QPushButton, "pb_down")
        self.pb_stop = self.ui.findChild(QPushButton, "pb_stop")

        # 라벨
        self.lb_power = self.ui.findChild(QLabel, "lb_power")
        self.lb_locate = self.ui.findChild(QLabel, "lb_locate")
        self.lb_move = self.ui.findChild(QLabel, "lb_move")

        # 비활성화 부분
        self.pb_close.setEnabled(False)

        # 기본 설정
        self.lb_power.setText("OFF")
        self.lb_locate.setText("정지")
        self.lb_move.setText("0mm")

        portlist = QSerialPortInfo.availablePorts()

        for i, port_info in enumerate(portlist):
            self.cb_port.insertItem(i, port_info.portName())

        baurdrate_list = [115200]

        for i, baurdrate_info in enumerate(baurdrate_list):
            self.cb_speed.insertItem(i, str(baurdrate_info))


        # MainWindow 윈도우 표시
        self.ui.show()


    # 16진수를 음수로
    def tohex(self,value : int):
        conv = (value + (1 << 16)) % (1 << 16)
        conv = hex(conv)
        return int(conv, 16)
    
    def open(self):
        str_port = self.cb_port.currentText()
        int_buard = self.cb_speed.currentText()
        self.client = ModbusSerialClient(port=str_port, framer='rtu',baudrate=int_buard)
        try:
            con = self.client.connect()
            if(con == True):
                reg = self.client.write_registers(address=0, values=1, slave=1)
                self.lb_power.Text("ON")
                self.pb_open.setEnabled(False)
                self.cb_port.setEnabled(False)
                self.cb_speed.setEnabled(False)
        except Exception as e:
            return

    def close(self):
        self.client.close()
        self.lb_power.Text("OFF")
        reg = self.client.write_registers(address=0, values=0, slave=1)



    def up(self):
        return
    def down(self):
        return
    def stop(self):
        return
    def zero_set(self):
        return






if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())