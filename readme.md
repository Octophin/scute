# Schema Compiled Utility Template Engine

SCUTE will build an extendable graphical administration interface for hardware devices from JSON schema files, allowing people to view reports about connected devices, update and manage configuration (with preset saving and loading) and perform command line actions such as viewing and exporting data from the device (on one device or several at once) through a step-through graphical interface.

It has been built by Octophin Digital for the Arribada Horizon biologging tags.

[How it works](#quick-start)

![screenshot](https://raw.githubusercontent.com/Octophin/scute/master/scute-home.PNG)

# Quick start

* copy the `app.py` example file and the `exampleSchema` directory from this repository to a new directory
* `pip install git+https://github.com/octophin/scute`
* make changes to `app.py` and the JSON schema files to make it relevant to your device
* optionally, make copies of the templates under `scute/default_templates` and place them in your Flask templates folder (usually `/templates`). Files in this directory will override the default ones.
* Run the app using `python -m flask run`

# Initialisation

SCUTE makes a `SCUTE` class available. It is used in the following way:

```Python

from scute import scute
from flask import Flask

app = Flask(__name__)

options = {
        "reportSchema": "reportSchema.json",
        "actionsSchema": "actionsSchema.json",
        "configSchema": "configSchema.json",
        "dataViews": "dataViews.json",
        "presetsDirectory": "/presets",
        "scriptsDirectory": "/scripts"
    }

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
