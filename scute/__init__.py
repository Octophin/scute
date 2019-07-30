import json
from flask import render_template, send_from_directory, request, send_file, safe_join
import jinja2
import os
import re
import collections
from datetime import datetime, date

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
        self.server.add_url_rule('/config', 'deviceConfig', self.deviceConfigView, False, methods=["GET", "POST"])
        self.server.add_url_rule('/presets', 'presets', self.presets, methods=["GET", "POST"])
        self.server.add_url_rule('/scute/<path:filename>', 'static_assets', self.static_assets)
    def getConfigSchema(self):
        configSchema = {}
        with open(self.options["configSchema"]) as configSchema:  
            configSchema = json.load(configSchema)
            fields = {}
            # Assign default orders
            for category in configSchema:
                if "order" not in configSchema[category]:
                    self.getConfigSchema()[category]["order"] = 0
                for field in configSchema[category]["fields"]:
                    fields[field] = configSchema[category]["fields"][field]
                    if "order" not in fields[field]:
                        fields[field]["order"] = 0
        return configSchema
    def getReportSchema(self):
        with open(self.options["reportSchema"]) as reportSchema:  
            return json.load(reportSchema)
    def getReportFields(self):
        # Extract from categories to get quick access to fields
        fields = {}
        reportSchema = self.getReportSchema()
        for category in reportSchema:
            if "order" not in reportSchema[category]:
                reportSchema[category]["order"] = 0
            for field in reportSchema[category]["fields"]:
                fields[field] = reportSchema[category]["fields"][field]
                if "order" not in fields[field]:
                    fields[field]["order"] = 0
        return fields
    def getActions(self):
        with open(self.options["actionsSchema"]) as actionsSchema: 
            actions = json.load(actionsSchema)
            for key,value in actions.items():
                if "list" in value and not isinstance(value["list"], collections.Mapping):
                    actions[key]["list"] = self.hooks["get_list__" + value["list"]]()
            return actions
    def getDeviceReport(self, deviceID):
        reportValues = {}
        # First try to get all fields, then overwrite with specific ones
        try:
            reportValues = self.hooks["get_report_fields"](deviceID)
        except:
            pass
        for field in self.getReportFields():
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
        return render_template("list.html", title="Horizon",reportValues=self.getAllDeviceReports(), reportSchema=self.getReportSchema(), actions=self.getActions(), timeLoaded=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    def deviceConfigView(self):

        device = request.args.getlist("devices[]")[0]

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
    
        return render_template("config.html", title="Configuration", schema=self.getConfigSchema(), device=device, current=currentConfig)
    
    def presets(self):

        # Check if deleting a preset

        presetDirectory = 'presets/' # Todo add config parameter

        if not os.path.exists(presetDirectory):
            os.makedirs(presetDirectory)

        # Check if deleting and delete preset if yes
        if request.args.get('delete'):
            delete = request.args.get('delete')
            os.remove(presetDirectory + "/" + delete + ".json") 

        if request.method == "POST":
            saved = request.form.to_dict()
            presetName = saved["presetName"]
            saved["presetID"] = re.sub('[^a-zA-Z-]+', ' ', presetName)
            with open(presetDirectory + "/" + presetName + ".json" , 'w') as presetFile:
                json.dump(saved, presetFile)

        presetFilesNames = os.listdir(presetDirectory)
        presetFilesNames = sorted(presetFilesNames, reverse=False)

        presetFiles = []
        for file in presetFilesNames:
            with open(presetDirectory + file, "r") as f1:
                fileRaw = f1.read()
                fileJSON = json.loads(fileRaw)
                presetFiles.append(fileJSON)

        return render_template("presets.html", title="Presets", presets=presetFiles, schema=self.getConfigSchema(), current={})
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
