<!-- omit in toc -->
# Schema Compiled Utility Template Engine

SCUTE will build an extendable graphical administration interface for hardware devices from JSON schema files, allowing people to view reports about connected devices, update and manage configuration (with preset saving and loading) and perform command line actions such as viewing and exporting data (on one device or several at once) through a step-through graphical interface.

It is built to support integration with any hardware through a hook-based Python api.

Its templating and functionality is made to be as flexible as possible, taking inspiration from the theming, plugins and actions of content management systems like WordPress and Drupal.

An example set up:

* A computer such as a Raspberry Pi runs the SCUTE software with custom hooks programmed in to call various hardware functions on attached devices (via usb or bluetooth for example)
* A user connects to this computer via a web browser and uses the scute administration interface on their own laptop, tablet or phone.

*Scute was built by Octophin Digital for the Arribada Horizon biologging tags.*

![screenshot](scute-home.PNG)

- [Quick start](#quick-start)
- [Initialisation](#initialisation)
- [Hooks](#hooks)
  - [Device list](#device-list)
  - [Device Report JSON schema](#device-report-json-schema)
    - [Category](#category)
    - [Field](#field)
    - [Getting report field data](#getting-report-field-data)
  - [Device actions](#device-actions)
  - [Configuration management](#configuration-management)
    - [Category](#category-1)
    - [Fields](#fields)
    - [Loading in saved configuration into the form](#loading-in-saved-configuration-into-the-form)
    - [Saving configuration](#saving-configuration)
  - [Scripts](#scripts)
    - [Schema info](#schema-info)
  - [Template hooks](#template-hooks)
- [Templating](#templating)
- [Translations](#translations)
  - [Contributing to scute translations](#contributing-to-scute-translations)

# Quick start

* Install `python` and `pip`
* Copy the `app.py` example file and the `exampleSchema` directory from this repository to a new directory
* Copy the scute.json example file from this directory
* run `pip install git+https://github.com/octophin/scute`
* make changes to `app.py` and the JSON schema files to make it relevant to your device
* optionally, make copies of the templates under `scute/default_templates` and place them in your Flask templates folder (usually `/templates`). Files in this directory will override the default ones.
* Run the app using `python -m flask run` (note that if you've run a Flask app before you may have to run `export FLASK_APP=app` or similar beforehand. [Check the Flask documentation for more details](https://palletsprojects.com/p/flask/))

# Initialisation

SCUTE makes a `SCUTE` class available. It is used in the following way:

Scute stores its setup options in json format. Although you can pass them directly in as a dictionary, we recommend you use load the json into a dictionary with python. An example options file will look like:

```JSON

    {
        "reportSchema": "reportSchema.json",
        "actionsSchema": "actionsSchema.json",
        "configSchema": "configSchema.json",
        "presetsDirectory": "/presets",
        "scriptsDirectory": "/scripts"
    }

```

In your main `app.py` file you would run something like the following to initialise scute. Note that this won't do much on its own until you set up some devices, report, action and configuration hooks (see below or look through the example `app.py`).

```Python

from scute import scute
from flask import Flask
from json import json

app = Flask(__name__)

options = json.load(open("scute.json", "r"))

myScuteInstance = scute(options, app)

```

# Hooks

SCUTE makes use of various hooks that can be registered using a special decorator. This takes a hook name (string). For example:

```Python

@myScuteInstance.hook("get_devices")
def getDevices():
    return ["deviceOne", "deviceTwo"]


```

## Device list

The system checks for a `get_devices` hook and runs it. This should simply return a list of unique ids of connected devices. These device ids are then passed around to the other functions to get configuration, reports and data from a device and push changes to those devices.

## Device Report JSON schema

This contains information about a device for a device report screen / listing.

This reads from the report schema file path passed in to the options which contains a schema of fields like the following:

```JSON

    "<categoryName>": {
        "label": "<categoryLabel>",
        "description": "<categoryDescription>",
        "order": "<categoryOrder>",
        "fields": {
            "<fieldName>": {
                "label": "<fieldLabel>",
                "order": "<fieldOrder>",
            }
        }
    }

```

### Category

* key (string) - Category name used to group device report data into categories

* label (string) - Friendly name for the category
* description (string) - Description of the category shown to the user
* order (number) - Lower the number the higher up the page this category will sit. Category order comes before field order with fields being sorted by category first and then within a category.
* fields (object) - See below

### Field

* key (string) - System name for the field and will be used when retrieving it from the device.

* label (string) - Friendly name for the field shown to the user
* order - Lower the number the higher up the page this will sit.

(Note that at this time this structure is flat and cannot support nested / sub objects.)

### Getting report field data

For each device in the device list, the system checks for and runs the following methods

* `get_report_fields(deviceID, fieldsList)`

This takes a device ID and a list of all fields (as a list of strings) in the report schema. If present, it should return an object with key:value pairs of the field and its value. This is useful for the bulk loading of report data from a JSON file for instance.

* `get_report_field__fieldName(deviceID, fieldName)`

This, if it exists takes a device ID and a field name and return a value for the field. It will overwrite anything set in the general `get_report_fields()` function. 

## Device actions

Each device can have an action performed on it. Each action should be defined in an actions schema passed in to config. These are links that can be registered as Flask routes with parameters passed in to them automatically:

```JSON

    "<actionRoute>": {
        "label": "<actionLabel>",
        "order": "<actionOrder>",
        "bulk": "<boolean>",
        "warn": "<boolean>",
        "list": "<valueList>"
    }

```

* key (string) - The path to direct the user to. `/export` would go through to `/export/` and be passed in a query string with `devices[]` populated with a single or multiple devices as an array. If a list is passed in, the query string would also get a `value` parameter with the value of the selected dropdown item.

* label (string) - Friendly name shown on the button.
* order (number) - Order the button should appear. Lower numbers go first.
* bulk (boolean) - Can this action be performed on multiple devices?
* warn (boolean) - Should this display a confirmation popup before the action is performed?
* list (object or hookname) - Either an object of key / value pairs or the name (string) of a list hook that generates them. The hook should return key / value pairs and will be called as `get_list__<string>` (e.g `get_list__countries`).

Example usage:

```python

@app.route('/export')
def export():
    devices = request.args.getlist("devices[]")
    return 'Exporting data for ' + json.dumps(devices)

```


## Configuration management

Device configuration is managed by a JSON schema which auto generates a configuration form. The schema takes the following format.

```JSON

    "categoryName": {

        "label": "categoryLabel",
        "description": "categoryDescription",
        "order": "categoryOrder",
        "fields": {
            "<fieldName>": {
                "label": "<fieldLabel>",
                "description": "<fieldDescription>",
                "type": "<formFieldType>",
                "list": {
                    "<listItemValue>": "<listItemLabel>"
                },
                "exclueFromPresets": "<boolean>",
                "validateWith": "<functionName>"
            }

        }

    }


```

### Category

* key (string) - The system name of the category

* label (string) - Friendly category name shown to user
* description (string) - Description of the category shown to user
* Order - Lower the number the higher up the page this category will sit. Category order comes before field order with fields being sorted by category first and then within a category.
* fields (object) - See below

### Fields

* key (string) - The system name for the field. This will be called in save functions when saving configuration.

_Scute contains helper functions for flattening and unflattening `.` seperated keys for fields such as `parent.child.subfield`. These are called `flattenJSON()` and `expandJSON()`. They are demonstrated in the example `app.py` file._

* label (string) - Friendly name for the field shown to a user
* description (string) - Additional information about a field shown to a user 
* type (string) - Used in the template system. Currently available types
    * text
    * select
    * boolean
* list (object) - A key value pair of list items only used in the select field type
* excludeFromPresets (not yet implemented) - SCUTE allows users to save configuration presets, some values don't make sense to save as part of a preset. This boolean field allows such a field to be set (for example the friendly name of a device wouldn't make sense to store in a preset used by multiple devices)
* validateWith (not yet implemented) - This takes the name of a boolean function that will be called with the field value (it is also passed the device ID and field name). For example `checkIfDate(value, deviceID, fieldName)`

### Loading in saved configuration into the form

To load in saved configuration into the already set form values, use the `read_config` hook which gets passed the deviceID it's looking for the configuration for. This should return a dictionary with the key:value configuration pairs.

```Python

@myScuteInstance.hook("read_config")
def readConfig(deviceID):
    with open(deviceID + '_config.json', 'r') as configFile:
        return json.load(configFile)

```

### Saving configuration

When the configuration form is saved a `save_config` hook is run. For example:

```Python

@myScuteInstance.hook("save_config")
def saveConfig(deviceID, config):
    with open(deviceID + '_config.json', 'w') as configFile:  
        json.dump(config, configFile)


```

## Scripts

Scripts allow you to run pre-defined command line scripts with input of parameters from the GUI. Scripts are by default stored in a `"/scripts"` directory (or the `scriptsDirectory` options parameter when you initialise). They look like the following:

```JSON

{
    "name": "Basic Script",
    "description": "List a directory's files and then exit",
    "commands": [
        {
            "command": "cd ${directory} && ls",
            "description": "Go into the home directory",
            "parameters": {
                "directory": "The name of the directory"
            }
        },
        {
            "command": "ls",
            "description": "list all files"
        }
    ]
}

```

### Schema info

* Name (string) - Name of the script shown to the user
* Description (string) - A description shown to the user
* Commands (array) - A list of commands to run, each takes
    * Command (string) -  the actual command. Use `${parametername}` to swap out parameters supplied by the user through the interface.
    * Description (string) - A description of the command, shown before it is run
    * Parameters (object) - A list of parameters the user will be able to input, they will be swapped out in the command, the value is the label shown to the user, the key is the actual parameter in the command, `${directory}` for example.

## Template hooks

You may wish to add additional template variables to your templates. There is a `register_template_vars` hook for this purpose. It receives one parameter, the current Request object, and should return a dictionary. The dictionary returned will be placed in a `vars` object to use in your template.

For example:

```Python

def loadCustomVars(request):
    return {
        "url": request.url,
        "time" : datetime.now().strftime("%H:%M:%S")
    }


```

# Templating

Every template in the scute default_templates folder can be overriden with your own template placed in a `templates` folder. Each template has the following special scute global variables available:

* systemInfo - anything coming from a `get_system_info` hook
* scute_options - the options object you initially passed into your app
* hook_vars - the result of the `register_template_vars` hook for the current request. See [template hooks](#template-hooks).


# Translations

Scute makes use of Flask_Babel to provide translations.

To change the default locale of your app use the `BABEL_DEFAULT_LOCALE` Flask config setting. For example (app is your Flask app):

```python

    app.config.update({
        'BABEL_DEFAULT_LOCALE': 'de_DE', 
    })

```

Scute automatically looks in a "/translations" folder in your app if you wish to provide your own translations for your instance. Please see [Flask-Babel documentation](https://github.com/python-babel/flask-babel) for more information on how to do this or follow the guide below:

* Add a `babel.cfg` file at the root of your project with something like the following. This will check python files, templates and json files for translations.

```
[python: **.py]
[jinja2: templates/**.html]
extensions=jinja2.ext.autoescape,jinja2.ext.with_
[json_md: **.json]
```

* Make a messages.pot file for these traslations with `pybabel extract -F babel.cfg -k _l -o messages.pot .`
* Add a language (czech `cs` in this example) - `pybabel init -i messages.pot -d translations -l cs`
* Edit the file in for example `translations/cs/LC_MESSAGES/messages.po`
* Run `pybabel compile -d translations` to compile the translations

## Contributing to scute translations

We'd love it if you provided some translations to scute. To do so it's very similar to the above:

* Check templates and python files for translatable text. `pybabel extract -F babel.cfg -k _l -o messages.pot .`
* Add a language (czech `cs` in this example) - `pybabel init -i messages.pot -d scute/translations -l cs`
* Edit the file in for example `scute/translations/cs/LC_MESSAGES/messages.po`
* Run `pybabel compile -d scute/translations` to compile the translations

To test a locale, use `BABEL_DEFAULT_LOCALE` as above.
