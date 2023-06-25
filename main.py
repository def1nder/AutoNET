import serial
import time
def main():
    global vlan_id, vlan_name
    print("\n*-*-*-* The initiation of the serial port connection *-*-*-*")
    port_address = input("Enter the COM port address(for example - COM7): ")
    print("Attempting to connect to the switch...")

    ser = serial.Serial(
        port=port_address,
        baudrate=9600,
        stopbits=serial.STOPBITS_ONE,
        bytesize=8,
        timeout=2
    )

    ser.write(b'\r\n')
    print("Successfully connected to the switch!")

    ser.write(b'enable\r\n')
    ser.write(b'configure terminal\r\n')
    time.sleep(1)


    # ----------------------- Sending each command to the switch via config.txt -----------------------
    with open('config.txt', 'r') as config_file:
        sw_commands = config_file.readlines()
        for command in sw_commands:
            command = command.strip()
            ser.write(command.encode())
            time.sleep(1)
            ser.write(b'\r\n')
    # ----------------------- Sending each command to the switch via config.txt -----------------------


    ser.write(b'wr\r\n')
    ser.write(b'exit\r\n')
    output = ser.read_all().decode()
    print(output)
    ser.close()

if __name__ == "__main__":
    main()