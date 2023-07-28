from netmiko import ConnectHandler

global ssh_connection
def connect_and_execute(ip, username, password, enable_secret):
    # Establish SSH connection
    ssh_connection = ConnectHandler(
        device_type='cisco_ios',
        ip=ip,
        username=username,
        password=password,
        secret=enable_secret
    )

    ssh_connection.enable()
    result = ssh_connection.find_prompt() + "\n"
    with open("config.txt", "r") as file:
        config_commands = file.read().splitlines()

    output = ssh_connection.send_config_set(config_commands)
    print(output)
    ssh_connection.disconnect()

    return result

def main():
    switches = [
        {
            'ip': '192.168.1.11',
            'username': 'farhad',
            'password': 'cisco',
            'enable_secret': 'cisco123'
        }
    ]

    for switch in switches:
        ip = switch['ip']
        username = switch['username']
        password = switch['password']
        enable_secret = switch['enable_secret']

        result = connect_and_execute(ip, username, password, enable_secret)

        print(f"Switch {ip} Configuration:")
        print(result)

if __name__ == '__main__':
    main()