TBot - Main code to run T-Bot

DCMotorTest - Simple example to drive motors using the TB6612FNG driver board (used to calibrate motors)

BluetoothChangeName - Used to set BAUD rate, set name for T-Bot and get MAC address

BTListen - Read in data coming from Bluetooth controllers (useful if you want to make your own controller)

Python - Python code to retrieve and analyse data from the T-Bot

TBotLibraries.zip - Libraries require to run the T-Bot. These can be extracted directly into the Arduino libraries folder.

Ultrasound - Simple example to interrogate the HC-SR04 ultrasound module

ReadGyro - Simple example to interrogate MPU-6050 sensor

SchedulerExample - A simple example to show you how to use a schedular instead of nested loops.



TBot_Joystick_Python_PYBLUEZ - Bluetooth joystick written in python - Requires python-bluez and Bluez

TBot_Joystick_Python_SOCKET - Bluetooth joystick written in python - Python3


Install the arduino IDE form https://www.arduino.cc. Import the libraries by extracting TBotLibraries.zip directly in the Arduino library folder. Open TBot.ino and click on the upload button to send the code to your T-Bot.

You will need to select
 
Tools->Board->Arduino Nano

Note for Windows users:

Windows users need to use the old boot loader. In the Arduino IDE select TOOLS > PROCESSOR > in the pull down menu change ATmega328P to ATmega328P (Old Bootloader).

