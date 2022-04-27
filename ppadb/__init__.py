__version__ = "0.4.0-dev"

class InstallError(Exception):
    def __init__(self, path, error):
        super(InstallError, self).__init__(f"{path} could not be installed - [{error}]")


class ClearError(Exception):
    def __init__(self, package, error):
        super(ClearError, self).__init__(f"Package {package} could not be cleared - [{error}]")
