# Cisco2960SW-Automation

This project has been developed using Python to automate switch configuration. You can do automatic configuration tasks by using commands obtained from your own config file.

# Features

- Read the commands from the config file and send them automatically to the switch.
- Send commands to the terminal via the serial port using the Serial library without the need for SSH and Telnet configuration.

# How to use

1. Arrange the switch configuration commands in the config.txt listing them one after another.
2. Attempt to establish a terminal connection using the COM port with PuTTY or SecureCRT and if your successful connection is through a specific serial port, such as COM5, enter this addres as input.
3. Before running the program, please close actively running programs such as PuTTY and SecureCRT.
4. Copy your config.txt file to the project's directory

# Contributions

Pull requests are welcome. For major changes, please open an issue to discuss the proposed changes before making them.

# License

This project is licensed under the MIT License.