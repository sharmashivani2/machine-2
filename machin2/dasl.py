#!/usr/bin/python

#-*- encoding:utf-8 -*-
import tornado.web
import tornado.ioloop
from tornado.ioloop import IOLoop, PeriodicCallback
import tornado.process
import tornado.template
import tornado.httpserver
import json
import sys
import serial.tools.list_ports as ls
import os,time
import serial
import textwrap
def encrypt(string, length):
    a=textwrap.wrap(string,length)
    return a


from configparser import ConfigParser
os.chdir(os.path.dirname(os.path.realpath(__file__)))
configfile_name = "config.ini"
if not os.path.isfile(configfile_name):
    # Create the configuration file as it doesn't exist yet
    cfgfile = open(configfile_name, 'w')
    # Add content to the file
    Config = ConfigParser()
    Config.add_section('api')
    Config.set('api', 'port', '3009')
    Config.add_section('dazzler')
    Config.set('dazzler', 'sr_port', '/dev/ttyUSB0')
    Config.set('dazzler', 'baudrate', '57600')
    Config.set('dazzler', 'timeout', '1')
    Config.add_section('data')
    Config.set('data', 'on', '55 AA 04 03 50 11 03 48 F0') # on
    Config.set('data', 'off', '55 AA 04 03 50 11 04 49 F0') # off
    Config.write(cfgfile)
    cfgfile.close()
configReader = ConfigParser()
configReader.read('config.ini')
sr_port = configReader['dazzler']['sr_port']
baudrate = configReader['dazzler'].getint('baudrate')
sr_timeout = configReader['dazzler']['timeout']
api_port = configReader['api'].getint('port')
print(sr_port,baudrate)

def dazzler(data):
    os.system('python -m serial.tools.list_ports -v')
    obj = list(ls.comports())
    port_desc=obj[0].description
    ports = serial.tools.list_ports.comports(include_links=False)
    print(ports)
    actualport=''
    length=len(ports)
    print(length)
    print()
    for port in ports :
        print('Find port '+ port.device)
    try:
        ser = serial.Serial(ports[0].device)
        if ser.isOpen():
            ser.close()
        print("by port",ports[0].device)
        ser = serial.Serial(port.device, baudrate, timeout=1,stopbits=1,bytesize=8)
        ser.flushInput()
        ser.flushOutput()
        print('Connect ' + ser.name)
        actualport=ports[0].device
        ser.close()
    except:
        if length > 1:
            ser=serial.Serial(ports[1].device)
            if ser.isOpen():
                ser.close()
            print("by port",ports[1].device)
            ser = serial.Serial(port.device, baudrate, timeout=1,stopbits=1,bytesize=8)
            ser.flushInput()
            ser.flushOutput()
            print('Connect ' + ser.name)
            actualport=ports[1].device
            ser.close() 
        else:
            return "no open port found"
    sr=serial.Serial()
    # sr.port=port
    sr.port=sr_port
    sr.baudrate=baudrate
    sr.timeout=1
    sr.stopbits=1
    sr.bytesize=8
    sr.open()
    if sr.is_open:
        print("port is open")
        data=sr.write(data)
        print(data)
    else:
        print("port is not open")
        return 0
class Dazzler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')
class on(tornado.web.RequestHandler):
    def get(self):
        data = configReader['data']['on']
        resp = dazzler(bytes.fromhex(data))
        self.write({'Dazzler': 'ON'})
class off(tornado.web.RequestHandler):
    def get(self):
        data = configReader['data']['off']
        resp = dazzler(bytes.fromhex(data))
        self.write({'Dazzler': 'OFF'})

def make_app():
    return tornado.web.Application([("/", Dazzler),("/on", on),("/off", off)],template_path=os.path.join(os.path.dirname(__file__), "templates"))

if __name__ == '__main__':
    app = make_app()
    app.listen(api_port)
    print("dazzler is listening for commands on port: "+str(api_port))
    IOLoop.instance().start()