import json
from flask import render_template, send_from_directory, request, redirect, g, session
from flask_babel import Babel
import jinja2
import os
import re
import collections
from datetime import datetime, date
import urllib
import subprocess
import unicodedata
import string
import mistune #markdown renderer

here = os.path.dirname(os.path.abspath(__file__))

import pkg_resources 

try:
    scuteVersion = pkg_resources.require("scute")[0].version
except:
    scuteVersion =  "x.x.x"

class scute:
    hooks = {}
    def __init__(self, options, flaskServer):

        flaskServer.config.update({
            'BABEL_TRANSLATION_DIRECTORIES': here + '/translations;translations',
        })

        babel = Babel(flaskServer)

        # Use the browser's language preferences to select an available translation
        # @babel.localeselector
        # def get_locale():
        #     translations = [str(translation) for translation in babel.list_translations()]
        #     return request.accept_languages.best_match(translations)

        @flaskServer.context_processor
        def default_vars():
            return {"systemInfo":self.tryHook("get_system_info"), "scute_options":self.options, "hook_vars":self.tryHook("register_template_vars", request)}

        self.options = options
        self.server = flaskServer
        my_loader = jinja2.ChoiceLoader([
            self.server.jinja_loader,
            jinja2.FileSystemLoader(here + '/default_templates')
        ])
        self.server.jinja_loader = my_loader
        self.server.add_url_rule('/', 'index', self.indexView)
        self.server.add_url_rule('/list', 'list', self.deviceListView, False, methods=["GET", "POST"])
        self.server.add_url_rule('/config', 'deviceConfig', self.deviceConfigView, False, methods=["GET", "POST"])
        self.server.add_url_rule('/applyPreset', 'applyPreset', self.applyPresetView, False, methods=["GET", "POST"])
        self.server.add_url_rule('/presets', 'presets', self.presets, methods=["GET", "POST"])
        self.server.add_url_rule('/scute/<path:filename>', 'static_assets', self.static_assets)
        self.server.add_url_rule('/scripts', 'scripts', self.scriptsView, False, methods=["GET", "POST"])
        self.server.add_url_rule('/scripts/<script>', 'script', self.script, False, methods=["GET", "POST"])
        self.server.add_url_rule('/help', 'help', self.helpView)
 
    def getSCUTEVersion(self):
        return scuteVersion

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

    def hook(self, hookName):
        def registerHookInternal(hookFunction):
            return self.registerHook(hookName, hookFunction)
        return registerHookInternal

    def tryHook(self, hookName, *args):
        try:
            return self.hooks[hookName](*args)
        except Exception as e:
            print(e)
            pass
    
    def getDevices(self):
        return self.hooks["get_devices"]()

    def getAllDeviceReports(self):
        deviceReports = {}
        devices = self.getDevices()
        if 'error' in devices:
            deviceReports = devices
        else:
            for device in devices:
                deviceReports[device] = self.getDeviceReport(device)
        return deviceReports

    def getHelpInfo(self):
        helpInfo = {}

        with open(self.options["helpInfo"], "r") as f1:
                dataRaw = f1.read()
                helpInfo = mistune.markdown(dataRaw)

        return helpInfo

    def indexView(self):

        indexData = {"header": "Welcome To SCUTE", "content": "<a href='/list'>Scan For Devices</a>"}
        return render_template("content/index.html", title="Welcome", indexData = indexData)


    def deviceListView(self):
        
        return render_template("content/list.html", title="Devices", reportValues=self.getAllDeviceReports(), reportSchema=self.getReportSchema(), presetValues=self.getAllPresetValues(), actions=self.getActions())
    
    def getAllPresetValues(self):
        # scan the preset directory and return value label pairs
        if not os.path.exists('presets'):
            return [{"value": "", "label": "No Presets Found"}]
        pathContent = os.listdir('presets')
        replyValues = []
        for file in pathContent:
            fileParts = file.split(".")
            replyValues.append({"value": file, "label": fileParts[0]})
        
        if replyValues == []:
            replyValues = [{"value": "", "label": "No Presets Found"}]
        return replyValues

    def deviceConfigView(self):

        device = request.args.getlist("devices[]")[0]

        # Save config
        if request.method == "POST":

            clickAction = request.values['clickAction']

            try:

                # Check if saving preset
                if clickAction == "preset" :
                    # Go to presets page
                    presetQuery = self.processFormTypes(request.form)
                    presetQueryJSON = json.dumps(presetQuery)
                    return redirect("/presets?config=" + presetQueryJSON, code=302)
                else:
                    saveResponse = self.hooks["save_config"](device, self.processFormTypes(request.form))

                    if saveResponse:
                        session['userMessage'] = saveResponse

                    if "redirect" in g:
                        return redirect(g.redirect)


            except:
                pass

        # Load existing config and render form
        currentConfig = {}
        try:
            currentConfig = self.hooks["read_config"](device)
        except:
            pass


        if 'invalidConfigDetected' in currentConfig and currentConfig['invalidConfigDetected'] == True:
                              
            session['userMessage'] = {"type": 'error', "message": "Invalid config detected for '<strong>" + currentConfig['local.friendlyName']  + " ("+ str(device) + ")</strong>'.<br />Please enter config manually, apply a preset or apply the default config via the SCRIPTS."}
    

        return render_template("content/config.html", title="Device Configuration", schema=self.getConfigSchema(), device=device, current=currentConfig)

    def applyPresetView(self):
        devices = request.args.getlist("devices[]")
        preset = request.args.get("value")

        if request.method == "POST":
            responseType = 'success'
            responseMessages = []
            form = self.processFormTypes(request.form)
            for device in devices:
                deviceConfig = self.hooks["read_config"](device)
                for field,value in form.items():
                    deviceConfig[field] = value
                saveResponse = self.hooks["save_config"](device, deviceConfig)
                # error or success?
                if saveResponse['type'] == "error" and responseType == 'success':
                    responseType = 'error'
                if saveResponse['type'] == "error":
                    responseMessages.append("Error for " + device + " - " + saveResponse['message'])
                else:
                    responseMessages.append("Applied to " + device + " sucessfully.")
           
            session['userMessage'] = {"type": responseType, "message": "<strong>Apply Preset " + preset + " results</strong><br > " + '<br />'.join(responseMessages) }

            return redirect("/list")

        presetDirectory = ""

        if("presetsDirectory" in self.options):
            presetDirectory = self.options["presetsDirectory"]
        else:
            presetDirectory = 'presets/'

        with open(presetDirectory + preset, "r") as f1:
                presetRaw = f1.read()
                presetJSON = json.loads(presetRaw)

        presetSchema = self.filterOutFieldsWithBooleanAttribute(self.getConfigSchema(), "excludeFromPresets")

        return render_template("content/applyPreset.html", title="Apply preset", schema=presetSchema, devices=devices, preset=preset, current = presetJSON)

    def helpView(self):
        return render_template("content/helpPage.html", title="Help", helpInfo=self.getHelpInfo())
    


    def filterOutFieldsWithBooleanAttribute(self, fullSchema, excludeAttribute):

        filteredSchema = {}

        for thisCategory in fullSchema.keys(): # loop categories
            filteredSchema[thisCategory] = fullSchema[thisCategory]
            filteredFields = {}

            for fieldName in fullSchema[thisCategory]["fields"]: #loop fields
                               
                if (excludeAttribute in fullSchema[thisCategory]["fields"][fieldName] 
                    and fullSchema[thisCategory]["fields"][fieldName][excludeAttribute] == True):
                    print("Filtering out " + fieldName)

                else:
                    #only add fields that no not match.
                    filteredFields[fieldName] = fullSchema[thisCategory]["fields"][fieldName]

            filteredSchema[thisCategory]["fields"] = filteredFields
            if len(filteredFields) == 0:
                # remove the category..
                del(filteredSchema[thisCategory])
            else:
                # update the fields.
                filteredSchema[thisCategory]["fields"] = filteredFields
                    
        return filteredSchema


    def presets(self, current=None):

        presetDirectory = ""

        if("presetsDirectory" in self.options):
            presetDirectory = self.options["presetsDirectory"]
        else:
            presetDirectory = 'presets/'

        if presetDirectory[len(presetDirectory)-1] != "/":
            presetDirectory = presetDirectory + "/"

        if not os.path.exists(presetDirectory):
            os.makedirs(presetDirectory)

        # Check if deleting and delete preset if yes
        if request.args.get('delete'):
            delete = request.args.get('delete')
            os.remove(presetDirectory + "/" + delete + ".json") 
            # refresh the page to remove the 'delete' from URL params.
            session['userMessage'] = {"type": 'info', "message": "Preset Deleted: <strong>" + delete +"</strong>." }
            return redirect("/presets")

        # Check if query contains a preset (from the config page)

        prefill = {}

        if request.args.get("config"):
            prefill = json.loads(request.args.get("config"))

        if request.method == "POST":
            if "paste" in request.form:

                try:
                    prefill = json.loads(request.form["paste"])
                except:
                    session['userMessage'] = {"type": 'error', "message": "<strong>Invalid Preset.</strong><br />Please check and try again.  Note: this only accepts json data created through this preset manager (flattened JSON)." }
                    return redirect("/presets") # reloads this page.
                
                session['userMessage'] = {"type": 'info', "message": "<strong>Preset Valdated.</strong><br />Please check the name and description, make any changes required and press save." }


            else:
                saved = self.processFormTypes(request.form)
                safeName = re.sub('[^a-zA-Z-_0-9]+', ' ', saved["presetName"])
                safeName = safeName.strip()
                safeName = safeName.replace(" ", "_")
                saved["presetID"] = safeName
                with open(presetDirectory + safeName + ".json" , 'w') as presetFile:
                    json.dump(saved, presetFile)
                session['userMessage'] = {"type": 'success', "message": "Preset Saved: <strong>" + safeName + "</strong>." }

        presetFilesNames = os.listdir(presetDirectory)
        presetFilesNames = sorted(presetFilesNames, reverse=False)

        presetFiles = []
        for file in presetFilesNames:
            with open(presetDirectory + file, "r") as f1:
                fileRaw = f1.read()
                fileJSON = json.loads(fileRaw)
                presetFiles.append(fileJSON)
        
        presetSchema = self.filterOutFieldsWithBooleanAttribute(self.getConfigSchema(), "excludeFromPresets")

        return render_template("content/presetsView.html", title="Preset Manager", presets=presetFiles, schema=presetSchema, current=prefill, sidepanel=True)



    def script(self, script):

        scriptsDirectory = ""

        if("scriptsDirectory" in self.options):
            scriptsDirectory = self.options["scriptsDirectory"]
        else:
            scriptsDirectory = 'content/scripts/'


        scriptSchema = {}
        with open(scriptsDirectory + "/" + script, "r") as f1:
            fileRaw = f1.read()
            scriptSchema = json.loads(fileRaw)

        if request.args.get("command"):
            currentCommand = int(request.args.get("command"))
            nextCommand = currentCommand + 1
        else:
            currentCommand = -1
            nextCommand = 0

        output = ""
        error = False
        if currentCommand > 0:
            commandToRun = currentCommand - 1
            # Run command

            # Check if any parameters have been passed in

            command = scriptSchema["commands"][commandToRun]["command"]
            output = ""
            for key,value in request.args.items():
                command = command.replace("${"+key+"}", value)
            p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = p.communicate()
            if stdout:
                output = stdout
            else:
                output = stderr
                error = True

        return render_template("content/script.html", title=scriptSchema["name"], script=scriptSchema, nextCommand = nextCommand, fileName=script, output=output, error = error)

    def scriptsView(self):

        scriptsDirectory = ""

        if("scriptsDirectory" in self.options):
            scriptsDirectory = self.options["scriptsDirectory"] + '/'
        else:
            scriptsDirectory = 'content/scripts/'


        # Check if deleting and delete scripe if yes
        if request.args.get('delete'):
            delete = request.args.get('delete')
            os.remove(scriptsDirectory + "/" + delete ) 
            # refresh the page to remove the 'delete' from URL params.
            session['userMessage'] = {"type": 'info', "message": "Script Deleted: <strong>" + delete +"</strong>." }
            return redirect("/scripts") # clear the 'delete' from URL - reloads this page.


        if request.method == "POST":

            # make filename safe
            filename = re.sub('[^a-zA-Z-_0-9]+', ' ', request.form["scriptName"])
            filename = filename.strip().lower().replace(" ", "_")


            try:
                commands = json.loads(request.form['scriptCommands'])
            except:
                session['userMessage'] = {"type": 'error', "message": "<strong>Invalid Commands.</strong>Please check and try again." }
                return redirect("/scripts") # reloads this page.

            # validate the input command array
            if  not iter(commands):
                session['userMessage'] = {"type": 'error', "message": "<strong>Invalid Commands.</strong> You must enter a valid json array.  Please check and try again." }
            elif len(commands) == 0 or "command" not in commands[0]:
                session['userMessage'] = {"type": 'error', "message": "<strong>Invalid Commands.</strong> Invalid command array. Please check and try again." }

            else:

                # new script object
                newScript = {}
                newScript['name'] = request.form["scriptName"]
                newScript['description'] = request.form['scriptDescription']
                newScript['commands'] = commands
                newScript['type'] = "user" #'system' scripts can not be deleted, 'user' can.

                with open(scriptsDirectory + filename + ".json" , 'w') as outputFile:
                    json.dump(newScript, outputFile)
                session['userMessage'] = {"type": 'success', "message": "Script Saved: <strong>" + newScript['name']  +" ("  + filename+ ")</strong>." }


        try:
            scriptsFileNames = os.listdir(scriptsDirectory)
            scriptsFileNames = sorted(scriptsFileNames, reverse=False)
        except:
            scriptsFileNames = []

        scripts = []

        for file in scriptsFileNames:
            with open(scriptsDirectory + "/" + file, "r") as f1:
                fileRaw = f1.read()
                fileJSON = json.loads(fileRaw)
                fileJSON["fileName"] = file
                scripts.append(fileJSON)

        return render_template("content/scriptsView.html", title="Scripts", scripts=scripts, sidepanel=True)

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
    def processFormTypes(self, formObject):

        form = formObject.to_dict()

        # Convert a submitted form to have the correct types (booleans only for now)  
        output = {}

        for key,value in form.items():
            if value == "notselected":
                value = False
            if value == "selected":
                value = True
            output[key] = value
        
        return output
