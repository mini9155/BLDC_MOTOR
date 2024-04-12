# BLDC_MOTOR
Control BLDC motor.


# BLDC 모터 제어.

## BLDC AC 모터를 제어하기 위한 프로젝트

- 방식 : Modbus RTU
- 사용 언어 : Python
- 사용모듈
  - ver 1 : pymodbus, PySide6, sys
  - ver 2 : pymodbus, PySide6, logging, time, sys
  - ver 3 : Serial, sturct, crcmod, sys
- 제작 기간 : 1달
- 통신 방식 : RS-485

1. 모드버스 RTU
  - 모드버스는 Master - slave로 이루어진 프로토콜로 이 프로젝트를 진행하면서 처음 알게 되었다.
  - 슬레이브 주소 - 1byte, 함수 코드 1 byte, 주소 High - 1byte, 주소 Low - 1byte, Data - 2byte, CRC16 - 2bye
  - ex) 0x1 0x6 0x78 0x0 0x1 0xc8 0x13 <- 이런식으로 구성이 된다
  - 끝에 2자리인 CRC16 (0xc8, 0x13)은 계산식이 따로 있으나 pymodbus 혹 crcmod의 함수를 빌려쓰면 편하다

2. 버전 및 방식을 바꾼 이유
   - 버전1은 아무 지식도 없는 상태에서 모터 제어부터 시작해보기 위해 간단한 인터페이스와 작동 위주의 코드를 작성하기 시작했다
   - 버전2는 간단한 기능 명령 처리 후 어느 정도의 기능 처리 및 이동 거리를 계산하기 위해 logging 모듈을 사용하기로 하였다.
   - 버전3은 logging 모듈로 데이터를 받아올 시 받아들이는 데이터가 많고 그 중에서 원하는 메세지만 받아들이기에는 변칙적인 부분이 있어 Serial 모듈을 이용하게 되었다.
  
3. 버전을 걸치면서 배우게 된 점
   - 버전2에서는 logging 중 emit 이란 모듈을 통해 메세지를 받아오는 방법을 배웠다.
   - 버전2에서 버전3로 넘어가기 전 라이브러리의 코드를 살펴보며 굳이 외부 모듈을 쓰지 않아도 내가 원하는 영역을 구현시킬 수 있는 힌트를 얻었다. 클래스의 구조 등을 알게 되었다.
   - 버전 3에서는 메세지를 바이트로 쓰는 방법과 바이트로 패킹을 하는 struct 모듈을 사용해보며 새로운 부분을 알게 되었다.


