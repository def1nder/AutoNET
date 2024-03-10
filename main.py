import pickle
from netmiko import ConnectHandler

def window():
    print("""
    \033[31m
    //         █████╗ ██╗   ██╗████████╗ ██████╗ ███╗   ██╗███████╗████████╗
    //        ██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗████╗  ██║██╔════╝╚══██╔══╝
    //        ███████║██║   ██║   ██║   ██║   ██║██╔██╗ ██║█████╗     ██║   
    //        ██╔══██║██║   ██║   ██║   ██║   ██║██║╚██╗██║██╔══╝     ██║   
    //        ██║  ██║╚██████╔╝   ██║   ╚██████╔╝██║ ╚████║███████╗   ██║   
    //        ╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ ╚═╝  ╚═══╝╚══════╝   ╚═╝   
    //                                                          
    //         [+] Copyright (c) 2023 def1nder (Farhad Abdulkarimov) [+]
    //               \033[32mv1.0.0\033[0m \033[34m- https://github.com/def1nder/AutoNET      
                              """)
    print()
    print("   Select from the menu: ")
    print()
    print('   \033[32m1)\033[0m - Upload command to the Cisco devices')
    print('   \033[32m2)\033[0m - Download backup from the Cisco device')
    print('   \033[32m3)\033[0m - Set the daily backup configuration')
    print('   \033[32m0)\033[0m - Quit\n')

def connect_via_ssh(ip, username, password):

    ssh_connection = ConnectHandler(
        device_type='cisco_ios',
        ip=ip,
        username=username,
        password=password,
        #secret = enable_secret
    )
    ssh_connection.enable()
    return ssh_connection

def command_upload_ssh():

    switches = []
    print()
    config = input('    \033[31m[*]\033[0m - Provide the full path for the commands file: ')
    path = input('    \033[31m[*]\033[0m - Provide the directory path for the Cisco devices containing the IP addresses: ')
    username = input('    \033[31m[*]\033[0m - Enter the username for connecting to these devices: ')
    password = input('    \033[31m[*]\033[0m - Enter the password for connecting to these devices: ')

    with open(config, 'r') as file:
        config_commands = file.readlines()
        file.close()

    with open(path, 'r') as file:
        for line in file:
            ip_add = line.strip()
            switches.append(ip_add)
        file.close()

    for each_switch in switches:
        ssh_connection = connect_via_ssh(each_switch, username, password)
        output = ssh_connection.send_config_set(config_commands)
        print()
        print(f'    \033[32m[INFO]\033[0m - Switch {each_switch} Configuration:')
        print(output)
        ssh_connection.disconnect()
def get_backup_directly():

    ip = input('    \033[31m[*]\033[0m - Please enter the SSH IP address of the device from which you want to fetch the config: ')
    username = input('    \033[31m[*]\033[0m - Enter the SSH username: ')
    password = input('    \033[31m[*]\033[0m - Enter the SSH password: ')
    ssh_connection = connect_via_ssh(ip, username, password)
    ssh_connection.send_command('end')
    ssh_connection.send_command('terminal length 0')
    output = ssh_connection.send_command('show running-config')

    with open('backup.txt', 'w') as file:
        file.write(output)
        file.close()

    print()
    print(f'    \033[32m[INFO]\033[0m - Backup completed: {ip}. Check the \033[31mbackup.txt\033[0m file!')
    ssh_connection.disconnect()

def get_backup_daily():

    path = input('    \033[31m[*]\033[0m - Provide the directory path for the Cisco devices containing the IP addresses: ')
    username = input('    \033[31m[*]\033[0m - Enter the username for connecting to these devices: ')
    password = input('    \033[31m[*]\033[0m - Enter the password for connecting to these devices: ')
    receiver_email = input('    \033[31m[*]\033[0m - Enter the receiver email address: ')
    sender_email = input('    \033[31m[*]\033[0m - Enter the sender email address: ')
    ip_smtp_server = input('    \033[31m[*]\033[0m - Enter the IP address of SMTP server: ')
    port_smtp_server = input('    \033[31m[*]\033[0m - Enter the SMTP server port: ')

    SWcredentials_and_emailDetails = {

        'Credentials': {'username': username, 'password': password, 'path': path,
                        'receiver_email': receiver_email, 'sender_email': sender_email,
                        'ip_smtp_server': ip_smtp_server, 'port_smtp_server' : port_smtp_server
                        }
    }

    with open('daily_backup_devices_credentials.pkl', "wb") as file:
        pickle.dump(SWcredentials_and_emailDetails, file)
        file.close()
    print()
    print('    \033[32m[INFO]\033[0m - The information you provided about the '
                                                  'device for the daily backup has been successfully saved in the '
                                                  'file daily_backup_devices_credentials.pkl. You can now '
                                                  'give daily_backup_cisco.py as input to task schedulers like Crontab and Systemd.')

if __name__ == '__main__':

    while True:
        window()
        inp = input("   Choose an option: ")

        match inp:
            case '1':
                command_upload_ssh()
            case '2':
                get_backup_directly()
            case '3':
                get_backup_daily()
            case '0':
                break