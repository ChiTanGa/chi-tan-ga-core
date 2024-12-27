import serial
import time

# Replace '/dev/tty.usbmodemXXXX' with the actual port name
# You can find this in the Arduino IDE under Tools > Port
# It often looks like /dev/tty.usbmodemXXXX or /dev/tty.usbserial-XXXX
port = '/dev/tty.usbmodem1101'
baud_rate = 9600  # Match the baud rate with the Arduino code

try:
    # Open the serial connection
    ser = serial.Serial(port, baud_rate, timeout=1)
    time.sleep(2)  # Give time for Arduino to reset (optional)

    print("Reading from Arduino:")
    while True:
        # Read a line from the Arduino
        line = ser.readline().decode('utf-8').strip()
        if line:
            print("Arduino:", line)

except serial.SerialException as e:
    print(f"Error opening serial port: {e}")

except KeyboardInterrupt:
    print("Exiting program...")

finally:
    # Close the serial connection
    if 'ser' in locals() and ser.is_open:
        ser.close()