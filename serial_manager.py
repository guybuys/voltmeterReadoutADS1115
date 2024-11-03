import serial.tools.list_ports


class SerialManager:
    def __init__(self):
        self.serial_connection = None
        self.esp32_connected = False  # Track whether an ESP32 connection has been established

    def find_esp32_port(self):
        esp32_ports = [
            p.device
            for p in serial.tools.list_ports.comports()
            if 'Silicon Labs' in p.manufacturer
        ]
        if not esp32_ports:
            raise IOError("No ESP32 found")
        if len(esp32_ports) > 1:
            print("Multiple ESP32s found - using the first one")
        self.esp32_connected = True  # Set to True when ESP32 is found
        return esp32_ports[0]

    def open_connection(self, port):
        self.serial_connection = serial.Serial(port, 115200)  # 115200 is the default baud rate for ESP32
        self.esp32_connected = True  # Set to True when connection is opened
        return self.serial_connection  # Return the serial connection object

    def write_to_serial(self, data):
        if not self.esp32_connected:  # Check if ESP32 is connected
            print("No ESP32 connection. Cannot write data.")
            return

        if self.serial_connection is None or not self.serial_connection.is_open:
            print("Serial connection is not open. Cannot write data.")
            return

        try:
            if isinstance(data, str):
                data_bytes = data.encode()  # Convert string to bytes if necessary
            else:
                data_bytes = data  # Data is already in bytes format

            self.serial_connection.write(data_bytes)  # Write data to serial port
        except serial.SerialException as e:
            print("Error writing to serial port:", e)
            # Handle the error condition (e.g., retry, log, or exit gracefully)


'''
class SerialManager:
    def __init__(self):
        self.serial_connection = None

    def find_esp32_port(self):
        esp32_ports = [
            p.device
            for p in serial.tools.list_ports.comports()
            if 'Silicon Labs' in p.manufacturer
        ]
        if not esp32_ports:
            raise IOError("No ESP32 found")
        if len(esp32_ports) > 1:
            print("Multiple ESP32s found - using the first one")
        return esp32_ports[0]

    def open_connection(self, port):
        self.serial_connection = serial.Serial(port, 115200)  # 115200 is the default baud rate for ESP32
        return self.serial_connection  # Return the serial connection object

    def write_to_serial(self, data):
        if self.serial_connection is None or not self.serial_connection.is_open:
            print("Serial connection is not open. Cannot write data.")
            return

        try:
            if isinstance(data, str):
                data_bytes = data.encode()  # Convert string to bytes if necessary
            else:
                data_bytes = data  # Data is already in bytes format

            self.serial_connection.write(data_bytes)  # Write data to serial port
        except serial.SerialException as e:
            print("Error writing to serial port:", e)
            # Handle the error condition (e.g., retry, log, or exit gracefully)

'''
