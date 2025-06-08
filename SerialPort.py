import serial
import time

def read_arduino_data(serial_port, baud_rate, output_file, duration):
    try:
        # Open the serial port
        ser = serial.Serial(serial_port, baud_rate, timeout=1)
        time.sleep(2)  # Wait for the serial connection to initialize

        start_time = time.time()
        with open(output_file, 'w') as file:
            while (time.time() - start_time) < duration:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').rstrip()
                    print(line)
                    file.write(line + '\n')

        ser.close()
    except Exception as e:
        print(f"Error: {e}")

def reset_arduino(serial_port, baud_rate):
    try:
        # Open the serial port
        ser = serial.Serial(serial_port, baud_rate)
        time.sleep(2)  # Wait for the serial connection to initialize

        # Toggle DTR to reset the Arduino
        ser.setDTR(False)
        time.sleep(0.5)
        ser.setDTR(True)

        ser.close()
        print("Arduino reset via DTR signal.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    serial_port = 'COM5'  # Update with your Arduino serial port
    baud_rate = 9600
    duration = 15  # Duration in seconds to read data

    num_files = 100  # Number of files to create

    for i in range(num_files):
        output_file = f'arduino_data_{i+1}.txt'
        print(f'Starting data collection for {output_file}')
        read_arduino_data(serial_port, baud_rate, output_file, duration)
        reset_arduino(serial_port, baud_rate)
        time.sleep(1)  # Optional: wait a bit between measurements
