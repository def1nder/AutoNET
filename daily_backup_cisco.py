import smtplib
import pickle
from email.mime.text import MIMEText
from netmiko import ConnectHandler
from datetime import datetime
def connect_via_ssh(ip, username, password):
    ssh_connection = ConnectHandler(

        device_type ='cisco_ios',
        ip = ip,
        username = username,
        password = password,
        #secret = enable_secret
    )

    ssh_connection.enable()
    return ssh_connection

def send_email(ip_address, sender, receiver, smtp_ip, smtp_port):
    subject = "Error trying to take backup from Cisco device"
    body = f"The backup failed due to a TCP connection or device failure : {ip_address}"
    msg = MIMEText(body)
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = subject

    try:
        with smtplib.SMTP(smtp_ip, smtp_port) as server:
            server.sendmail(sender_email, receiver_email, msg.as_string())
            file.close()
    except Exception as e:
        print(f"Error occurred while sending email: {str(e)}")

def backup_config(ip):

    try:
        ssh_connection = connect_via_ssh(ip, ssh_username, ssh_password)
        ssh_connection.send_command('end')
        ssh_connection.send_command('terminal length 0')
        output = ssh_connection.send_command('show running-config')

        now = datetime.now()
        timestamp = now.strftime("%d%m%Y")

        with open(f'backup_{ip}_{timestamp}.txt', 'w') as file:
            file.write(output)
            print(f'    \033[31m[INFO]\033[0m - Backup completed: {ip}. Check the backup_{ip}_{timestamp}.txt file!')
            file.close()

        ssh_connection.disconnect()

    except Exception as e:
        print(f"Error occurred for IP {ip}: {str(e)}")
        send_email(ip, receiver_email, sender_email, smtp_server, smtp_port)

if __name__ == '__main__':

    with open('daily_backup_devices_credentials.pkl', "rb") as file:
        deserialized_dict = pickle.load(file)
        file.close()

    ssh_username = deserialized_dict["Credentials"]["username"]
    ssh_password = deserialized_dict["Credentials"]["password"]
    ip_path = deserialized_dict["Credentials"]["path"]
    receiver_email = deserialized_dict["Credentials"]["receiver_email"]
    sender_email = deserialized_dict["Credentials"]["sender_email"]
    smtp_server = deserialized_dict["Credentials"]["ip_smtp_server"]
    smtp_port = deserialized_dict["Credentials"]["port_smtp_server"]

    with open(ip_path, 'r') as file:
        for line in file:
            ip_add = line.strip()
            backup_config(ip_add)
        file.close()