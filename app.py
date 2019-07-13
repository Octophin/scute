# Example file

from scute import scute
from flask import Flask

app = Flask(__name__)

options = {
        "templateDirectory": "",
        "reportSchema": "",
        "actionsSchema": "",
        "configSchema": "",
        "dataViews": "",
        "staticFolder": ""
    }

hooks = {}

def getDevices():
    return ["hello", "world"]

hooks["getDevices"] = getDevices

test = scute(options, hooks, app)

print(test.getDevices())
