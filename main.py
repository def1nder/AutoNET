import serial
import paramiko
import time
from colorama import Fore, Style

class SwitchConfigTool:

    switches_file = 'switches.txt'
    def __init__(self):
        self.connection = None

    def main(self):
        print("""
        /$$$$$$              /$$               /$$   /$$ /$$$$$$$$ /$$$$$$$$
       /$$__  $$            | $$              | $$$ | $$| $$_____/|__  $$__/
      | $$  \ $$ /$$   /$$ /$$$$$$    /$$$$$$ | $$$$| $$| $$         | $$   
      | $$$$$$$$| $$  | $$|_  $$_/   /$$__  $$| $$ $$ $$| $$$$$      | $$   
      | $$__  $$| $$  | $$  | $$    | $$  \ $$| $$  $$$$| $$__/      | $$   
      | $$  | $$| $$  | $$  | $$ /$$| $$  | $$| $$\  $$$| $$         | $$   
      | $$  | $$|  $$$$$$/  |  $$$$/|  $$$$$$/| $$ \  $$| $$$$$$$$   | $$   
      |__/  |__/ \______/    \___/   \______/ |__/  \__/|________/   |__/   
      
      [+] Created By Farhad Abdulkarimov & Orkhan Jabrayilov [+]
      [+] Network Automation Tool [+]                        
                                                        """)
        connection_type = input(f"What type of connection do you choose? {Fore.GREEN}[COM{Style.RESET_ALL}/{Fore.GREEN}SSH]{Style.RESET_ALL}: ")

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
            self.choice_screen()
        except serial.SerialException as e:
            print("Connection to the switch failed: {}".format(e))
        finally:
            if self.connection and self.connection.is_open:
                self.connection.close()
    def choice_screen(self):
        while True:
            print(f"{Fore.GREEN}[1]{Style.RESET_ALL} Upload config to the Switch")
            print(f"{Fore.GREEN}[2]{Style.RESET_ALL} Download config from Switch")
            print(f"{Fore.GREEN}[q]{Style.RESET_ALL} Quit\n")
            int = input(f"{Fore.GREEN}[*]{Style.RESET_ALL} Choose an option: ")
            if int == '1':
                self.execute_config()
            elif int == '2':
                self.get_running_config()
            elif int == 'q':
                break

    def connect_multiple_switches(self):

        switch_list = ['192.168.0.5', '192.168.0.8']
        credential_source = input(
            "Credential bilgilerini kullanıcıdan almak için 'input', config'den okumak için 'config' yazın: ")

        if credential_source == "input":
            # Kullanıcıdan her switch için credential bilgilerini alın
            for switch in switch_list:
                username = input(f"{switch} için kullanıcı adını girin: ")
                password = input(f"{switch} için şifreyi girin: ")
                self.connect_via_ssh(switch, username, password)
        elif credential_source == "dosya":
            filename = 'switches.txt'
            with open(filename, 'r') as file:
                credentials = file.readlines()

            for i, switch in enumerate(switch_list):
                username = credentials[i].split(',')[0].strip()
                password = credentials[i].split(',')[1].strip()
                self.connect_via_ssh(switch, username, password)
        else:
            print("Geçersiz seçenek.")


    def connect_via_ssh(self, ssh_address, ssh_username, ssh_password):
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(ssh_address, username=ssh_username, password=ssh_password)
            print("Successfully connected to the switch via SSH!")
            print("")
            self.connection = client
            self.choice_screen()
        except paramiko.AuthenticationException:
            print("Authentication failed. Please check your credentials.")
        except paramiko.SSHException as e:
            print("SSH connection failed: {}".format(str(e)))
        except paramiko.ssh_exception.NoValidConnectionsError as e:
            print("Unable to connect to the SSH server: {}".format(str(e)))
        finally:
            if self.connection:
                self.connection.close()

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
        if isinstance(self.connection, serial.Serial):
            self.connection.write(b'en \r\n')
            self.connection.write(b'terminal length 0 \r\n')
            self.connection.write(b'show running-config \r\n')
            time.sleep(10)
        output = self.connection.read_all().decode()
        self.write_config_to_file(output)

    def write_config_to_file(self, config_output):
        with open('new_config.txt', 'w') as file:
            file.write(config_output)


if __name__ == "__main__":
    switch_config_tool = SwitchConfigTool()
    switch_config_tool.main()