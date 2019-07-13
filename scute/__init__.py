import json
class scute:
    def __init__(self, options, hooks, flaskServer):
        self.options = options
        self.hooks = hooks
        self.server = flaskServer
        self.server.add_url_rule('/', 'index', self.getDevices)
    def getDevices(self):
        return json.dumps(self.hooks["getDevices"]())
