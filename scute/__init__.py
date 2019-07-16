import json
from flask import render_template, send_from_directory, request, send_file, safe_join
import jinja2
import os
import collections

here = os.path.dirname(os.path.abspath(__file__))

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
        self.server.add_url_rule('/config/<device>', 'deviceConfig', self.deviceConfigView, False, methods=["GET", "POST"])
        self.server.add_url_rule('/presets', 'presets', self.presets)
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
        return send_from_directory(here + "/client_side/", filename)
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
        return render_template("list.html", title="Device Manager",reportValues=self.getAllDeviceReports(), reportSchema=self.reportSchema, actions=self.actionsSchema)
    def deviceConfigView(self, device):

        # Save config
        if request.method == "POST":
            try:
                self.hooks["save_config"](device, request.form)
            except:
                pass

        # Load existing config and render form
        currentConfig = {}
        try:
            currentConfig = self.hooks["read_config"](device)
        except:
            pass
    
        return render_template("config.html", title="Configuration", schema=self.configSchema, device=device, current=currentConfig)
    def presets(self):
        devices = request.args.getlist("devices[]")
        return render_template("presets.html", title="Presets", devices=devices)
    def expandJSON(self, json):
        # Expand a JSON object with dot based keys into a nested JSON
        expanded = {}
        for key,value in json.items():
            output = expanded
            parts = key.split(".")
            for index,part in enumerate(parts,start=1):
                if part not in output:
                    output[part] = {}
                if index == len(parts):
                    output[part] = value
                output = output[part]
        return expanded
    def flattenJSON(self, object):
        out = {}
        def flatten(x, name=''):
            if type(x) is dict:
                for a in x:
                    flatten(x[a], name + a + '.')
            elif type(x) is list:
                i = 0
                for a in x:
                    flatten(a, name + str(i) + '.')
                    i += 1
            else:
                out[name[:-1]] = x

        flatten(object)
        return out
