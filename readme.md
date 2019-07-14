# Schema Compiled Utility Template Engine

SCUTE will build an administration interface from JSON schema files, allowing people to view reports about connected devices, update and manage configuration and view and export data from the device.

It has been built by Octophin Digital for the Arribada Horizon biologging tags.

# Dependencies

SCUTE is currently built on top of Python, Flask and Jinja.

# System configuration

SCUTE makes a `SCUTE` class available. This takes a construction object which tells SCUTE where to look for templates, schema and functions, which hooks to register and a flask server app object.

Options look like:

```Python

    {
        "templateDirectory": "",
        "reportSchema": "",
        "actionsSchema": "",
        "configSchema": "",
        "dataViews": "",
        "staticFolder": "",
    }


```

* templateDirectory (path) - Location of the template directory (used to override the default SCUTE templates)
* reportSchema (path) - reportSchema JSON file path
* actionSchema (path) - actionsSchema JSON file path
* configScheam (path) - configSchema JSON file path
* dataViews (path) - dataViews JSON file path,
* staticFolder (path) - path to the static directory the frontend will use for any client side CSS and JavaScript

# Feeds

## Device list

The system checks for a `getDeviceList` hook and runs it. This should simply return a list of unique ids of devices. These device ids are then passed around to the other functions to get configuration, reports and data from a device and push changes to that device.

## Device Report

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

* getFields(deviceID, fieldsList)

This takes a device ID and a list of all fields (as strings) in the report schema. If present, it should return an object with key:value pairs of the field and its value. This is useful for the bulk loading of report data from a JSON file for instance.

* getField__fieldName(deviceID, fieldName)

This, if it exists takes a device ID and a field name and return a value for the field. It will overwrite anything set in the general getFields() function. 

## Device actions

Each device can have an action performed on it. Each action should be defined in an `deviceActionsSchema.json`. This looks like:

```JSON

    "<actionName>": {
        "label": "<actionLabel>",
        "order": "<actionOrder>"
    }

```

* key (string) - The name of the action that will be called (called as `action__actionName(deviceID)`).

* label (string) - Friendly name shown on the button.
* order (number) - Order the button should appear. Lower numbers go first.

These actions will be shown as buttons which will, on being pressed run a python function with the naming convention of `action__actionName` passing in the device ID.

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
                "listFrom": "<functionName>",
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
    * textarea
    * select
    * boolean
* list (object) - A key value pair of list items only used in the select field type
* listFrom (string) - A function name called to retrieve the list information, this is passed the deviceId and fieldName - e.g `getCountryList(deviceID, fieldName)`. List from overwrites anything in list. The function should return an object (dictionary) of labels and values like the list parameter takes.
* excludeFromPresets - SCUTE allows users to save configuration presets, some values don't make sense to save as part of a preset. This boolean field allows such a field to be set (for example the friendly name of a device wouldn't make sense to store in a preset used by multiple devices)
* validateWith - This takes the name of a boolean function that will be called with the field value (it is also passed the device ID and field name). For example `checkIfDate(value, deviceID, fieldName)`

### Viewing data

Alongside reports, devices can show a view of their data. The views available are templates that do something with the device data they receive. How this data is formatted and what the view does depends on the view. A view is simply a Jinja template that has access to the data it is provided.

To register a view, add it to `deviceDataViews.json` to the following specification:

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
