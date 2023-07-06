import serial
import time

def main(port_adress):
    try:
        ser = serial.Serial(
        port=port_adress,
        baudrate=9600,
        stopbits=1,
        bytesize=8,
        parity='N',
        timeout=None
        )
        ser.write(b'\r\n')
        time.sleep(1)
        print("Successfully connected to the switch!")
        print("")
        vlan_info = get_active_vlans(ser)

        if vlan_info is not None:
            vlan_count = len(vlan_info)
            print("Switch has a total of {} active VLAN(s).".format(vlan_count))
            print("Active VLANs and their names:")
            for vlan in vlan_info:
                print("VLAN {}: {}".format(vlan[0], vlan[1]))
        else:
            print("Aktif VLAN bilgisi alınamadı.")

        port_selection = input("Enter 'single' to select a specific port or 'range' to select a port range: ")
        if port_selection == 'single':
            port_num = input("Enter the port number for the interface (e.g., 0/1): ")
            process_single_port(ser, port_num)
        elif port_selection == 'range':
            start_port = input("Enter the starting port number (e.g., 0/1): ")
            end_port = input("Enter the ending port number (e.g., 24): ")
            process_port_range(ser, start_port, end_port)
        else:
            print("Invalid selection. Please try again.")

    except serial.SerialException as e:
        print("Connection to the switch failed: {}".format(e))

    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()


def process_single_port(ser, port_num):
    with open('config.txt', 'r') as config_file:
        sw_commands = config_file.readlines()
        for command in sw_commands:
            command = command.strip()
            if 'interface FastEthernet' in command:
                command = command.replace('FastEthernet', f'FastEthernet{port_num}')
            print("Sending command:", command)
            ser.write(command.encode())
            time.sleep(0.1)
            ser.write(b'\r\n')

    time.sleep(1)
    output = ser.read_all().decode()
    print("Switch Response:", output)

def process_port_range(ser, start_port, end_port):
    with open('config.txt', 'r') as config_file:
        sw_commands = config_file.readlines()
        for command in sw_commands:
            command = command.strip()
            if 'interface FastEthernet' in command:
                command = command.replace('FastEthernet', f'range FastEthernet{start_port}-{end_port}')
            print("Sending command:", command)
            ser.write(command.encode())
            time.sleep(0.1)
            ser.write(b'\r\n')

    time.sleep(1)
    output = ser.read_all().decode()
    print("Switch Response:", output)

def get_active_vlans(ser):
    ser.write(b'show vlan brief\r\n')
    time.sleep(2)
    output = ser.read_all().decode()
    lines = output.split('\n')
    vlan_info = []

    for line in lines:
        line = line.strip()
        if 'active' in line.lower():
            vlan_parts = line.split()
            if len(vlan_parts) >= 3:
               vlan_id = vlan_parts[0]
               vlan_name = vlan_parts[1]
               vlan_info.append((vlan_id, vlan_name))

    return vlan_info

if __name__ == "__main__":
    print("\n*-*-*-* The initiation of the serial port connection *-*-*-*")
    port_address = input("Enter the COM port address (for example - COM7): ")
    print("Attempting to connect to the switch...")

    main(port_address)