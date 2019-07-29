# Demonstration file

from scute import scute
from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

options = {
        "reportSchema": "exampleSchema/reportSchema.json",
        "actionsSchema": "exampleSchema/actionsSchema.json",
        "configSchema": "exampleSchema/configSchema.json"
    }

exampleInstance = scute(options, app)

def getDevices():
    return ["ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT", "NINE"]

exampleInstance.registerHook("get_devices", getDevices)

def getFields(deviceID):
    return  {
           "id": "11:11:00:00:00:00",
           "batteryLevel": 50,
           "fileSize": 123456,
           "sensorsEnabled": [
               "gps",
               "pressure",
               "saltwater",
               "accelerometer"
           ],
           "firmwareVersion": 4,
           "fileType": "LINEAR"}

exampleInstance.registerHook("get_report_fields", getFields)

def getFriendlyName(deviceID):
    return deviceID[0] + deviceID[1]

exampleInstance.registerHook("get_report_field__friendlyName", getFriendlyName)

def saveConfig(deviceID, config):
    with open("exampleConfig_" + deviceID + '_config.json', 'w') as configFile: 
        json.dump(exampleInstance.expandJSON(config), configFile)

exampleInstance.registerHook("save_config", saveConfig)

def readConfig(deviceID):
    with open("exampleConfig_" + deviceID + '_config.json', 'r') as configFile:
        return exampleInstance.flattenJSON(json.load(configFile))

exampleInstance.registerHook("read_config", readConfig)

def getMyList():
    return {"magic": "world", "hero": "gold", "wonderful": "true"}

exampleInstance.registerHook("get_list__mylist", getMyList)

@app.route('/export')
def export():
    devices = request.args.getlist("devices[]")
    return 'Export data for ' + json.dumps(devices)

@app.route('/disconnect')
def disconnect():
    devices = request.args.getlist("devices[]")
    return 'Disconnecting ' + json.dumps(devices)

