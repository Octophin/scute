# Demonstration file

from scute import scute
from flask import Flask, request
import json

app = Flask(__name__)

options = {
        "reportSchema": "exampleSchema/reportSchema.json",
        "actionsSchema": "exampleSchema/actionsSchema.json",
        "configSchema": "exampleSchema/configSchema.json",
        "dataViews": "exampleSchema/dataViews.json",
    }

test = scute(options, app)

def getDevices():
    return ["deviceOne", "deviceTwo"]

test.registerHook("get_devices", getDevices)

def getFields(deviceID):
    return {"hello": "world"}

test.registerHook("get_report_fields", getFields)

def getFriendlyName(deviceID):
    return deviceID + "FRIENDLY"

test.registerHook("get_report_field__friendlyName", getFriendlyName)

def saveConfig(deviceID, config):
    with open(deviceID + '_config.json', 'w') as configFile:  
        json.dump(config, configFile)

test.registerHook("save_config", saveConfig)

def readConfig(deviceID):
    with open(deviceID + '_config.json', 'r') as configFile:
        return json.load(configFile)

test.registerHook("read_config", readConfig)

@app.route('/export/<device>')
def export(device):
    return 'Export data for ' + device
    