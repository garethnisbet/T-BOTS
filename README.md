## File Structure:

[BluetoothChangeName](/BluetoothChangeName) - Used to set BAUD rate, set name for T-Bot and get MAC address.

[BTListen](/BTListen) - Read in data coming from Bluetooth controllers (useful if you want to make your own controller).

[DCMotorTest](/DCMotorTest) - Simple example to drive motors using the TB6612FNG driver board (used to calibrate motors).

[Python](/Python) - Python code to retrieve and analyse data from the T-Bot.

[ReadGyro](/ReadGyro) - Simple example to interrogate MPU-6050 sensor.

[SchedulerExample](/SchedulerExample) - A simple example to show you how to use a schedular instead of nested loops.

[TBot](/TBot) - Main code to run T-Bot.

[TBot_Joystick_Python_PYBLUEZ](/TBot_Joystick_Python_PYBLUEZ) - Bluetooth joystick written in python - Requires python-bluez and Bluez - works on Linux.

[TBot_Joystick_Python_Pyserial](/TBot_Joystick_Python_Pyserial) - Bluetooth joystick written in python - Works on Windows and Mac.

[TBot_Joystick_Python_SOCKET](/TBot_Joystick_Python_SOCKET) - Bluetooth joystick written in python - Python3 - works on Linux.

[TBotLibraries.zip](/TBotLibraries.zip) - Libraries required to run the T-Bot. These can be extracted directly into the Arduino libraries folder.

[Ultrasound](/Ultrasound) - Simple example to interrogate the HC-SR04 ultrasound module.


## Usage:
1. Install the arduino IDE from https://www.arduino.cc.
2. Import the libraries by extracting [TBotLibraries.zip](/TBotLibraries.zip) directly in the Arduino library folder.
3. You will need to select ```Tools > Board > Arduino Nano```.
4. Open TBot.ino and click on the upload button to send the code to your T-Bot.

💡 **Note:** Windows users need to use the old boot loader. In the Arduino IDE select ```TOOLS > PROCESSOR > in the pull down menu change ATmega328P to ATmega328P (Old Bootloader)```.
