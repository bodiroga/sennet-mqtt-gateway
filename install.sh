#!/bin/bash

# Make sure only root can run our script
if [[ $EUID -ne 0 ]]; then
   echo -e "This script must be run as root" 1>&2
   exit 1
fi

echo -e '\nInstalling the required programs...'
apt-get update
apt-get --assume-yes install git python-pip mosquitto
pip install paho-mqtt

cd /tmp

echo -e '\nCloning the github repository...'
git clone https://github.com/bodiroga/sennet-mqtt-gateway.git
cd sennet-mqtt-gateway

echo -e '\nMoving the program files to the /root directory...'
cp -rf files/* /root

echo -e '\nAdding the start script file...'
cp -rf init.d/* /etc/init.d/
chmod +x /etc/init.d/sennet-mqtt
update-rc.d sennet-mqtt defaults

cd /root
if [ ! -f configuration.ini ]; then
	echo -e '\nCreating the configuration.ini file, edit the parameters to meet your needs...'
	cp configuration_default.ini configuration.ini
else
	echo -e '\nYour configuration.ini file already exists, we will not touch it...'
fi

echo -e '\nRemoving the tmp folder...'
rm -rf /tmp/sennet-mqtt-gateway

echo -e '\n----------------------------------------------------------------------------'
echo -e 'Go to the /root folder, read the README-SENNET-MQTT file and edit the sennet-mqtt section of the configuration.ini file'
echo -e '----------------------------------------------------------------------------'
