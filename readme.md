# Schema Compiled Utility Template Engine

SCUTE will build an administration interface from JSON schema files, allowing people to view reports about connected devices, update and manage configuration and view and export data from the device.

It has been built by Octophin Digital for the Arribada Horizon biologging tags.

# Quick start

* look in the `scute/example` folder in this repository and copy all the files to a new directory
* `pip install git+https://github.com/octophin/scute`
* make changes to `app.py` and the JSON schema files to make it relevant to your device
* make copies of the templates under `scute/default_templates` and place them in your Flask templates folder (usually `/templates`). Files in this directory will override the default ones.
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
    }

myScuteInstance = scute(options, app)

```

# Hooks

SCUTE makes use of various hooks that can be registered using the `registerHook` class. This takes a hook name (string) and a function for that hook. For example:

```Python

def getDevices():
    return ["deviceOne", "deviceTwo"]

myScuteInstance.registerHook("get_devices", getDevices)

```

## Device list

The system checks for a `get_devices` hook and runs it. This should simply return a list of unique ids of devices. These device ids are then passed around to the other functions to get configuration, reports and data from a device and push changes to that device.

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

This takes a device ID and a list of all fields (as strings) in the report schema. If present, it should return an object with key:value pairs of the field and its value. This is useful for the bulk loading of report data from a JSON file for instance.

* `get_report_field__fieldName(deviceID, fieldName)`

This, if it exists takes a device ID and a field name and return a value for the field. It will overwrite anything set in the general `get_report_fields()` function. 

## Device actions

Each device can have an action performed on it. Each action should be defined in an actions schema passed in to config. At the moment these are simply links that can be registered as Flask routes:

```JSON

    "<actionRoute>": {
        "label": "<actionLabel>",
        "order": "<actionOrder>",
    }

```

* key (string) - The path to direct the user to. `/export` would go through to `/export/<deviceID>` for example.

* label (string) - Friendly name shown on the button.
* order (number) - Order the button should appear. Lower numbers go first.


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

def readConfig(deviceID):
    with open(deviceID + '_config.json', 'r') as configFile:
        return json.load(configFile)

myScuteInstance.registerHook("read_config", readConfig)

```

### Saving configuration

When the configuration form is saved a `save_config` hook is run. For example:

```Python

def saveConfig(deviceID, config):
    with open(deviceID + '_config.json', 'w') as configFile:  
        json.dump(config, configFile)

myScuteInstance.registerHook("save_config", saveConfig)

```

### Viewing data (not yet implemented)

Alongside reports, devices can show a view of their data. The views available are templates that do something with the device data they receive. How this data is formatted and what the view does depends on the view. A view is simply a Jinja template that has access to the data it is provided.

To register a view, pass in its config in the initial options object to the following specification:

```JSON

    "viewName": {
        "label": "<viewLabel>",
        "description": "<viewDescription>",
        "data": "<functionName>"
    }

```

* key (string) - System name for the view, also used in the template which should be named `viewName.html` and placed in the `templates` directory.
* label (string) - Friendly name for the view shown to the user
* data (string) - Function name called to retrieve the data which is then passed to the template.
