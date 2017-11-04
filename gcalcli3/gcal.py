#!/usr/bin/env python

__program__ = 'gcalcli'
__version__ = 'v4.0.0-alpha'
__author__ = 'Jordan Knott, Eric Davis, Brian Hartvigsen'
__doc__ = '''
Usage:

%s [options] command [command args or options]

 Commands:

  list                     list all calendars

  search <text> [start] [end]
                           search for events within an optional time period
                           - case insensitive search terms to find events that
                             match these terms in any field, like traditional
                             Google search with quotes, exclusion, etc.
                           - for example to get just games: "soccer -practice"
                           - [start] and [end] use the same formats as agenda

  agenda [start] [end]     get an agenda for a time period
                           - start time default is 12am today
                           - end time default is 5 days from start
                           - example time strings:
                              '9/24/2007'
                              '24/09/2007'
                              '24/9/07'
                              'Sep 24 2007 3:30pm'
                              '2007-09-24T15:30'
                              '2007-09-24T15:30-8:00'
                              '20070924T15'
                              '8am'

  calw <weeks> [start]     get a week based agenda in a nice calendar format
                           - weeks is the number of weeks to display
                           - start time default is beginning of this week
                           - note that all events for the week(s) are displayed

  calm [start]             get a month agenda in a nice calendar format
                           - start time default is the beginning of this month
                           - note that all events for the month are displayed
                             and only one month will be displayed

  quick <text>             quick add an event to a calendar
                           - a single --calendar must specified
                           - the "--details url" option will show the event link
                           - example text:
                              'Dinner with Eric 7pm tomorrow'
                              '5pm 10/31 Trick or Treat'

  add                      add a detailed event to a calendar
                           - a single --calendar must specified
                           - the "--details url" option will show the event link
                           - example:
                              gcalcli --calendar 'Eric Davis'
                                      --title 'Analysis of Algorithms Final'
                                      --where UCI
                                      --when '12/14/2012 10:00'
                                      --who 'foo@bar.com'
                                      --who 'baz@bar.com'
                                      --duration 60
                                      --description 'It is going to be hard!'
                                      --reminder 30
                                      add

  delete <text> [start] [end]
                           delete event(s) within the optional time period
                           - case insensitive search terms to find and delete
                             events, just like the 'search' command
                           - deleting is interactive
                             use the --iamaexpert option to auto delete
                             THINK YOU'RE AN EXPERT? USE AT YOUR OWN RISK!!!
                           - use the --details options to show event details
                           - [start] and [end] use the same formats as agenda

  edit <text>              edit event(s)
                           - case insensitive search terms to find and edit
                             events, just like the 'search' command
                           - editing is interactive

  import [file]            import an ics/vcal file to a calendar
                           - a single --calendar must specified
                           - if a file is not specified then the data is read
                             from standard input
                           - if -v is given then each event in the file is
                             displayed and you're given the option to import
                             or skip it, by default everything is imported
                             quietly without any interaction
                           - if -d is given then each event in the file is
                             displayed and is not imported, a --calendar does
                             not need to be specified for this option

  remind <mins> <command>  execute command if event occurs within <mins>
                           minutes time ('%%s' in <command> is replaced with
                           event start time and title text)
                           - <mins> default is 10
                           - default command:
                              'notify-send -u critical -a gcalcli %%s'
'''

__API_CLIENT_ID__ = '232867676714.apps.googleusercontent.com'
__API_CLIENT_SECRET__ = '3tZSxItw6_VnZMezQwC8lUqy'

import json
import shlex
# These are standard libraries and should never fail
import sys
import textwrap
import time
from builtins import str, range
from datetime import datetime, timedelta, date
from unicodedata import east_asian_width

import locale
import os
import random
import re
from past.builtins import raw_input

from . import art, colors, utils

# Required 3rd party libraries
try:
    import attr
    from dateutil.tz import tzlocal
    from dateutil.parser import parse
    import gflags
    import httplib2
    from apiclient.discovery import build
    from apiclient.errors import HttpError
    from oauth2client.file import Storage
    from oauth2client.client import OAuth2WebServerFlow
    from oauth2client.tools import run
except ImportError as e:
    print("ERROR: Missing module - %s" % e.args[0])
    sys.exit(1)

# cPickle is a standard library, but in case someone did something really
# dumb, fall back to pickle.  If that's not their, your python is fucked
try:
    import cPickle as pickle
except ImportError:
    import pickle

# If they have parsedatetime, we'll use it for fuzzy datetime comparison.  If
# not, we just return a fake failure every time and use only dateutil.
try:
    from parsedatetime import Parsedatetime
except BaseException:
    class Parsedatetime:
        class Calendar:
            def parse(self, string):
                return ([], 0)

locale.setlocale(locale.LC_ALL, "")


@attr.s
class Gcalapi(object):
    cache = {}
    all_cals = []
    all_events = []
    cals = []
    now = datetime.now(tzlocal())
    agenda_length = 5
    max_retries = 5
    auth_http = None
    cal_service = None
    url_service = None
    command = 'notify-send -u critical -a gcalcli %s'
    date_parser = utils.DateTimeParser()

    ACCESS_OWNER = 'owner'
    ACCESS_WRITER = 'writer'
    ACCESS_READER = 'reader'
    ACCESS_FREEBUSY = 'freeBusyReader'

    UNIWIDTH = {'W': 2, 'F': 2, 'N': 1, 'Na': 1, 'H': 1, 'A': 1}

    cal_names = attr.ib(default=attr.Factory(list))
    cal_name_colors = attr.ib(default=attr.Factory(list))
    military = attr.ib(default=False)
    detail_calendar = attr.ib(False)
    detail_location = attr.ib(default=False)
    detail_attendees = attr.ib(default=False)
    detail_attachments = attr.ib(default=False)
    detail_length = attr.ib(default=False)
    detail_reminders = attr.ib(default=False)
    detail_descr = attr.ib(default=False)
    detail_descr_width = attr.ib(default=80)
    detail_url = attr.ib(default=None)
    detail_email = attr.ib(default=False)
    ignore_started = attr.ib(default=False)
    ignore_declined = attr.ib(default=False)
    cal_width = attr.ib(default=10)
    cal_monday = attr.ib(default=False)
    cal_owner_color = attr.ib(default=colors.ClrCyn())
    cal_writer_color = attr.ib(default=colors.ClrGrn())
    cal_reader_color = attr.ib(default=colors.ClrMag())
    cal_free_busy_color = attr.ib(default=colors.ClrNrm())
    date_color = attr.ib(default=colors.ClrYlw())
    now_marker_color = attr.ib(default=colors.ClrBrred())
    border_color = attr.ib(default=colors.ClrWht())
    tsv = attr.ib(default=False)
    refresh_cache = attr.ib(default=False)
    use_cache = attr.ib(default=True)
    config_folder = attr.ib(default=None)
    client_id = attr.ib(default=__API_CLIENT_ID__)
    client_secret = attr.ib(default=__API_CLIENT_SECRET__)
    default_reminders = attr.ib(default=True)
    all_day = attr.ib(False)

    def load(self):
        self.__get_cached()
        if len(self.cal_names):
            # Changing the order of this and the `cal in self.allCals` loop
            # is necessary for the matching to actually be sane (ie match
            # supplied name to cached vs matching cache against supplied names)
            for i in range(len(self.cal_names)):
                matches = []
                for cal in self.all_cals:
                    # For exact match, we should match only 1 entry and accept
                    # the first entry.  Should honor access role order since
                    # it happens after _GetCached()
                    print("comparing %s -> %s" %
                          (self.cal_names[i], cal['summary']))
                    if self.cal_names[i] == cal['summary']:
                        # This makes sure that if we have any regex matches
                        # that we toss them out in favor of the specific match
                        matches = [cal]
                        cal['colorSpec'] = self.cal_name_colors[i]
                        break
                    # Otherwise, if the calendar matches as a regex, append
                    # it to the list of potential matches
                    elif re.search(self.cal_names[i], cal['summary'], flags=re.I):
                        matches.append(cal)
                        cal['colorSpec'] = self.cal_name_colors[i]
                # Add relevant matches to the list of calendars we want to
                # operate against
                self.cals += matches
        else:
            self.cals = self.all_cals

    @staticmethod
    def __localize_date_time(dt):
        if not hasattr(dt, 'tzinfo'):
            return dt
        if dt.tzinfo is None:
            return dt.replace(tzinfo=tzlocal())
        else:
            return dt.astimezone(tzlocal())

    def __retry_with_backoff(self, method):
        for n in range(0, self.max_retries):
            try:
                return method.execute()
            except HttpError as e:
                error = json.loads(e.content)
                if error.get('code') == '403' and \
                                error.get('errors')[0].get('reason') \
                                in ['rateLimitExceeded', 'userRateLimitExceeded']:
                    time.sleep((2 ** n) + random.random())
                else:
                    raise

        return None

    def __google_auth(self):
        if not self.auth_http:
            if self.config_folder:
                storage = Storage(os.path.expanduser("%s/oauth" %
                                                     self.config_folder))
            else:
                storage = Storage(os.path.expanduser('~/.gcalcli_oauth'))
            credentials = storage.get()

            if credentials is None or credentials.invalid:
                credentials = run(
                    OAuth2WebServerFlow(
                        client_id=self.client_id,
                        client_secret=self.client_secret,
                        scope=['https://www.googleapis.com/auth/calendar',
                               'https://www.googleapis.com/auth/urlshortener'],
                        user_agent=__program__ + '/' + __version__),
                    storage)

            self.auth_http = credentials.authorize(httplib2.Http())

        return self.auth_http

    def __cal_service(self):
        if not self.cal_service:
            self.cal_service = \
                build(serviceName='calendar',
                      version='v3',
                      http=self.__google_auth())

        return self.cal_service

    def __url_service(self):
        if not self.url_service:
            self.__google_auth()
            self.url_service = \
                build(serviceName='urlshortener',
                      version='v1',
                      http=self.__google_auth())

        return self.url_service

    def __get_cached(self):
        if self.config_folder:
            cache_file = os.path.expanduser("%s/cache" % self.config_folder)
        else:
            cache_file = os.path.expanduser('~/.gcalcli_cache')

        if self.refresh_cache:
            try:
                os.remove(cache_file)
            except OSError:
                pass
                # fall through

        self.cache = {}
        self.all_cals = []

        if self.use_cache:
            # note that we need to use pickle for cache data since we stuff
            # various non-JSON data in the runtime storage structures
            try:
                with open(cache_file, 'rb') as _cache_:
                    self.cache = pickle.load(_cache_)
                    self.all_cals = self.cache['allCals']
                # XXX assuming data is valid, need some verification check here
                return
            except IOError:
                pass
                # fall through

        cal_list = self.__retry_with_backoff(
            self.__cal_service().calendarList().list())

        while True:
            for cal in cal_list['items']:
                self.all_cals.append(cal)
            page_token = cal_list.get('nextPageToken')
            if page_token:
                cal_list = self.__retry_with_backoff(
                    self.__cal_service().calendarList().list(page_token=page_token))
            else:
                break

        # gcalcli defined way to order calendars
        order = {self.ACCESS_OWNER: 1,
                 self.ACCESS_WRITER: 2,
                 self.ACCESS_READER: 3,
                 self.ACCESS_FREEBUSY: 4}

        if self.use_cache:
            self.cache['allCals'] = self.all_cals
            with open(cache_file, 'wb') as _cache_:
                pickle.dump(self.cache, _cache_)

    def __shorten_url(self, url):
        if self.detail_url != "short":
            return url
        # Note that when authenticated to a google account different shortUrls
        # can be returned for the same longUrl. See: http://goo.gl/Ya0A9
        short_url = self.__retry_with_backoff(
            self.__url_service().url().insert(body={'longUrl': url}))
        return short_url['id']

    def __calendar_color(self, cal):

        if cal is None:
            return colors.ClrNrm()
        elif 'colorSpec' in cal and cal['colorSpec'] is not None:
            return cal['colorSpec']
        elif cal['accessRole'] == self.ACCESS_OWNER:
            return self.cal_owner_color
        elif cal['accessRole'] == self.ACCESS_WRITER:
            return self.cal_writer_color
        elif cal['accessRole'] == self.ACCESS_READER:
            return self.cal_reader_color
        elif cal['accessRole'] == self.ACCESS_FREEBUSY:
            return self.cal_free_busy_color
        else:
            return colors.ClrNrm()

    def __valid_title(self, event):
        if 'summary' in event and event['summary'].strip():
            return event['summary']
        else:
            return "(No title)"

    def __is_all_day(self, event):
        return event['s'].hour == 0 and event['s'].minute == 0 and \
               event['e'].hour == 0 and event['e'].minute == 0

    def __get_week_event_strings(self, cmd, cur_month,
                                 start_date_time, end_date_time, event_list):

        week_event_strings = ['', '', '', '', '', '', '']

        now_marker_printed = False
        if self.now < start_date_time or self.now > end_date_time:
            # now isn't in this week
            now_marker_printed = True

        for event in event_list:

            if cmd == 'calm' and cur_month != event['s'].strftime("%b"):
                continue

            day_num = int(event['s'].strftime("%w"))
            if self.cal_monday:
                day_num -= 1
                if day_num < 0:
                    day_num = 6

            if event['s'] >= start_date_time and event['s'] < end_date_time:

                force_event_color_as_marker = False

                all_day = self.__is_all_day(event)

                if not now_marker_printed:
                    if (utils.days_since_epoch(self.now) <
                            utils.days_since_epoch(event['s'])):
                        now_marker_printed = True
                        week_event_strings[day_num - 1] += \
                            ("\n" +
                             str(self.now_marker_color) +
                             (self.cal_width * '-'))
                    elif self.now <= event['s']:
                        # add a line marker before next event
                        now_marker_printed = True
                        week_event_strings[day_num] += \
                            ("\n" +
                             str(self.now_marker_color) +
                             (self.cal_width * '-'))
                    # We don't want to recolor all day events, but ignoring
                    # them leads to issues where the "now" marker misprints
                    # into the wrong day.  This resolves the issue by skipping
                    # all day events for specific coloring but not for previous
                    # or next events
                    elif self.now >= event['s'] and \
                                    self.now <= event['e'] and \
                            not all_day:
                        # line marker is during the event (recolor event)
                        now_marker_printed = True
                        force_event_color_as_marker = True

                if all_day:
                    tmp_time_str = ''
                elif self.military:
                    tmp_time_str = event['s'].strftime("%H:%M")
                else:
                    tmp_time_str = \
                        event['s'].strftime("%I:%M").lstrip('0') + \
                        event['s'].strftime('%p').lower()

                if force_event_color_as_marker:
                    event_color = self.now_marker_color
                else:
                    event_color = self.__calendar_color(event['gcalcli_cal'])

                # newline and empty string are the keys to turn off coloring
                week_event_strings[day_num] += \
                    "\n" + \
                    utils.string_to_unicode(str(event_color)) + \
                    utils.string_to_unicode(tmp_time_str.strip()) + \
                    " " + \
                    self.__valid_title(event).strip()

        return week_event_strings

    def __print_len(self, string):
        # We need to treat everything as unicode for this to actually give
        # us the info we want.  Date string were coming in as `str` type
        # so we convert them to unicode and then check their size. Fixes
        # the output issues we were seeing around non-US locale strings
        string = utils.string_to_unicode(string)
        print_len = 0
        for tmp_char in string:
            print_len += self.UNIWIDTH[east_asian_width(tmp_char)]
        return print_len

    # return print length before cut, cut index, and force cut flag
    def __next_cut(self, string, cur_print_len):
        idx = 0
        print_len = 0
        string = utils.string_to_unicode(string)
        for tmp_char in string:
            if (cur_print_len + print_len) >= self.cal_width:
                return (print_len, idx, True)
            if tmp_char in (' ', '\n'):
                return (print_len, idx, False)
            idx += 1
            print_len += self.UNIWIDTH[east_asian_width(tmp_char)]
        return (print_len, -1, False)

    def __get_cut_index(self, event_string):

        print_len = self.__print_len(event_string)

        if print_len <= self.cal_width:
            if '\n' in event_string:
                idx = event_string.find('\n')
                print_len = self.__print_len(event_string[:idx])
            else:
                idx = len(event_string)

            utils.debug_print("------ printLen=%d (end of string)\n" % idx)
            return (print_len, idx)

        cut_width, cut, force_cut = self.__next_cut(event_string, 0)
        utils.debug_print("------ cutWidth=%d cut=%d \"%s\"\n" %
                          (cut_width, cut, event_string))

        if force_cut:
            utils.debug_print("--- forceCut cutWidth=%d cut=%d\n" %
                              (cut_width, cut))
            return (cut_width, cut)

        utils.debug_print("--- looping\n")

        while cut_width < self.cal_width:

            utils.debug_print("--- cutWidth=%d cut=%d \"%s\"\n" %
                              (cut_width, cut, event_string[cut:]))

            while cut < self.cal_width and \
                            cut < print_len and \
                            event_string[cut] == ' ':
                utils.debug_print("-> skipping space <-\n")
                cut_width += 1
                cut += 1

            utils.debug_print("--- cutWidth=%d cut=%d \"%s\"\n" %
                              (cut_width, cut, event_string[cut:]))

            next_cut_width, next_cut, force_cut = \
                self.__next_cut(event_string[cut:], cut_width)

            if force_cut:
                utils.debug_print("--- forceCut cutWidth=%d cut=%d\n" % (cut_width,
                                                                         cut))
                break

            cut_width += next_cut_width
            cut += next_cut

            if event_string[cut] == '\n':
                break

            utils.debug_print("--- loop cutWidth=%d cut=%d\n" % (cut_width, cut))

        return (cut_width, cut)

    def __graph_events(self, cmd, start_date_time, count, event_list):

        count = int(count)

        # ignore started events (i.e. events that start previous day and end
        # start day)
        while (len(event_list) and event_list[0]['s'] < start_date_time):
            event_list = event_list[1:]

        day_width_line = (self.cal_width * str(art.ArtHrz()))

        top_week_divider = (str(self.border_color) +
                            str(art.ArtUlc()) + day_width_line +
                            (6 * (str(art.ArtUte()) + day_width_line)) +
                            str(art.ArtUrc()) + str(colors.ClrNrm()))

        mid_week_divider = (str(self.border_color) +
                            str(art.ArtLte()) + day_width_line +
                            (6 * (str(art.ArtCrs()) + day_width_line)) +
                            str(art.ArtRte()) + str(colors.ClrNrm()))

        bot_week_divider = (str(self.border_color) +
                            str(art.ArtLlc()) + day_width_line +
                            (6 * (str(art.ArtBte()) + day_width_line)) +
                            str(art.ArtLrc()) + str(colors.ClrNrm()))

        empty = self.cal_width * ' '

        # Get the localized day names... January 1, 2001 was a Monday
        day_names = [date(2001, 1, i + 1).strftime('%A') for i in range(7)]
        day_names = day_names[6:] + day_names[:6]

        day_header = str(self.border_color) + \
                     str(art.ArtVrt()) + str(colors.ClrNrm())
        for i in range(7):
            if self.cal_monday:
                if i == 6:
                    day_name = day_names[0]
                else:
                    day_name = day_names[i + 1]
            else:
                day_name = day_names[i]
            day_name += ' ' * (self.cal_width - self.__print_len(day_name))
            day_header += str(self.date_color) + day_name + str(colors.ClrNrm())
            day_header += str(self.border_color) + str(art.ArtVrt()) + \
                          str(colors.ClrNrm())

        if cmd == 'calm':
            top_month_divider = (str(self.border_color) +
                                 str(art.ArtUlc()) + day_width_line +
                                 (6 * (str(art.ArtHrz()) + day_width_line)) +
                                 str(art.ArtUrc()) + str(colors.ClrNrm()))
            utils.print_msg(colors.ClrNrm(), "\n" + top_month_divider + "\n")

            m = start_date_time.strftime('%B %Y')
            mw = (self.cal_width * 7) + 6
            m += ' ' * (mw - self.__print_len(m))
            utils.print_msg(colors.ClrNrm(),
                            str(self.border_color) +
                            str(art.ArtVrt()) +
                            str(colors.ClrNrm()) +
                            str(self.date_color) +
                            m +
                            str(colors.ClrNrm()) +
                            str(self.border_color) +
                            str(art.ArtVrt()) +
                            str(colors.ClrNrm()) +
                            '\n')

            bot_month_divider = (str(self.border_color) +
                                 str(art.ArtLte()) + day_width_line +
                                 (6 * (str(art.ArtUte()) + day_width_line)) +
                                 str(art.ArtRte()) + str(colors.ClrNrm()))
            utils.print_msg(colors.ClrNrm(), bot_month_divider + "\n")

        else:  # calw
            utils.print_msg(colors.ClrNrm(), "\n" + top_week_divider + "\n")

        utils.print_msg(colors.ClrNrm(), day_header + "\n")
        utils.print_msg(colors.ClrNrm(), mid_week_divider + "\n")

        cur_month = start_date_time.strftime("%b")

        # get date range objects for the first week
        if cmd == 'calm':
            day_num = int(start_date_time.strftime("%w"))
            if self.cal_monday:
                day_num -= 1
                if day_num < 0:
                    day_num = 6
            start_date_time = (start_date_time - timedelta(days=day_num))
        start_week_date_time = start_date_time
        end_week_date_time = (start_week_date_time + timedelta(days=7))

        for i in range(int(count)):

            # create/print date line
            line = str(self.border_color) + \
                   str(art.ArtVrt()) + str(colors.ClrNrm())
            for j in range(7):
                if cmd == 'calw':
                    d = (start_week_date_time +
                         timedelta(days=j)).strftime("%d %b")
                else:  # (cmd == 'calm'):
                    d = (start_week_date_time +
                         timedelta(days=j)).strftime("%d")
                    if cur_month != (start_week_date_time +
                                         timedelta(days=j)).strftime("%b"):
                        d = ''
                tmp_date_color = self.date_color

                if self.now.strftime("%d%b%Y") == \
                        (start_week_date_time + timedelta(days=j)).strftime("%d%b%Y"):
                    tmp_date_color = self.now_marker_color
                    d += " **"

                d += ' ' * (self.cal_width - self.__print_len(d))
                line += str(tmp_date_color) + \
                        d + \
                        str(colors.ClrNrm()) + \
                        str(self.border_color) + \
                        str(art.ArtVrt()) + \
                        str(colors.ClrNrm())
            utils.print_msg(colors.ClrNrm(), line + "\n")

            week_color_strings = ['', '', '', '', '', '', '']
            week_event_strings = self.__get_week_event_strings(cmd, cur_month,
                                                               start_week_date_time,
                                                               end_week_date_time,
                                                               event_list)

            # get date range objects for the next week
            start_week_date_time = end_week_date_time
            end_week_date_time = (end_week_date_time + timedelta(days=7))

            while True:

                done = True
                line = str(self.border_color) + \
                       str(art.ArtVrt()) + str(colors.ClrNrm())

                for j in range(7):

                    if week_event_strings[j] == '':
                        week_color_strings[j] = ''
                        line += (empty +
                                 str(self.border_color) +
                                 str(art.ArtVrt()) +
                                 str(colors.ClrNrm()))
                        continue

                    # get/skip over a color sequence
                    if ((not colors.CLR.conky and week_event_strings[j][0] == '\033') or
                            (colors.CLR.conky and week_event_strings[j][0] == '$')):
                        week_color_strings[j] = ''
                        while ((not colors.CLR.conky and
                                        week_event_strings[j][0] != 'm') or
                                   (colors.CLR.conky and week_event_strings[j][0] != '}')):
                            week_color_strings[j] += week_event_strings[j][0]
                            week_event_strings[j] = week_event_strings[j][1:]
                        week_color_strings[j] += week_event_strings[j][0]
                        week_event_strings[j] = week_event_strings[j][1:]

                    if week_event_strings[j][0] == '\n':
                        week_color_strings[j] = ''
                        week_event_strings[j] = week_event_strings[j][1:]
                        line += (empty +
                                 str(self.border_color) +
                                 str(art.ArtVrt()) +
                                 str(colors.ClrNrm()))
                        done = False
                        continue

                    week_event_strings[j] = week_event_strings[j].lstrip()

                    print_len, cut = self.__get_cut_index(week_event_strings[j])
                    padding = ' ' * (self.cal_width - print_len)

                    line += (week_color_strings[j] +
                             week_event_strings[j][:cut] +
                             padding +
                             str(colors.ClrNrm()))
                    week_event_strings[j] = week_event_strings[j][cut:]

                    done = False
                    line += (str(self.border_color) +
                             str(art.ArtVrt()) +
                             str(colors.ClrNrm()))

                if done:
                    break

                utils.print_msg(colors.ClrNrm(), line + "\n")

            if i < range(count)[len(range(count)) - 1]:
                utils.print_msg(colors.ClrNrm(), mid_week_divider + "\n")
            else:
                utils.print_msg(colors.ClrNrm(), bot_week_divider + "\n")

    def _tsv(self, start_date_time, event_list):
        for event in event_list:
            if self.ignore_started and (event['s'] < self.now):
                continue
            output = "%s\t%s\t%s\t%s" % (event['s'].strftime('%Y-%m-%d'),
                                         event['s'].strftime('%H:%M'),
                                         event['e'].strftime('%Y-%m-%d'),
                                         event['e'].strftime('%H:%M'))

            if self.detail_url:
                output += "\t%s" % (self.__shorten_url(event['htmlLink'])
                                    if 'htmlLink' in event else '')
                output += "\t%s" % (self.__shorten_url(event['hangoutLink'])
                                    if 'hangoutLink' in event else '')

            output += "\t%s" % self.__valid_title(event).strip()

            if self.detail_location:
                output += "\t%s" % (event['location'].strip()
                                    if 'location' in event else '')

            if self.detail_descr:
                output += "\t%s" % (event['description'].strip()
                                    if 'description' in event else '')

            if self.detail_calendar:
                output += "\t%s" % event['gcalcli_cal']['summary'].strip()

            if self.detail_email:
                output += "\t%s" % (event['creator']['email'].strip()
                                    if 'email' in event['creator'] else '')

            output = "%s\n" % output.replace('\n', '''\\n''')
            sys.stdout.write(utils.string_from_unicode(output))

    def __print_event(self, event, prefix):

        def _format_descr(descr, indent, box):
            wrapper = textwrap.TextWrapper()
            if box:
                wrapper.initial_indent = (indent + '  ')
                wrapper.subsequent_indent = (indent + '  ')
                wrapper.width = (self.detail_descr_width - 2)
            else:
                wrapper.initial_indent = indent
                wrapper.subsequent_indent = indent
                wrapper.width = self.detail_descr_width
            new_descr = ""
            for line in descr.split("\n"):
                if box:
                    tmp_line = wrapper.fill(line)
                    for single_line in tmp_line.split("\n"):
                        single_line = single_line.ljust(self.detail_descr_width,
                                                        ' ')
                        new_descr += single_line[:len(indent)] + \
                                     str(art.ArtVrt()) + \
                                     single_line[(len(indent) + 1):
                                     (self.detail_descr_width - 1)] + \
                                     str(art.ArtVrt()) + '\n'
                else:
                    new_descr += wrapper.fill(line) + "\n"
            return new_descr.rstrip()

        indent = 10 * ' '
        details_indent = 19 * ' '

        if self.military:
            time_format = '%-5s'
            tmp_time_str = event['s'].strftime("%H:%M")
        else:
            time_format = '%-7s'
            tmp_time_str = \
                event['s'].strftime("%I:%M").lstrip('0').rjust(5) + \
                event['s'].strftime('%p').lower()

        if not prefix:
            prefix = indent

        utils.print_msg(self.date_color, prefix)

        happening_now = event['s'] <= self.now <= event['e']
        all_day = self.__is_all_day(event)
        event_color = self.now_marker_color if happening_now and not all_day else self.__calendar_color(
            event['gcalcli_cal'])

        if all_day:
            fmt = '  ' + time_format + '  %s\n'
            utils.print_msg(event_color, fmt %
                            ('', self.__valid_title(event).strip()))
        else:
            fmt = '  ' + time_format + '  %s\n'
            utils.print_msg(event_color, fmt % (utils.string_to_unicode(
                tmp_time_str), self.__valid_title(event).strip()))

        if self.detail_calendar:
            xstr = "%s  Calendar: %s\n" % (
                details_indent,
                event['gcalcli_cal']['summary']
            )
            utils.print_msg(colors.ClrNrm(), xstr)

        if self.detail_url and 'htmlLink' in event:
            h_link = self.__shorten_url(event['htmlLink'])
            xstr = "%s  Link: %s\n" % (details_indent, h_link)
            utils.print_msg(colors.ClrNrm(), xstr)

        if self.detail_url and 'hangoutLink' in event:
            h_link = self.__shorten_url(event['hangoutLink'])
            xstr = "%s  Hangout Link: %s\n" % (details_indent, h_link)
            utils.print_msg(colors.ClrNrm(), xstr)

        if self.detail_location and \
                        'location' in event and \
                event['location'].strip():
            xstr = "%s  Location: %s\n" % (
                details_indent,
                event['location'].strip()
            )
            utils.print_msg(colors.ClrNrm(), xstr)

        if self.detail_attendees and 'attendees' in event:
            xstr = "%s  Attendees:\n" % (details_indent)
            utils.print_msg(colors.ClrNrm(), xstr)

            if 'self' not in event['organizer']:
                xstr = "%s    %s: <%s>\n" % (
                    details_indent,
                    event['organizer'].get('displayName', 'Not Provided')
                        .strip(),
                    event['organizer'].get('email', 'Not Provided').strip()
                )
                utils.print_msg(colors.ClrNrm(), xstr)

            for attendee in event['attendees']:
                if 'self' not in attendee:
                    xstr = "%s    %s: <%s>\n" % (
                        details_indent,
                        attendee.get('displayName', 'Not Provided').strip(),
                        attendee.get('email', 'Not Provided').strip()
                    )
                    utils.print_msg(colors.ClrNrm(), xstr)

        if self.detail_attachments and 'attachments' in event:
            xstr = "%s  Attachments:\n" % (details_indent)
            utils.print_msg(colors.ClrNrm(), xstr)

            for attendee in event['attachments']:
                xstr = "%s    %s\n%s    -> %s\n" % (
                    details_indent,
                    attendee.get('title', 'Not Provided').strip(),
                    details_indent,
                    attendee.get('fileUrl', 'Not Provided').strip()
                )
                utils.print_msg(colors.ClrNrm(), xstr)

        if self.detail_length:
            diff_date_time = (event['e'] - event['s'])
            xstr = "%s  Length: %s\n" % (details_indent, diff_date_time)
            utils.print_msg(colors.ClrNrm(), xstr)

        if self.detail_reminders and 'reminders' in event:
            if event['reminders']['useDefault'] is True:
                xstr = "%s  Reminder: (default)\n" % (details_indent)
                utils.print_msg(colors.ClrNrm(), xstr)
            elif 'overrides' in event['reminders']:
                for rem in event['reminders']['overrides']:
                    xstr = "%s  Reminder: %s %d minutes\n" % \
                           (details_indent, rem['method'], rem['minutes'])
                    utils.print_msg(colors.ClrNrm(), xstr)

        if self.detail_email and \
                        'email' in event['creator'] and \
                event['creator']['email'].strip():
            xstr = "%s  Email: %s\n" % (
                details_indent,
                event['creator']['email'].strip()
            )
            utils.print_msg(colors.ClrNrm(), xstr)

        if self.detail_descr and \
                        'description' in event and \
                event['description'].strip():
            descr_indent = details_indent + '  '
            box = True  # leave old non-box code for option later
            if box:
                top_marker = (descr_indent +
                              str(art.ArtUlc()) +
                              (str(art.ArtHrz()) *
                               ((self.detail_descr_width - len(descr_indent)) -
                                2)) +
                              str(art.ArtUrc()))
                bot_marker = (descr_indent +
                              str(art.ArtLlc()) +
                              (str(art.ArtHrz()) *
                               ((self.detail_descr_width - len(descr_indent)) -
                                2)) +
                              str(art.ArtLrc()))
                xstr = "%s  Description:\n%s\n%s\n%s\n" % (
                    details_indent,
                    top_marker,
                    _format_descr(event['description'].strip(),
                                  descr_indent, box),
                    bot_marker
                )
            else:
                marker = descr_indent + '-' * \
                                        (self.detail_descr_width - len(descr_indent))
                xstr = "%s  Description:\n%s\n%s\n%s\n" % (
                    details_indent,
                    marker,
                    _format_descr(event['description'].strip(),
                                  descr_indent, box),
                    marker
                )
            utils.print_msg(colors.ClrNrm(), xstr)

    def __delete_event(self, event):

        if self.iama_expert:
            self.__retry_with_backoff(
                self.__cal_service().events().
                    delete(calendarId=event['gcalcli_cal']['id'],
                           eventId=event['id']))
            utils.print_msg(colors.ClrRed(), "Deleted!\n")
            return

        utils.print_msg(colors.ClrMag(), "Delete? [N]o [y]es [q]uit: ")
        val = raw_input()

        if not val or val.lower() == 'n':
            return

        elif val.lower() == 'y':
            self.__retry_with_backoff(
                self.__cal_service().events().
                    delete(calendarId=event['gcalcli_cal']['id'],
                           eventId=event['id']))
            utils.print_msg(colors.ClrRed(), "Deleted!\n")

        elif val.lower() == 'q':
            sys.stdout.write('\n')
            sys.exit(0)

        else:
            utils.print_err_msg('Error: invalid input\n')
            sys.stdout.write('\n')
            sys.exit(1)

    def __edit_event(self, event):

        while True:

            utils.print_msg(colors.ClrMag(), "Edit?\n" +
                            "[N]o [s]ave [q]uit " +
                            "[t]itle [l]ocation " +
                            "[w]hen len[g]th " +
                            "[r]eminder [d]escr: ")
            val = raw_input()

            if not val or val.lower() == 'n':
                return

            elif val.lower() == 's':
                # copy only editable event details for patching
                mod_event = {}
                keys = ['summary', 'location', 'start', 'end',
                        'reminders', 'description']
                for k in keys:
                    if k in event:
                        mod_event[k] = event[k]

                self.__retry_with_backoff(
                    self.__cal_service().events().
                        patch(calendarId=event['gcalcli_cal']['id'],
                              eventId=event['id'],
                              body=mod_event))
                utils.print_msg(colors.ClrRed(), "Saved!\n")
                return

            elif not val or val.lower() == 'q':
                sys.stdout.write('\n')
                sys.exit(0)

            elif val.lower() == 't':
                utils.print_msg(colors.ClrMag(), "Title: ")
                val = raw_input()
                if val.strip():
                    event['summary'] = \
                        utils.string_to_unicode(val.strip())

            elif val.lower() == 'l':
                utils.print_msg(colors.ClrMag(), "Location: ")
                val = raw_input()
                if val.strip():
                    event['location'] = \
                        utils.string_to_unicode(val.strip())

            elif val.lower() == 'w':
                utils.print_msg(colors.ClrMag(), "When: ")
                val = raw_input()
                if val.strip():
                    td = (event['e'] - event['s'])
                    length = ((td.days * 1440) + (td.seconds / 60))
                    new_start, new_end = utils.get_time_from_str(
                        val.strip(), length)
                    event['s'] = parse(new_start)
                    event['e'] = parse(new_end)

                    if self.all_day:
                        event['start'] = {'date': new_start,
                                          'dateTime': None,
                                          'timeZone': None}
                        event['end'] = {'date': new_end,
                                        'dateTime': None,
                                        'timeZone': None}

                    else:
                        event['start'] = {'date': None,
                                          'dateTime': new_start,
                                          'timeZone': event['gcalcli_cal']['timeZone']}
                        event['end'] = {'date': None,
                                        'dateTime': new_end,
                                        'timeZone': event['gcalcli_cal']['timeZone']}

            elif val.lower() == 'g':
                utils.print_msg(colors.ClrMag(), "Length (mins): ")
                val = raw_input()
                if val.strip():
                    new_start, new_end = \
                        utils.get_time_from_str(
                            event['start']['dateTime'], val.strip())
                    event['s'] = parse(new_start)
                    event['e'] = parse(new_end)

                    if self.all_day:
                        event['start'] = {'date': new_start,
                                          'dateTime': None,
                                          'timeZone': None}
                        event['end'] = {'date': new_end,
                                        'dateTime': None,
                                        'timeZone': None}

                    else:
                        event['start'] = {'date': None,
                                          'dateTime': new_start,
                                          'timeZone': event['gcalcli_cal']['timeZone']}
                        event['end'] = {'date': None,
                                        'dateTime': new_end,
                                        'timeZone': event['gcalcli_cal']['timeZone']}

            elif val.lower() == 'r':
                rem = []
                while True:
                    utils.print_msg(colors.ClrMag(),
                                    "Enter a valid reminder or '.' to end: ")
                    r = raw_input()
                    if r == '.':
                        break
                    rem.append(r)

                if rem or not self.default_reminders:
                    event['reminders'] = {'useDefault': False,
                                          'overrides': []}
                    for r in rem:
                        n, m = utils.parse_reminder(r)
                        event['reminders']['overrides'].append({'minutes': n,
                                                                'method': m})
                else:
                    event['reminders'] = {'useDefault': True,
                                          'overrides': []}

            elif val.lower() == 'd':
                utils.print_msg(colors.ClrMag(), "Description: ")
                val = raw_input()
                if val.strip():
                    event['description'] = \
                        utils.string_to_unicode(val.strip())

            else:
                utils.print_err_msg('Error: invalid input\n')
                sys.stdout.write('\n')
                sys.exit(1)

            self.__print_event(event, event['s'].strftime('\n%Y-%m-%d'))

    def __iterate_events(self, start_date_time, event_list,
                         year_date=False, work=None):

        if len(event_list) == 0:
            utils.print_msg(colors.ClrYlw(), "\nNo Events Found...\n")
            return

        # 10 chars for day and length must match 'indent' in _PrintEvent
        day_format = '\n%Y-%m-%d' if year_date else '\n%a %b %d'
        day = ''

        for event in event_list:

            if self.ignore_started and (event['s'] < self.now):
                continue
            if self.ignore_declined:
                if 'attendees' in event:
                    attendee = [a for a in event['attendees']
                                if a['email'] == event['gcalcli_cal']['id']][0]
                    if attendee and attendee['responseStatus'] == 'declined':
                        continue

            tmp_day_str = event['s'].strftime(day_format)
            prefix = None
            if year_date or tmp_day_str != day:
                day = prefix = tmp_day_str

            self.__print_event(event, prefix)

            if work:
                work(event)

    def __get_all_events(self, cal, events, end):

        event_list = []

        while True:
            if 'items' not in events:
                break

            for event in events['items']:

                event['gcalcli_cal'] = cal

                if 'status' in event and event['status'] == 'cancelled':
                    continue

                if 'dateTime' in event['start']:
                    event['s'] = parse(event['start']['dateTime'])
                else:
                    # all date events
                    event['s'] = parse(event['start']['date'])

                event['s'] = self.__localize_date_time(event['s'])

                if 'dateTime' in event['end']:
                    event['e'] = parse(event['end']['dateTime'])
                else:
                    # all date events
                    event['e'] = parse(event['end']['date'])

                event['e'] = self.__localize_date_time(event['e'])

                # For all-day events, Google seems to assume that the event
                # time is based in the UTC instead of the local timezone.  Here
                # we filter out those events start beyond a specified end time.
                if end and (event['s'] >= end):
                    continue

                # http://en.wikipedia.org/wiki/Year_2038_problem
                # Catch the year 2038 problem here as the python dateutil
                # module can choke throwing a ValueError exception. If either
                # the start or end time for an event has a year '>= 2038' dump
                # it.
                if event['s'].year >= 2038 or event['e'].year >= 2038:
                    continue

                event_list.append(event)

            page_token = events.get('nextPageToken')
            if page_token:
                events = self.__retry_with_backoff(
                    self.__cal_service().events().
                        list(calendarId=cal['id'], page_token=page_token))
            else:
                break

        return event_list

    def __search_for_cal_events(self, start, end, search_text):

        event_list = []
        for cal in self.cals:
            work = self.__cal_service().events(). \
                list(calendarId=cal['id'],
                     timeMin=start.isoformat() if start else None,
                     timeMax=end.isoformat() if end else None,
                     q=search_text if search_text else None,
                     singleEvents=True)
            events = self.__retry_with_backoff(work)
            event_list.extend(self.__get_all_events(cal, events, end))

        return event_list

    def list_all_calendars(self):

        access_len = 0

        for cal in self.all_cals:
            length = len(cal['accessRole'])
            if length > access_len:
                access_len = length

        if access_len < len('Access'):
            access_len = len('Access')

        format = ' %0' + str(access_len) + 's  %s\n'

        utils.print_msg(colors.ClrBrylw(), format % ('Access', 'Title'))
        utils.print_msg(colors.ClrBrylw(), format % ('------', '-----'))

        for cal in self.all_cals:
            utils.print_msg(self.__calendar_color(cal),
                            format % (cal['accessRole'], cal['summary']))

    def text_query(self, search_text='', start_text='', end_text=''):

        # the empty string would get *ALL* events...
        if search_text == '':
            return

        # This is really just an optimization to the gcalendar api
        # why ask for a bunch of events we are going to filter out
        # anyway?
        # TODO: Look at moving this into the _SearchForCalEvents
        #       Don't forget to clean up AgendaQuery too!

        if start_text == '':
            start = self.now if self.ignore_started else None
        else:
            try:
                start = self.date_parser.from_string(start_text)
            except BaseException:
                utils.print_err_msg('Error: failed to parse start time\n')
                return

        if end_text == '':
            end = None
        else:
            try:
                end = self.date_parser.from_string(end_text)
            except BaseException:
                utils.print_err_msg('Error: failed to parse end time\n')
                return

        event_list = self.__search_for_cal_events(start, end, search_text)

        if self.tsv:
            self._tsv(self.now, event_list)
        else:
            self.__iterate_events(self.now, event_list, year_date=True)

    def agenda_query(self, start_text='', end_text=''):

        if start_text == '':
            # convert now to midnight this morning and use for default
            start = self.now.replace(hour=0,
                                     minute=0,
                                     second=0,
                                     microsecond=0)
        else:
            try:
                start = self.date_parser.from_string(start_text)
            except BaseException:
                utils.print_err_msg('Error: failed to parse start time\n')
                return

        # Again optimizing calls to the api.  If we've been told to
        # ignore started events, then it doesn't make ANY sense to
        # search for things that may be in the past
        if self.ignore_started and start < self.now:
            start = self.now

        if end_text == '':
            end = (start + timedelta(days=self.agenda_length))
        else:
            try:
                end = self.date_parser.from_string(end_text)
            except BaseException:
                utils.print_err_msg('Error: failed to parse end time\n')
                return

        event_list = self.__search_for_cal_events(start, end, None)

        if self.tsv:
            self._tsv(start, event_list)
        else:
            self.__iterate_events(start, event_list, year_date=False)

    def cal_query(self, cmd, start_text='', count=1):

        if start_text == '':
            # convert now to midnight this morning and use for default
            start = self.now.replace(hour=0,
                                     minute=0,
                                     second=0,
                                     microsecond=0)
        else:
            try:
                start = self.date_parser.from_string(start_text)
                start = start.replace(hour=0, minute=0, second=0,
                                      microsecond=0)
            except BaseException:
                utils.print_err_msg('Error: failed to parse start time\n')
                return

        # convert start date to the beginning of the week or month
        if cmd == 'calw':
            day_num = int(start.strftime("%w"))
            if self.cal_monday:
                day_num -= 1
                if day_num < 0:
                    day_num = 6
            start = (start - timedelta(days=day_num))
            end = (start + timedelta(days=(count * 7)))
        else:  # cmd == 'calm':
            start = (start - timedelta(days=(start.day - 1)))
            end_month = (start.month + 1)
            end_year = start.year
            if end_month == 13:
                end_month = 1
                end_year += 1
            end = start.replace(month=end_month, year=end_year)
            days_in_month = (end - start).days
            offset_days = int(start.strftime('%w'))
            if self.cal_monday:
                offset_days -= 1
                if offset_days < 0:
                    offset_days = 6
            total_days = (days_in_month + offset_days)
            count = (total_days / 7)
            if total_days % 7:
                count += 1

        event_list = self.__search_for_cal_events(start, end, None)

        self.__graph_events(cmd, start, count, event_list)

    def quick_add_event(self, event_text, reminder=None):

        if event_text == '':
            return

        if len(self.cals) > 1:
            utils.print_err_msg("You must only specify a single calendar\n")
            return

        if len(self.cals) < 1:
            utils.print_err_msg(
                "Calendar not specified or not found.\nIf \"gcalcli list\" doesn't find the calendar you're trying to use,\nyour cache file might be stale and you might need to remove it and try again\n")
            return

        new_event = self.__retry_with_backoff(
            self.__cal_service().events().quickAdd(calendarId=self.cals[0]['id'],
                                                   text=event_text))

        if reminder or not self.default_reminders:
            rem = {}
            rem['reminders'] = {'useDefault': False,
                                'overrides': []}
            for r in reminder:
                n, m = utils.parse_reminder(r)
                rem['reminders']['overrides'].append({'minutes': n,
                                                      'method': m})

            new_event = self.__retry_with_backoff(
                self.__cal_service().events().
                    patch(calendarId=self.cals[0]['id'],
                          eventId=new_event['id'],
                          body=rem))

        if self.detail_url:
            h_link = self.__shorten_url(new_event['htmlLink'])
            utils.print_msg(colors.ClrGrn(), 'New event added: %s\n' % h_link)

    def add_event(self, e_title, e_where, e_start, e_end, e_descr, e_who, reminder):

        if len(self.cals) != 1:
            utils.print_err_msg("Must specify a single calendar\n")
            return

        event = {}
        event['summary'] = utils.string_to_unicode(e_title)

        if self.all_day:
            event['start'] = {'date': e_start}
            event['end'] = {'date': e_end}
            print("All day!")

        else:
            event['start'] = {'dateTime': e_start,
                              'timeZone': self.cals[0]['timeZone']}
            event['end'] = {'dateTime': e_end,
                            'timeZone': self.cals[0]['timeZone']}
            print("Not all day!")

        if e_where:
            event['location'] = utils.string_to_unicode(e_where)
        if e_descr:
            event['description'] = utils.string_to_unicode(e_descr)

        event['attendees'] = list(
            map(lambda w: {'email': utils.string_to_unicode(w)}, e_who))

        if reminder or not self.default_reminders:
            event['reminders'] = {'useDefault': False,
                                  'overrides': []}
            for r in reminder:
                n, m = utils.parse_reminder(r)
                event['reminders']['overrides'].append({'minutes': n,
                                                        'method': m})

        print(str(event))
        new_event = self.__retry_with_backoff(
            self.__cal_service().events().
                insert(calendarId=self.cals[0]['id'], body=(event)))

        if self.detail_url:
            h_link = self.__shorten_url(new_event['htmlLink'])
            utils.print_msg(colors.ClrGrn(), 'New event added: %s\n' % h_link)

    def delete_events(self, search_text='', expert=False, start=None, end=None):

        # the empty string would get *ALL* events...
        if search_text == '':
            return

        event_list = self.__search_for_cal_events(start, end, search_text)

        self.iama_expert = expert
        self.__iterate_events(self.now, event_list,
                              year_date=True, work=self.__delete_event)

    def edit_events(self, search_text=''):

        # the empty string would get *ALL* events...
        if search_text == '':
            return

        event_list = self.__search_for_cal_events(None, None, search_text)

        self.__iterate_events(self.now, event_list,
                              year_date=True, work=self.__edit_event)

    def remind(self, minutes=10, command=None, use_reminders=False):
        """Check for events between now and now+minutes.
           If use_reminders then only remind if now >= event['start'] - reminder
    """

        if command is None:
            command = self.command

        # perform a date query for now + minutes + slip
        start = self.now
        end = (start + timedelta(minutes=(minutes + 5)))

        event_list = self.__search_for_cal_events(start, end, None)

        message = ''

        for event in event_list:

            # skip this event if it already started
            # XXX maybe add a 2+ minute grace period here...
            if event['s'] < self.now:
                continue

            # not sure if 'reminders' always in event
            if use_reminders and 'reminders' in event and 'overrides' in event['reminders']:
                if all(event['s'] - timedelta(minutes=r['minutes']) > self.now
                       for r in event['reminders']['overrides']):
                    continue  # don't remind if all reminders haven't arrived yet

            if self.military:
                tmp_time_str = event['s'].strftime('%H:%M')
            else:
                tmp_time_str = \
                    event['s'].strftime('%I:%M').lstrip('0') + \
                    event['s'].strftime('%p').lower()

            message += '%s  %s\n' % \
                       (tmp_time_str, self.__valid_title(event).strip())

        if message == '':
            return

        cmd = shlex.split(command)

        for i, a in zip(range(len(cmd)), cmd):
            if a == '%s':
                cmd[i] = message

        pid = os.fork()
        if not pid:
            os.execvp(cmd[0], cmd)

    def import_ics(self, verbose=False, dump=False, reminder=None,
                   icsFile=None):

        def create_event_from_vobj(ve):

            event = {}

            if verbose:
                print("+----------------+")
                print("| Calendar Event |")
                print("+----------------+")

            if hasattr(ve, 'summary'):
                utils.debug_print("SUMMARY: %s\n" % ve.summary.value)
                if verbose:
                    print("Event........%s" % ve.summary.value)
                event['summary'] = ve.summary.value

            if hasattr(ve, 'location'):
                utils.debug_print("LOCATION: %s\n" % ve.location.value)
                if verbose:
                    print("Location.....%s" % ve.location.value)
                event['location'] = ve.location.value

            if not hasattr(ve, 'dtstart') or not hasattr(ve, 'dtend'):
                utils.print_err_msg("Error: event does not have a dtstart and "
                                    "dtend!\n")
                return None

            if ve.dtstart.value:
                utils.debug_print("DTSTart.ART: %s\n" %
                                  ve.dtstart.value.isoformat())
            if ve.dtend.value:
                utils.debug_print("DTEND: %s\n" % ve.dtend.value.isoformat())
            if verbose:
                if ve.dtstart.value:
                    print("Start........%s" %
                          ve.dtstart.value.isoformat())
                if ve.dtend.value:
                    print("End..........%s" %
                          ve.dtend.value.isoformat())
                if ve.dtstart.value:
                    print("Local Start..%s" %
                          self.__localize_date_time(ve.dtstart.value))
                if ve.dtend.value:
                    print("Local End....%s" %
                          self.__localize_date_time(ve.dtend.value))

            if hasattr(ve, 'rrule'):

                utils.debug_print("RRULE: %s\n" % ve.rrule.value)
                if verbose:
                    print("Recurrence...%s" % ve.rrule.value)

                event['recurrence'] = ["RRULE:" + ve.rrule.value]

            if hasattr(ve, 'dtstart') and ve.dtstart.value:
                # XXX
                # Timezone madness! Note that we're using the timezone for the
                # calendar being added to. This is OK if the event is in the
                # same timezone. This needs to be changed to use the timezone
                # from the DTSTart.ART and DTEND values. Problem is, for example,
                # the TZID might be "Pacific Standard Time" and Google expects
                # a timezone string like "America/Los_Angeles". Need to find
                # a way in python to convert to the more specific timezone
                # string.
                # XXX
                # print ve.dtstart.params['X-VOBJ-ORIGINAL-TZID'][0]
                # print self.cals[0]['timeZone']
                # print dir(ve.dtstart.value.tzinfo)
                # print vars(ve.dtstart.value.tzinfo)

                start = ve.dtstart.value.isoformat()
                if isinstance(ve.dtstart.value, datetime):
                    event['start'] = {'dateTime': start,
                                      'timeZone': self.cals[0]['timeZone']}
                else:
                    event['start'] = {'date': start}

                if reminder or not self.default_reminders:
                    event['reminders'] = {'useDefault': False,
                                          'overrides': []}
                    for r in reminder:
                        n, m = utils.parse_reminder(r)
                        event['reminders']['overrides'].append({'minutes': n,
                                                                'method': m})

                # Can only have an end if we have a start, but not the other
                # way around apparently...  If there is no end, use the start
                if hasattr(ve, 'dtend') and ve.dtend.value:
                    end = ve.dtend.value.isoformat()
                    if isinstance(ve.dtend.value, datetime):
                        event['end'] = {'dateTime': end,
                                        'timeZone': self.cals[0]['timeZone']}
                    else:
                        event['end'] = {'date': end}

                else:
                    event['end'] = event['start']

            if hasattr(ve, 'description') and ve.description.value.strip():
                descr = ve.description.value.strip()
                utils.debug_print("DESCRIPTION: %s\n" % descr)
                if verbose:
                    print("Description:\n%s" % descr)
                event['description'] = descr

            if hasattr(ve, 'organizer'):
                utils.debug_print("ORGANIZER: %s\n" % ve.organizer.value)

                if ve.organizer.value.startswith("MAILTO:"):
                    email = ve.organizer.value[7:]
                else:
                    email = ve.organizer.value
                if verbose:
                    print("organizer:\n %s" % email)
                event['organizer'] = {'displayName': ve.organizer.name,
                                      'email': email}

            if hasattr(ve, 'attendee_list'):
                utils.debug_print("ATTENDEE_LIST : %s\n" % ve.attendee_list)
                if verbose:
                    print("attendees:")
                event['attendees'] = []
                for attendee in ve.attendee_list:
                    if attendee.value.upper().startswith("MAILTO:"):
                        email = attendee.value[7:]
                    else:
                        email = attendee.value
                    if verbose:
                        print(" %s" % email)

                    event['attendees'].append({'displayName': attendee.name,
                                               'email': email})

            return event

        try:
            import vobject
        except BaseException:
            utils.print_err_msg('Python vobject module not installed!\n')
            sys.exit(1)

        if dump:
            verbose = True

        if not dump and len(self.cals) != 1:
            utils.print_err_msg("Must specify a single calendar\n")
            return

        f = sys.stdin

        if icsFile:
            try:
                f = open(icsFile)
            except Exception as e:
                utils.print_err_msg("Error: " + str(e) + "!\n")
                sys.exit(1)

        while True:

            try:
                v = vobject.readComponents(f).next()
            except StopIteration:
                break

            for ve in v.vevent_list:

                event = create_event_from_vobj(ve)

                if not event:
                    continue

                if dump:
                    continue

                if not verbose:
                    newEvent = self.__retry_with_backoff(
                        self.__cal_service().events().
                            insert(calendarId=self.cals[0]['id'],
                                   body=event))
                    hLink = self.__shorten_url(newEvent['htmlLink'])
                    utils.print_msg(colors.ClrGrn(),
                                    'New event added: %s\n' % hLink)
                    continue

                utils.print_msg(colors.ClrMag(), "\n[S]kip [i]mport [q]uit: ")
                val = raw_input()
                if not val or val.lower() == 's':
                    continue
                if val.lower() == 'i':
                    newEvent = self.__retry_with_backoff(
                        self.__cal_service().events().
                            insert(calendarId=self.cals[0]['id'],
                                   body=event))
                    hLink = self.__shorten_url(newEvent['htmlLink'])
                    utils.print_msg(colors.ClrGrn(),
                                    'New event added: %s\n' % hLink)
                elif val.lower() == 'q':
                    sys.exit(0)
                else:
                    utils.print_err_msg('Error: invalid input\n')
                    sys.exit(1)


def parse_color_options(set_color):
    """Parses color options and returns them formatted correctly to be consumed by a Gcalapi object"""
    valid_color_options = ["owner", "writer", "reader", "freebusy", "date", "nowmarker", "border"]
    color_options = {}
    for opt in set_color:
        if opt[0] not in valid_color_options:
            raise ValueError("Not a valid color type!")
        color_options[opt[0] + "_color"] = opt[1]
    return color_options


def setup_gcal(color, lineart, conky, user_locale, calendar, default_calendar,
               cache, client_id, client_secret, set_color, config_folder, details, include_config,
               military, monday, refresh, started):
    if not color:
        colors.CLR.use_color = False

    if not lineart:
        art.ART.use_art = False

    if conky:
        colors.set_conky_colors()

    if user_locale:
        try:
            locale.setlocale(locale.LC_ALL, user_locale)
        except Exception as e:
            utils.print_err_msg("Error: " + str(e) + "!\n"
                                                     "Check supported locales of your system.\n")
            sys.exit(1)

    if len(calendar) == 0:
        calendar = default_calendar

    cal_name_colors = []
    cal_colors = colors.get_cal_colors(calendar)
    cal_names_filtered = []
    for cal_name in calendar:
        cal_name_simple = cal_name.split("#")[0]
        cal_names_filtered.append(str(cal_name_simple))
        cal_name_colors.append(cal_colors[cal_name_simple])
    cal_names = cal_names_filtered
    gcal = Gcalapi(cal_names, cal_name_colors, cache=cache, client_id=client_id, client_secret=client_secret,
                   military=military, monday=module, refresh=refresh, started=started)
    return gcal
