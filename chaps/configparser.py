import json
import sys

PY2 = sys.version_info < (3,)


class ConfigParser(object):
    """
    Json config parser

    Sample config:
    {
        "deps: {
            "heater": "chaps.samples.simple.Heater",
            "pump": "chaps.samples.simple.Pump"
        },
        "scopes": {
            "thread": "chaps.scopes.thread.ThreadScope"
        }
    }
    """

    def __init__(self, path):
        with open(path) as f:
            self.config_data = json.load(f)

    @staticmethod
    def _import(imp):
        if PY2:
            imp = imp.encode('utf8')
        mod_name, obj_name = imp.rsplit('.', 1)
        mod = __import__(mod_name, fromlist=[obj_name])
        return getattr(mod, obj_name)

    def _import_section(self, section):
        """
        Import section from config
        """
        deps_list = self.config_data.get(section, {})

        ret = {}
        for name, imp in deps_list.items():
            ret[name] = self._import(imp)

        return ret

    def deps(self):
        """

        Returns:
            Dependency section {'name': callable}
        """
        return self._import_section('deps')

    def scopes(self):
        """

        Returns:
            Scopes section {'name': callable}
        """
        return self._import_section('scopes')
