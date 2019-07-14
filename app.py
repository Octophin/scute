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
    return ["hello", "world"]

test.registerHook("getDevices", getDevices)

