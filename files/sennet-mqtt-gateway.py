import urllib2, os, time, datetime, re, sys
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
import xml.etree.ElementTree as ET

from threading import Thread
import paho.mqtt.publish as mqtt_publish
import paho.mqtt.client as mqtt_client
from ConfigParser import ConfigParser

service_name = "sennet-mqtt"
current_path = "/".join(os.path.realpath(__file__).split("/")[:-1])
logfile = "/var/log/%s.log" % (current_path, service_name)
configuration_file = "%s/configuration.ini" %current_path
global_variables = {}

def read_configuration():
    config = ConfigParser()
    config.read(configuration_file)
    for section in config.sections():
        for (variable, value) in config.items(section):
            final_variable = section+"_"+variable
            if "," in value: value = value.split(",")
            global_variables[final_variable] = value

def update_configuration(section, parameter, new_value):
    config = ConfigParser()
    config.read(configuration_file)
    config.set(section, parameter, new_value)
    log("[%s] The %s variable of %s has been changed to %s" %(datetime.datetime.now(), parameter, section, new_value))
    with open(configuration_file, 'w') as configfile:
        config.write(configfile)

def log(what):
    f = open(logfile,"a")
    f.write(what)
    f.write("\n")
    f.close()

def on_connect(client, userdata, flags, rc):
    client.subscribe(global_variables[service_name+'_suscribe_topic_prefix']+"/+")

def on_message(client, userdata, message):
    variable = message.topic.replace(global_variables[service_name+'_suscribe_topic_prefix'],'').replace('/','')
    try:
        global_variables[service_name+"_"+variable] = int(message.payload)
        update_configuration(service_name, variable, int(float(message.payload)))
    except:
        pass

def suscriberService():
    client = mqtt_client.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(global_variables['global_mqtt_broker_host'], 1883, 60)
    client.loop_forever()

def get_xml(host,port,user,password,devices):
    try:
        url = 'http://%s:%s/services/data.xml?from_id=1?to_id=%s??user=%s?password=%s?' % (host,port,devices,user,password)
        req = urllib2.Request(url)
        response = urllib2.urlopen(req, timeout=4)
        xml = response.read()
        return xml
    except Exception, e:
        log("[%s] Error connecting to the datalogger: %s" %(datetime.datetime.now(), e))
        return "<root></root>"

def get_values():
    while True:
        for index, host in enumerate(global_variables[service_name+"_datalogger_hosts"]):
            host = global_variables[service_name+"_datalogger_hosts"][index]
            name = global_variables[service_name+"_datalogger_names"][index]
            port = global_variables[service_name+"_datalogger_ports"][index]
            user = global_variables[service_name+"_datalogger_users"][index]
            password = global_variables[service_name+"_datalogger_passwords"][index]
            devices = global_variables[service_name+"_datalogger_devices"][index]

            xml = get_xml(host,port,user,password,devices)
            tree = ET.ElementTree(ET.fromstring(xml))
            root = tree.getroot()
            for each_device in root:
                device_name = each_device.attrib["name"]
                for each_channel in each_device:
                    channel_name = each_channel.attrib["des"]
                    channel_magnitude = channel_name.split(" ")[0]
                    channel_unit = channel_name[channel_name.find("(")+1:channel_name.find(")")]
                    channel_value = standarize_unit(channel_unit,each_channel.text)
                    topic_name = "%s/%s/%s" %(global_variables[service_name+'_publish_topic_prefix'],device_name,channel_magnitude)
                    try:
                        print "Publishing topic '%s' with value '%s'" %(topic_name,channel_value)
                        mqtt_publish.single(topic_name, channel_value, hostname=global_variables['global_mqtt_broker_host'])
                    except:
		        log("[%s] ERROR - Can't publish topic %s" %(datetime.datetime.now(),topic_name))
            try:
                mqtt_publish.single(global_variables[service_name+'_publish_topic_prefix']+"/timestamp",time.strftime("%Y-%m-%d %H:%M:%S"), hostname=global_variables['global_mqtt_broker_host'])
            except:
                pass
        time.sleep(float(global_variables[service_name+'_data_interval']))

def standarize_unit(unit, old_value):
    if unit == "kW":
        return float(old_value)*1000
    return old_value

def prettify_configuration_values(values):
    try:
        hosts = values[service_name+'_datalogger_hosts']
        names = values[service_name+'_datalogger_names']
        ports = values[service_name+'_datalogger_ports']
        users = values[service_name+'_datalogger_users']
        passwords = values[service_name+'_datalogger_passwords']
        devices = values[service_name+'_datalogger_devices']

        if type(hosts).__name__ == 'str':
            if type(ports).__name__ == 'str' and type(users).__name__ == 'str' and type(passwords).__name__ == 'str' and type(devices).__name__ == 'str' and type(devices).__name__ == 'str':
                values[service_name+'_datalogger_hosts'] = [hosts]
                values[service_name+'_datalogger_names'] = [names]
                values[service_name+'_datalogger_ports'] = [ports]
                values[service_name+'_datalogger_users'] = [users]
                values[service_name+'_datalogger_passwords'] = [passwords]
                values[service_name+'_datalogger_devices'] = [devices]
            else:
                log("[%s] Check the configuration syntax, you have one host configured and more than one value for the rest of the parameters" % (datetime.datetime.now()))
                print("Check the configuration syntax, you have one host configured and more than one value for the rest of the parameters")
                sys.exit(1)
        elif type(hosts).__name__ == 'list':
            hosts_size = len(hosts)
            if len(names) != hosts_size:
                log("[%s] Check the configuration syntax, each host must have a name" % (datetime.datetime.now()))
                print("Check the configuration syntax, each host must have a name")
                sys.exit(1)
            if type(ports).__name__ == 'str' and type(users).__name__ == 'str' and type(passwords).__name__ == 'str':
                values[service_name+'_datalogger_ports'] = [ports for i in range(hosts_size)]
                values[service_name+'_datalogger_users'] = [users for i in range(hosts_size)]
                values[service_name+'_datalogger_passwords'] = [passwords for i in range(hosts_size)]
                if type(devices).__name__ == 'str':
                    values[service_name+'_datalogger_devices'] = [devices for i in range(hosts_size)]
                elif len(devices) != hosts_size:
                    log("[%s] Check the configuration syntax, hosts and devices lengths are different" % (datetime.datetime.now()))
                    print("Check the configuration syntax, hosts and devices lengths are differente")
                    sys.exit(1)
            elif len(ports) != hosts_size and len(users) != hosts_size and len(passwords) != hosts_size and len(devices) != hosts_size:
                log("[%s] Check the configuration syntax, all the parameters must have the same size (hosts,ports,users,passwords and devices)" % (datetime.datetime.now()))
                print("Check the configuration syntax, all the parameters must have the same size (hosts,ports,users,passwords and devices)")
                sys.exit(1)
        else:            
            log("[%s] Check the configuration syntax" % (datetime.datetime.now()))
            print("Check the configuration syntax")
            sys.exit(1)
            
        return values

    except Exception as e:
        print e

if __name__ == "__main__":
    log("[%s] Starting Sennet service" %(datetime.datetime.now()))
    read_configuration()
    log("[%s] Configuration parameters read" %(datetime.datetime.now()))
    global_variables = prettify_configuration_values(global_variables)
    Thread(target=suscriberService).start()
    Thread(target=get_values).start()
