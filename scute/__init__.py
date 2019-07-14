import json
from flask import render_template, send_from_directory
import jinja2
import os
import collections

here = os.path.dirname(os.path.realpath(__file__))

class scute:
    hooks = {}
    def __init__(self, options, flaskServer):
        self.options = options
        self.server = flaskServer
        my_loader = jinja2.ChoiceLoader([
            self.server.jinja_loader,
            jinja2.FileSystemLoader(here + '/default_templates')
        ])
        self.server.jinja_loader = my_loader
        self.server.add_url_rule('/', 'index', self.deviceListView)
        self.server.add_url_rule('/config/<device>', 'deviceConfig', self.deviceConfigView)
        self.server.add_url_rule('/scute/<path:filename>', 'static_assets', self.static_assets)
        with open(options["reportSchema"]) as reportSchema:  
            fields = {}
            self.reportSchema = json.load(reportSchema)
            # Extract from categories to get quick access to fields
            for category in self.reportSchema:
                if "order" not in self.reportSchema[category]:
                    self.reportSchema[category]["order"] = 0
                for field in self.reportSchema[category]["fields"]:
                    fields[field] = self.reportSchema[category]["fields"][field]
                    if "order" not in fields[field]:
                        fields[field]["order"] = 0
            self.deviceReportFields = fields
        with open(options["actionsSchema"]) as actionsSchema:  
            self.actionsSchema = json.load(actionsSchema)
        with open(options["configSchema"]) as configSchema:  
            self.configSchema = json.load(configSchema)
            # Assign default orders
            for category in self.configSchema:
                if "order" not in self.configSchema[category]:
                    self.configSchema[category]["order"] = 0
                for field in self.configSchema[category]["fields"]:
                    fields[field] = self.configSchema[category]["fields"][field]
                    if "order" not in fields[field]:
                        fields[field]["order"] = 0
        with open(options["dataViews"]) as dataViews:  
            self.dataViews = json.load(dataViews)
    def getDeviceReport(self, deviceID):
        reportValues = {}
        # First try to get all fields, then overwrite with specific ones
        try:
            reportValues = self.hooks["get_report_fields"](deviceID)
        except:
            pass
        for field in self.deviceReportFields:
            try:
                reportValues[field] = self.hooks["get_report_field__" + field](deviceID)
            except:
                pass
        return reportValues
    def static_assets(self, filename):
        print(here + "/static/" + filename)
        return send_from_directory(here + "/client_side", filename)
    def registerHook(self, hookName, hookFunction):
        self.hooks[hookName] = hookFunction
    def getDevices(self):
        return self.hooks["get_devices"]()
    def getAllDeviceReports(self):
        deviceReports = {}
        for device in self.getDevices():
            deviceReports[device] = self.getDeviceReport(device)
        return deviceReports
    def deviceListView(self):
        return render_template("list.html", reportValues=self.getAllDeviceReports(), reportSchema=self.reportSchema)
    def deviceConfigView(self, device):
        return render_template("config.html", schema=self.configSchema, device=device)
    