## Introduction

This script reads information from a Sennet datalogger and sends the obtained values through MQTT.

## Installation

You don't even need to clone the repository to use this script, just download the install.sh file to your server, execute it with root privileges, configure the configuration.ini file with your requirements and start the script through '/etc/init.d/sennet-mqtt start'. The script will automatically send the datalogger information.

wget https://raw.githubusercontent.com/bodiroga/sennet-mqtt-gateway/master/install.sh

sudo chmod +x install.sh

sudo ./install.sh
