# Example file

from scute import scute
from flask import Flask

app = Flask(__name__)

options = {
        "reportSchema": "reportSchema.json",
        "actionsSchema": "actionsSchema.json",
        "configSchema": "configSchema.json",
        "dataViews": "dataViews.json",
    }

test = scute(options, app)

def getDevices():
    return ["deviceOne", "deviceTwo"]

test.registerHook("get_devices", getDevices)

def getFields(deviceID):
    return {"hello": "world"}

test.registerHook("get_fields", getFields)

def getFriendlyName(deviceID):
    return deviceID + "FRIENDLY"

test.registerHook("get_field__friendlyName", getFriendlyName)

report = test.getReport("deviceOne")

