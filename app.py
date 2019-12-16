# Demonstration file

from scute import scute
from flask import Flask, request, jsonify, g, render_template, session
from datetime import datetime, date
import json
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

options = {
    "reportSchema": "exampleSchema/reportSchema.json",
    "actionsSchema": "exampleSchema/actionsSchema.json",
    "configSchema": "exampleSchema/configSchema.json",
    "scriptsDirectory": "exampleSchema/scripts",
    "helpInfo": "helpfiles/index.md"
}

exampleInstance = scute(options, app)


def getDevices():

    return [
        "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT", "NINE"
    ]


exampleInstance.registerHook("get_devices", getDevices)


def getIndexData():
    {
        "accessAllowed": True,
        "usermessage": {
            "type": "success",
            "message": "OK"
        }
    }


exampleInstance.registerHook("get_index_data", getIndexData)


def getSystemInfo():

    # user message in session? extract it for display and remove it from session.
    if 'userMessage' in session:
        userMessage = session['userMessage']
        session.pop('userMessage')
    else:
        userMessage = False

    now = datetime.now()

    # add anything here you want available to all pages.
    return {
        "userMessage": userMessage,
        "scuteVersion": exampleInstance.getSCUTEVersion(),
        "currentDateTime": now.strftime("%c")
    }


exampleInstance.registerHook("get_system_info", getSystemInfo)


def getFields(deviceID):
    return {
        "id": "11:11:00:00:00:00",
        "batteryLevel": 50,
        "fileSize": 123456,
        "sensorsEnabled": ["gps", "pressure", "saltwater", "accelerometer"],
        "firmwareVersion": 4,
        "fileType": "LINEAR"
    }


exampleInstance.registerHook("get_report_fields", getFields)


def getFriendlyName(deviceID):
    return deviceID[0] + deviceID[1]


exampleInstance.registerHook("get_report_field__friendlyName", getFriendlyName)


def saveConfig(deviceID, config):

    session['userMessage'] = {
        "type": 'success',
        "message": "Config Saved for <strong>" + str(deviceID) + "</strong>"
    }

    with open("exampleConfig_" + deviceID + '_config.json', 'w') as configFile:
        g.redirect = "/list"
        json.dump(exampleInstance.expandJSON(config), configFile)


exampleInstance.registerHook("save_config", saveConfig)


def readConfig(deviceID):
    with open("exampleConfig_" + deviceID + '_config.json', 'r') as configFile:
        return exampleInstance.flattenJSON(json.load(configFile))


exampleInstance.registerHook("read_config", readConfig)


def getExampleList():
    return {
        "Example 1": "Example_1",
        "Example 2": "Example_2",
        "Example 3": "Example_3"
    }


exampleInstance.registerHook("get_list__myExampleList", getExampleList)

# Additional Routes

@app.route('/export')
def export():
    devices = request.args.getlist("devices[]")
    userMessage = {
        "message": "Export TBC: <strong>" + json.dumps(devices) + "</strong>"
    }

    return render_template("content/defaultPage.html",
                           title="Export",
                           systemInfo=getSystemInfo(),
                           userMessage=userMessage)


@app.route('/erase_log')
def erase_log():
    devices = request.args.getlist("devices[]")
    userMessage = {
        "message":
        "Erase Log TBC: <strong>" + json.dumps(devices) + "</strong>"
    }

    return render_template("content/defaultPage.html",
                           title="Erase Log",
                           systemInfo=getSystemInfo(),
                           userMessage=userMessage)


@app.route('/reset_device')
def reset_device():
    devices = request.args.getlist("devices[]")
    userMessage = {
        "message":
        "Reset Device TBC: <strong>" + json.dumps(devices) + "</strong>"
    }

    return render_template("content/defaultPage.html",
                           title="Reset Device",
                           systemInfo=getSystemInfo(),
                           userMessage=userMessage)


@app.route('/another_task')
def another_task():
    devices = request.args.getlist("devices[]")
    userMessage = {
        "message":
        "Another Task TBC: <strong>" + json.dumps(devices) + "</strong>"
    }

    return render_template("content/defaultPage.html",
                           title="Another Task",
                           systemInfo=getSystemInfo(),
                           userMessage=userMessage)
