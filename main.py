import serial
import paramiko
import tkinter as tk
import time

class SwitchConfigTool:
    def __init__(self):
        self.connection = None

    def main(self):
        connection_type = input("Enter 'COM' to connect via COM or 'ssh' to connect via SSH: ")

        if connection_type == 'COM':
            port_address = input("Enter the COM port address (e.g., COM7): ")
            self.connect_via_serial(port_address)
        elif connection_type == 'ssh':
            ssh_address = input("Enter the SSH address: ")
            ssh_username = input("Enter the SSH username: ")
            ssh_password = input("Enter the SSH password: ")
            self.connect_via_ssh(ssh_address, ssh_username, ssh_password)
        else:
            print("Invalid selection. Please try again.")

    def connect_via_serial(self, port_address):
        try:
            ser = serial.Serial(
                port=port_address,
                baudrate=9600,
                stopbits=1,
                bytesize=8,
                parity='N',
                timeout=None
            )
            ser.write(b'\r\n')
            time.sleep(1)
            print("Successfully connected to the switch via serial port!")
            print("")
            self.connection = ser
            self.process_switch()
        except serial.SerialException as e:
            print("Connection to the switch failed: {}".format(e))
        finally:
            if self.connection and self.connection.is_open:
                self.connection.close()

    def connect_via_ssh(self, ssh_address, ssh_username, ssh_password):
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(ssh_address, username=ssh_username, password=ssh_password)

            print("Successfully connected to the switch via SSH!")
            print("")
            self.connection = client
            self.process_switch()
        except paramiko.AuthenticationException:
            print("Authentication failed. Please check your credentials.")
        except paramiko.SSHException as e:
            print("SSH connection failed: {}".format(str(e)))
        except paramiko.ssh_exception.NoValidConnectionsError as e:
            print("Unable to connect to the SSH server: {}".format(str(e)))
        finally:
            if self.connection:
                self.connection.close()

    def process_switch(self):
        selection = input("If you want to execute your own configuration file on a switch, enter 'yes'. Otherwise, enter 'no': ")
        if selection == 'yes':
            self.execute_config()
        elif selection == 'no':
            print("Program terminated.")
        else:
            print("Invalid selection. Please try again.")

        select = input("Do you want to write default config file as 'new.config.txt'")
        if select == 'yes':
            self.get_running_config()

    def execute_config(self):
        if isinstance(self.connection, serial.Serial):
            with open('config.txt', 'r') as config_file:
                sw_commands = config_file.readlines()
                for command in sw_commands:
                    command = command.strip()
                    print("Sending command:", command)
                    self.connection.write(command.encode())
                    time.sleep(0.1)
                    self.connection.write(b'\r\n')

            time.sleep(1)
            output = self.connection.read_all().decode()
            print("Switch Response:", output)
        elif isinstance(self.connection, paramiko.SSHClient):
            command = f"your command here for SSH connection"
            print("Sending command:", command)
            stdin, stdout, stderr = self.connection.exec_command(command)
            time.sleep(0.1)
            output = stdout.read().decode()
            print("Switch Response:", output)
        else:
            print("Invalid connection type.")


    def get_running_config(self):
        self.connection.write(b'show running-config \r\n')
        time.sleep(10)
        output = self.connection.read_all().decode()
        self.write_config_to_file(output)

    def write_config_to_file(self, config_output):
        with open('new_config.txt', 'w') as file:
            file.write(config_output)

    def send_command(self, command):
        output = None

        if isinstance(self.connection, serial.Serial):
            self.connection.write(command.encode())
            time.sleep(2)
            output = self.connection.read_all().decode()
        elif isinstance(self.connection, paramiko.SSHClient):
            stdin, stdout, stderr = self.connection.exec_command(command)
            time.sleep(2)
            output = stdout.read().decode()
        else:
            print("Invalid connection type.")

        return output

if __name__ == "__main__":
    switch_config_tool = SwitchConfigTool()
    switch_config_tool.main()