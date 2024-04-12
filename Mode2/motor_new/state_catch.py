error : str = 'RECV: 0x1 0x2 0x0 0x5 0xA0 0x18'

def error_to_message(message : str):
    list_message : list = message.split(" ")
    if(list_message[2] == '0x2'):
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
        return error_value.get(list_message[4],"오류")




print(error_to_message(error))