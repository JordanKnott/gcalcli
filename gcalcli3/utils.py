import calendar
import sys
import time
from builtins import str
from datetime import datetime, timedelta

import locale
import re

# Required 3rd party libraries
from parsedatetime import parsedatetime

try:
    import attr
    from dateutil.tz import tzlocal
    from dateutil.parser import parse
except ImportError as e:
    print("ERROR: Missing module - %s" % e.args[0])
    sys.exit(1)

from . import colors


def stringToUnicode(string):
    return str(string)


def stringFromUnicode(string):
    return string.encode(locale.getlocale()[1] or
                         locale.getpreferredencoding(False) or
                         "UTF-8", "replace")


def Usage(expanded=False):
    sys.stdout.write(__doc__ % sys.argv[0])
    sys.exit(1)


def PrintErrMsg(msg):
    PrintMsg(colors.CLR_BRRED(), msg)


def PrintMsg(color, msg):
    if colors.CLR.useColor:
        sys.stdout.write(str(color))
        sys.stdout.write(str(msg))
        sys.stdout.write(str(colors.CLR_NRM()))
    else:
        sys.stdout.write(msg)


def DebugPrint(msg):
    return
    PrintMsg(colors.CLR_YLW(), msg)


def dprint(obj):
    try:
        from pprint import pprint
        pprint(obj)
    except ImportError:
        print(obj)


class DateTimeParser:
    def __init__(self):
        self.pdtCalendar = parsedatetime.Calendar()

    def fromString(self, eWhen):
        defaultDateTime = datetime.now(tzlocal()).replace(hour=0,
                                                          minute=0,
                                                          second=0,
                                                          microsecond=0)

        try:
            eTimeStart = parse(eWhen, default=defaultDateTime)
        except:
            struct, result = self.pdtCalendar.parse(eWhen)
            if not result:
                raise ValueError("Date and time is invalid")
            eTimeStart = datetime.fromtimestamp(time.mktime(struct), tzlocal())

        return eTimeStart


def DaysSinceEpoch(dt):
    # Because I hate magic numbers
    __DAYS_IN_SECONDS__ = 24 * 60 * 60
    return calendar.timegm(dt.timetuple()) / __DAYS_IN_SECONDS__


def GetTimeFromStr(eWhen, eDuration=0, allday=False):
    dtp = DateTimeParser()

    try:
        eTimeStart = dtp.fromString(eWhen)
    except:
        PrintErrMsg('Date and time is invalid!\n')
        sys.exit(1)

    if allday:
        try:
            eTimeStop = eTimeStart + timedelta(days=float(eDuration))
        except:
            PrintErrMsg('Duration time (days) is invalid\n')
            sys.exit(1)

        sTimeStart = eTimeStart.date().isoformat()
        sTimeStop = eTimeStop.date().isoformat()

    else:
        try:
            eTimeStop = eTimeStart + timedelta(minutes=float(eDuration))
        except:
            PrintErrMsg('Duration time (minutes) is invalid\n')
            sys.exit(1)

        sTimeStart = eTimeStart.isoformat()
        sTimeStop = eTimeStop.isoformat()

    return sTimeStart, sTimeStop


def ParseReminder(rem):
    matchObj = re.match(r'^(\d+)([wdhm]?)(?:\s+(popup|email|sms))?$', rem)
    if not matchObj:
        PrintErrMsg('Invalid reminder: ' + rem + '\n')
        sys.exit(1)
    n = int(matchObj.group(1))
    t = matchObj.group(2)
    m = matchObj.group(3)
    if t == 'w':
        n = n * 7 * 24 * 60
    elif t == 'd':
        n = n * 24 * 60
    elif t == 'h':
        n = n * 60

    if not m:
        m = 'popup'

    return n, m


def SIGINT_handler(signum, frame):
    PrintErrMsg('Signal caught, bye!\n')
    sys.exit(1)

