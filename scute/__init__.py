import json
from flask import render_template, send_from_directory
import jinja2
import os

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
        self.server.add_url_rule('/', 'index', self.listView)
        self.server.add_url_rule('/scute/<path:filename>', 'static_assets', self.static_assets)
        with open(options["reportSchema"]) as reportSchema:  
            fields = {}
            self.reportSchema = json.load(reportSchema)
            # Extract from categories to get quick access to fields
            for category in self.reportSchema:
                for field in self.reportSchema[category]["fields"]:
                    fields[field] = self.reportSchema[category]["fields"][field]
            self.deviceReportFields = fields 
        with open(options["actionsSchema"]) as actionsSchema:  
            self.actionsSchema = json.load(actionsSchema)
        with open(options["configSchema"]) as configSchema:  
            self.configSchema = json.load(configSchema)
        with open(options["dataViews"]) as dataViews:  
            self.dataViews = json.load(dataViews)
    def getReport(self, deviceID):
        reportValues = {}
        # First try to get all fields, then overwrite with specific ones
        try:
            reportValues = self.hooks["get_fields"](deviceID)
        except:
            pass
        for field in self.deviceReportFields:
            try:
                reportValues[field] = self.hooks["get_field__" + field](deviceID)
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
    def listView(self):
        return render_template("hello.html", devices=self.getDevices())
    
