## CONFIGURATION PARAMETERS

data_interval: how often the script should check the datalogger and send the data through MQTT.
datalogger_names: comma separated list with the friendly names of all your dataloggers (e.g. main).
datalogger_hosts: comma separated list with the ip addresses of all your dataloggers (e.g. 192.168.1.50).
datalogger_devices: comma separated list with the number of devices connected to each dataloggers. If you write a single value, the same number of devices will be checked for all the dataloggers.
datalogger_ports: comma separated list with the connection ports of all your dataloggers. If you write a single value, the same port will be used for all the dataloggers.
datalogger_users: comma separated list with the user names of all your dataloggers. If you write a single value, the same user name will be used for all the dataloggers.
datalogger_passwords: comma separated list with the password of all your dataloggers. If you write a single value, the same password will be used for all the dataloggers.
publish_topic_prefix: root prefix for the MQTT topic where the data will be sent. The complete topic will be: <prefix>/<datalogger_name>/<datalogger_device>/<magnitude>, with the magnitude value in the MQTT message payload.
suscribe_topic_prefix: root prefix for the MQTT topic where the script will be listening to configuration changes. If your prefix is "openhab/scripts/configuration/sennet", you can change the data interval in realtime sending an MQTT message to the "openhab/scripts/configuration/sennet/data_interval", with the new data interval time in the message payload.
