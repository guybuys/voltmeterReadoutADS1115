from serial_manager import SerialManager


class ParameterManager:
    def __init__(self, serial_manager):
        self.serial_manager = serial_manager
        self.serial_connection = None
        self.serial_connected = False

    def open_serial_connection(self):
        try:
            esp32_port = self.serial_manager.find_esp32_port()
            self.serial_connection = self.serial_manager.open_connection(esp32_port)
            print(f"Opened {esp32_port}")
            self.serial_connected = True
        except IOError as e:
            print(e)

    def get_serial_connection_name(self):
        if self.serial_connection:
            return self.serial_connection.name
        return "/!\\ NOT CONNECTED"

    def close_serial_connection(self):
        if self.serial_connected and self.serial_connection:
            self.serial_connection.close()
            print("Serial connection closed.")
            self.serial_connected = False
        else:
            print("No serial connection to close.")

    def set_parameter(self, name, value):
        command = f"{name} {value}\n"
        self.serial_manager.write_to_serial(command.encode())

    def get_parameter(self, name):
        command = f"{name}\n"
        self.serial_manager.write_to_serial(command.encode())
        if self.serial_manager.esp32_connected:
            try:
                response = self.serial_manager.serial_connection.readline().decode().strip()
            except self.serial_manager.serial_connection.serialutil.SerialException:
                print("Timeout: No response received from the serial port")
                return "Unexpected", None

            if response:
                parts = response.split(' ')
                if len(parts) == 2:
                    parameter_name, parameter_value = parts
                    # Process the received parameter update
                    print(f"Received parameter '{parameter_name}' = {parameter_value}")
                    return parameter_name, parameter_value
                else:
                    print(f"ERROR: response does not contain 2 values: {response}")
                    return "Unexpected", response
            else:
                print(f"Error receiving parameter. '{response}' received")
                return "parameter manager error", response
        else:
            print(f"ESP32 not connected")
            return name, "0"

    '''
    def get_parameter(self, name):
        command = f"{name}\n"
        self.serial_manager.write_to_serial(command.encode())
        # response = self.serial_connection.readline().decode().strip()
        ### NEW CODE
        try:
            response = self.serial_connection.readline().decode().strip()
        except self.serial_connection.serialutil.SerialException:
            print("Timeout: No response received from the serial port")
            return "Unexpected", None

        ### END NEW CODE
        if response:
            parts = response.split(' ')
            if len(parts) == 2:
                parameter_name, parameter_value = parts
                # Process the received parameter update
                print(f"Received parameter '{parameter_name}' = {parameter_value}")
                return parameter_name, parameter_value
            else:
                print(f"ERROR: response does not contain 2 values: {response}")
                return "Unexpected", response
        else:
            print(f"Error receiving parameter. '{response}' received")
            return "parameter manager error", response
    '''

    def check_parameter_updates(self):
        parameter_updates = []
        if self.serial_manager.esp32_connected:
            while self.serial_connection.in_waiting:
                received_data = self.serial_connection.readline().decode().strip()
                if received_data:
                    parts = received_data.split(' ')
                    if len(parts) == 2:
                        parameter_name, parameter_value = parts
                        # Process the received parameter update
                        print(f"Received parameter update: {parameter_name} = {parameter_value}")
                        parameter_updates.append((parameter_name, parameter_value))
                else:
                    print(f"Error parameter updates. '{received_data}' received")

        return parameter_updates
