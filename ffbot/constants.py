from importlib.metadata import PackageNotFoundError, version

try:
    VERSION = version("ffbot")
except PackageNotFoundError:
    VERSION = "0+unknown"
