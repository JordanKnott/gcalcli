try:
    from gcalcli3 import cli
except ImportError:
    from . import cli

cli.gcal()
