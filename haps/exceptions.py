class AlreadyConfigured(Exception):
    pass


class ConfigurationError(Exception):
    pass


class NotConfigured(Exception):
    pass


class UnknownDependency(TypeError):
    pass


class UnknownScope(TypeError):
    pass


class CallError(TypeError):
    pass


class UnknownConfigVariable(ConfigurationError):
    pass
