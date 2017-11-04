import signal

import click

from . import gcal as gcalapi
from . import validators, colors, utils

from past.builtins import raw_input


@click.command("agenda")
@click.option("--cache/--no-cache", default=True,
              help="Execute command without using cache")
@click.option("--calendar", default=[], help="Which calendars to use;" +
                                             "repeat this option to specify a list of values")
@click.option("--client-id", default=None, help="API client_id")
@click.option("--client-secret", default=None, help="API client_secret")
@click.option("--color/--no-color", default=True,
              help="Enabled/Disable all color output")
@click.option("--set-color", nargs=2, default=[], multiple=True,
              callback=validators.validate_set_color)
@click.option("--config-folder", default=None,
              help="Optional directory to load/store all configuration information")
@click.option("--conky/--no-conky", default=False,
              help="Use Conky color codes")
@click.option("--default-calendar", default=[],
              help="Optional default calendar to use if no --calendar options are given; " +
                   "repeat this this option to speciy a list of values")
@click.option("--details", type=click.Choice(["all", "calendar", "location", "length", "reminders",
                                              "description", "longurl", "shorturl", "url", "attendees", "email"]),
              multiple=True,
              help="Which parts to display. Repeat this option to specify a list of values")
@click.option("--include-config/--no-include-config", default=False,
              help="Whether to include ~/.gcalapi.gcalapirc when using --config-folder")
@click.option("--lineart/--no-lineart", default=True,
              help="Enable/Disable line art")
@click.option("--locale", "user_locale", default=None, help="System locale")
@click.option("--military/--no-military",
              default=False, help="Use 24 hour display")
@click.option("--monday/--no-monday", default=False,
              help="Start the week on Monday")
@click.option("--refresh/--no-refresh", default=False,
              help="Delete and refresh cached data")
@click.option("--started/--no-started", default=True,
              help="Show events that have started")
@click.option("--verbose", "-v", default=False, help="Show logs")
def show_agenda(cache, calendar, client_id, client_secret, color, set_color, config_folder, conky,
                default_calendar, details, include_config, lineart, user_locale, military, monday, refresh, started,
                verbose):
    """Shows the current agenda. Uses the default calendar unless otherwise specified"""

    cal_names, cal_name_colors = gcalapi.setup_gcal(
        color, lineart, conky, user_locale, calendar, default_calendar)
    gcal = gcalapi.Gcalapi(cal_names=cal_names,
                           cal_name_colors=cal_name_colors)
    gcal.load()
    gcal.agenda_query()


@click.command("list")
@click.option("--cache/--no-cache", default=True,
              help="Execute command without using cache")
@click.option("--calendar", default=[], help="Which calendars to use;" +
                                             "repeat this option to specify a list of values")
@click.option("--client-id", default=None, help="API client_id")
@click.option("--client-secret", default=None, help="API client_secret")
@click.option("--color/--no-color", default=True,
              help="Enabled/Disable all color output")
@click.option("--set-color", nargs=2, default=[], multiple=True,
              callback=validators.validate_set_color)
@click.option("--config-folder", default=None,
              help="Optional directory to load/store all configuration information")
@click.option("--conky/--no-conky", default=False,
              help="Use Conky color codes")
@click.option("--default-calendar", default=[],
              help="Optional default calendar to use if no --calendar options are given; " +
                   "repeat this this option to speciy a list of values")
@click.option("--include-config/--no-include-config", default=False,
              help="Whether to include ~/.gcalapi.gcalapirc when using --config-folder")
@click.option("--locale", "user_locale", default=None, help="System locale")
@click.option("--military/--no-military",
              default=False, help="Use 24 hour display")
@click.option("--monday/--no-monday", default=False,
              help="Start the week on Monday")
@click.option("--refresh/--no-refresh", default=False,
              help="Delete and refresh cached data")
@click.option("--started/--no-started", default=True,
              help="Show events that have started")
@click.option("--verbose", "-v", default=False, help="Show logs")
def list_calendars(cache, calendar, client_id, client_secret, color, set_color, config_folder, conky,
                   default_calendar, include_config, user_locale, military, monday, refresh, started,
                   verbose):
    """Shows the current agenda. Uses the default calendar unless otherwise specified"""

    cal_names, cal_name_colors = gcalapi.setup_gcal(
        color, False, conky, user_locale, calendar, default_calendar)
    gcal = gcalapi.Gcalapi(cal_names=cal_names,
                           cal_name_colors=cal_name_colors)
    gcal.load()
    gcal.list_all_calendars()


@click.command("search")
@click.argument("query")
@click.option("--start-date", "-s", default=None,
              help="The starting date to start searching events from")
@click.option("--end-date", "-e", default=None,
              help="The ending date to start searching events to")
@click.option("--cache/--no-cache", default=True,
              help="Execute command without using cache")
@click.option("--calendar", default=[], help="Which calendars to use;" +
                                             "repeat this option to specify a list of values")
@click.option("--client-id", default=None, help="API client_id")
@click.option("--client-secret", default=None, help="API client_secret")
@click.option("--color/--no-color", default=True,
              help="Enabled/Disable all color output")
@click.option("--set-color", nargs=2, default=[], multiple=True,
              callback=validators.validate_set_color)
@click.option("--config-folder", default=None,
              help="Optional directory to load/store all configuration information")
@click.option("--conky/--no-conky", default=False,
              help="Use Conky color codes")
@click.option("--default-calendar", default=[],
              help="Optional default calendar to use if no --calendar options are given; " +
                   "repeat this this option to speciy a list of values")
@click.option("--details", type=click.Choice(["all", "calendar", "location", "length", "reminders",
                                              "description", "longurl", "shorturl", "url", "attendees", "email"]),
              multiple=True,
              help="Which parts to display. Repeat this option to specify a list of values")
@click.option("--include-config/--no-include-config", default=False,
              help="Whether to include ~/.gcalapi.gcalapirc when using --config-folder")
@click.option("--lineart/--no-lineart", default=True,
              help="Enable/Disable line art")
@click.option("--locale", "user_locale", default=None, help="System locale")
@click.option("--military/--no-military",
              default=False, help="Use 24 hour display")
@click.option("--monday/--no-monday", default=False,
              help="Start the week on Monday")
@click.option("--refresh/--no-refresh", default=False,
              help="Delete and refresh cached data")
@click.option("--started/--no-started", default=True,
              help="Show events that have started")
@click.option("--verbose", "-v", default=False, help="Show logs")
@click.option("--tsv", default=False,
              help="Show output using tab seperated values")
def search_events(query, start_date, end_date, cache, calendar, client_id, client_secret, color, set_color,
                  config_folder, conky,
                  default_calendar, details, include_config, lineart, user_locale, military, monday, refresh, started,
                  verbose, tsv):
    """Shows the current agenda. Uses the default calendar unless otherwise specified"""

    cal_names, cal_name_colors = gcalapi.setup_gcal(
        color, lineart, conky, user_locale, calendar, default_calendar)
    gcal = gcalapi.Gcalapi(cal_names=cal_names,
                           cal_name_colors=cal_name_colors)
    gcal.load()

    if start_date is None and end_date is None:
        gcal.text_query(query)
    elif start_date is not None and end_date is None:
        gcal.text_query(query, start_date)
    elif start_date is not None and end_date is not None:
        gcal.text_query(query, start_date, end_date)
    else:
        raise click.BadParameter(
            "--start-date should be used alongside --end-date!")


@click.command("calw")
@click.option("--start-date", "-s", default=None,
              help="The starting date to start searching events from")
@click.option("--end-date", "-e", default=None,
              help="The ending date to start searching events to")
@click.option("--cache/--no-cache", default=True,
              help="Execute command without using cache")
@click.option("--calendar", default=[], help="Which calendars to use;" +
                                             "repeat this option to specify a list of values")
@click.option("--client-id", default=None, help="API client_id")
@click.option("--client-secret", default=None, help="API client_secret")
@click.option("--color/--no-color", default=True,
              help="Enabled/Disable all color output")
@click.option("--set-color", nargs=2, default=[], multiple=True,
              callback=validators.validate_set_color)
@click.option("--config-folder", default=None,
              help="Optional directory to load/store all configuration information")
@click.option("--conky/--no-conky", default=False,
              help="Use Conky color codes")
@click.option("--default-calendar", default=[],
              help="Optional default calendar to use if no --calendar options are given; " +
                   "repeat this this option to speciy a list of values")
@click.option("--details", type=click.Choice(["all", "calendar", "location", "length", "reminders",
                                              "description", "longurl", "shorturl", "url", "attendees", "email"]),
              multiple=True,
              help="Which parts to display. Repeat this option to specify a list of values")
@click.option("--include-config/--no-include-config", default=False,
              help="Whether to include ~/.gcalapi.gcalapirc when using --config-folder")
@click.option("--lineart/--no-lineart", default=True,
              help="Enable/Disable line art")
@click.option("--locale", "user_locale", default=None, help="System locale")
@click.option("--military/--no-military",
              default=False, help="Use 24 hour display")
@click.option("--monday/--no-monday", default=False,
              help="Start the week on Monday")
@click.option("--refresh/--no-refresh", default=False,
              help="Delete and refresh cached data")
@click.option("--started/--no-started", default=True,
              help="Show events that have started")
@click.option("--verbose", "-v", default=False, help="Show logs")
@click.option("--tsv/--no-tsv", default=False,
              help="Show output using tab seperated values")
def show_calendar_week(start_date, end_date, cache, calendar, client_id, client_secret, color, set_color,
                       config_folder, conky,
                       default_calendar, details, include_config, lineart, user_locale, military, monday, refresh,
                       started,
                       verbose, tsv):
    """Shows the current agenda. Uses the default calendar unless otherwise specified"""

    cal_names, cal_name_colors = gcalapi.setup_gcal(
        color, lineart, conky, user_locale, calendar, default_calendar)
    gcal = gcalapi.Gcalapi(cal_names=cal_names,
                           cal_name_colors=cal_name_colors)
    gcal.load()

    if start_date is None and end_date is None:
        gcal.cal_query("calw")
    elif start_date is not None and end_date is None:
        gcal.cal_query("calw", start_date)
    elif start_date is not None and end_date is not None:
        gcal.text_query("calw", start_date, end_date)
    else:
        raise click.BadParameter(
            "--start-date should be used alongside --end-date!")


@click.command("calm")
@click.option("--start-date", "-s", default=None,
              help="The starting date to start searching events from")
@click.option("--weeks", "-w", default=1,
              help="The ending date to start searching events to")
@click.option("--cache/--no-cache", default=True,
              help="Execute command without using cache")
@click.option("--calendar", default=[], help="Which calendars to use;" +
                                             "repeat this option to specify a list of values")
@click.option("--client-id", default=None, help="API client_id")
@click.option("--client-secret", default=None, help="API client_secret")
@click.option("--color/--no-color", default=True,
              help="Enabled/Disable all color output")
@click.option("--set-color", nargs=2, default=[], multiple=True,
              callback=validators.validate_set_color)
@click.option("--config-folder", default=None,
              help="Optional directory to load/store all configuration information")
@click.option("--conky/--no-conky", default=False,
              help="Use Conky color codes")
@click.option("--default-calendar", default=[],
              help="Optional default calendar to use if no --calendar options are given; " +
                   "repeat this this option to speciy a list of values")
@click.option("--details", type=click.Choice(["all", "calendar", "location", "length", "reminders",
                                              "description", "longurl", "shorturl", "url", "attendees", "email"]),
              multiple=True,
              help="Which parts to display. Repeat this option to specify a list of values")
@click.option("--include-config/--no-include-config", default=False,
              help="Whether to include ~/.gcalapi.gcalapirc when using --config-folder")
@click.option("--lineart/--no-lineart", default=True,
              help="Enable/Disable line art")
@click.option("--locale", "user_locale", default=None, help="System locale")
@click.option("--military/--no-military",
              default=False, help="Use 24 hour display")
@click.option("--monday/--no-monday", default=False,
              help="Start the week on Monday")
@click.option("--refresh/--no-refresh", default=False,
              help="Delete and refresh cached data")
@click.option("--started/--no-started", default=True,
              help="Show events that have started")
@click.option("--verbose", "-v", default=False, help="Show logs")
@click.option("--tsv/--no-tsv", default=False,
              help="Show output using tab seperated values")
def show_calendar_month(start_date, weeks, cache, calendar, client_id, client_secret, color, set_color,
                        config_folder, conky,
                        default_calendar, details, include_config, lineart, user_locale, military, monday, refresh,
                        started,
                        verbose, tsv):
    """Shows the current agenda. Uses the default calendar unless otherwise specified"""

    cal_names, cal_name_colors = gcalapi.setup_gcal(
        color, lineart, conky, user_locale, calendar, default_calendar)
    gcal = gcalapi.Gcalapi(cal_names=cal_names,
                           cal_name_colors=cal_name_colors)
    gcal.load()

    if start_date is None:
        gcal.cal_query("calm", count=weeks)
    else:
        gcal.cal_query("calm", count=weeks, start_text=start_date)


@click.command("quick")
@click.argument("event-title")
@click.option("--cache/--no-cache", default=True,
              help="Execute command without using cache")
@click.option("--calendar", default=[], multiple=True, help="Which calendars to use;" +
                                                            "repeat this option to specify a list of values")
@click.option("--client-id", default=None, help="API client_id")
@click.option("--client-secret", default=None, help="API client_secret")
@click.option("--color/--no-color", default=True,
              help="Enabled/Disable all color output")
@click.option("--set-color", nargs=2, default=[], multiple=True,
              callback=validators.validate_set_color)
@click.option("--config-folder", default=None,
              help="Optional directory to load/store all configuration information")
@click.option("--conky/--no-conky", default=False,
              help="Use Conky color codes")
@click.option("--default-calendar", default=[],
              help="Optional default calendar to use if no --calendar options are given; " +
                   "repeat this this option to speciy a list of values")
@click.option("--include-config/--no-include-config", default=False,
              help="Whether to include ~/.gcalapi.gcalapirc when using --config-folder")
@click.option("--locale", "user_locale", default=None, help="System locale")
@click.option("--military/--no-military",
              default=False, help="Use 24 hour display")
@click.option("--monday/--no-monday", default=False,
              help="Start the week on Monday")
@click.option("--refresh/--no-refresh", default=False,
              help="Delete and refresh cached data")
@click.option("--started/--no-started", default=True,
              help="Show events that have started")
@click.option("--verbose", "-v", default=False, help="Show logs")
@click.option("--reminder", "-r", multiple=True, callback=validators.validate_reminder, default=False,
              help="Reminders in the form 'TIME METH' or 'TIME'.  TIME " +
                   "is a number which may be followed by an optional " +
                   "'w', 'd', 'h', or 'm' (meaning weeks, days, hours, " +
                   "minutes) and default to minutes.  METH is a string " +
                   "'popup', 'email', or 'sms' and defaults to popup.")
def quick_add_event(event_title, cache, calendar, client_id, client_secret, color, set_color, config_folder, conky,
                    default_calendar, include_config, user_locale, military, monday, refresh, started,
                    verbose, reminder):
    """Shows the current agenda. Uses the default calendar unless otherwise specified"""

    cal_names, cal_name_colors = gcalapi.setup_gcal(
        color, False, conky, user_locale, calendar, default_calendar)
    gcal = gcalapi.Gcalapi(cal_names=calendar,
                           cal_name_colors=cal_name_colors)
    gcal.load()
    gcal.quick_add_event(str(event_title), reminder=reminder)


@click.command("add")
@click.option("--title", default=None, help="The title of the event")
@click.option("--location", default=None, help="The location of the event")
@click.option("--when", default=None, help="When the event is")
@click.option("--duration", default=None,
              help="The duration of the event in minutes or days (if --allday is used)")
@click.option("--allday/--no-allday", default=False,
              help="If the event is all day")
@click.option("--description", default=False,
              help="The description of the event")
@click.option("--prompt/--no-prompt", default=True,
              help="Prompt for missing event data")
@click.option("--who", default=[], multiple=[],
              help="Who is attending the event")
@click.option("--cache/--no-cache", default=True,
              help="Execute command without using cache")
@click.option("--calendar", default=[], multiple=True, help="Which calendars to use;" +
                                                            "repeat this option to specify a list of values")
@click.option("--client-id", default=None, help="API client_id")
@click.option("--client-secret", default=None, help="API client_secret")
@click.option("--color/--no-color", default=True,
              help="Enabled/Disable all color output")
@click.option("--set-color", nargs=2, default=[], multiple=True,
              callback=validators.validate_set_color)
@click.option("--config-folder", default=None,
              help="Optional directory to load/store all configuration information")
@click.option("--conky/--no-conky", default=False,
              help="Use Conky color codes")
@click.option("--default-calendar", default=[],
              help="Optional default calendar to use if no --calendar options are given; " +
                   "repeat this this option to speciy a list of values")
@click.option("--include-config/--no-include-config", default=False,
              help="Whether to include ~/.gcalapi.gcalapirc when using --config-folder")
@click.option("--locale", "user_locale", default=None, help="System locale")
@click.option("--military/--no-military",
              default=False, help="Use 24 hour display")
@click.option("--monday/--no-monday", default=False,
              help="Start the week on Monday")
@click.option("--refresh/--no-refresh", default=False,
              help="Delete and refresh cached data")
@click.option("--started/--no-started", default=True,
              help="Show events that have started")
@click.option("--verbose", "-v", default=False, help="Show logs")
@click.option("--reminder", "-r", multiple=True, callback=validators.validate_reminder, default=False,
              help="Reminders in the form 'TIME METH' or 'TIME'.  TIME " +
                   "is a number which may be followed by an optional " +
                   "'w', 'd', 'h', or 'm' (meaning weeks, days, hours, " +
                   "minutes) and default to minutes.  METH is a string " +
                   "'popup', 'email', or 'sms' and defaults to popup.")
def add_event(title, location, when, duration, allday, description, prompt, who,
              cache, calendar, client_id, client_secret, color, set_color, config_folder, conky,
              default_calendar, include_config, user_locale, military, monday, refresh, started,
              verbose, reminder):
    """Shows the current agenda. Uses the default calendar unless otherwise specified"""

    cal_names, cal_name_colors = gcalapi.setup_gcal(
        color, False, conky, user_locale, calendar, default_calendar)
    gcal = gcalapi.Gcalapi(cal_names=calendar,
                           cal_name_colors=cal_name_colors)
    gcal.load()
    if prompt:
        if title is None:
            utils.print_msg(colors.ClrMag(), "Title: ")
            title = raw_input()
        if location is None:
            utils.print_msg(colors.ClrMag(), "Location: ")
            location = raw_input()
        if when is None:
            utils.print_msg(colors.ClrMag(), "When: ")
            when = raw_input()
        if duration is None:
            if allday:
                utils.print_msg(colors.ClrMag(), "Duration (days): ")
            else:
                utils.print_msg(colors.ClrMag(), "Duration (mins): ")
            duration = raw_input()
        if description is None:
            utils.print_msg((colors.ClrMag(), "Description: "))
            description = raw_input()
        if not reminder:
            reminder = []
            while True:
                utils.print_msg(colors.ClrMag(),
                               "Enter a valid reminder or 'q' to end: ")
                r = raw_input()
                if str(r) == 'q':
                    print("Breaking...")
                    break
                n, m = ParseReminder(str(r))
                reminder.append(str(n) + ' ' + m)

    e_start, e_end = utils.get_time_from_str(when, duration)
    print(duration)
    print(e_start)
    print(e_end)

    gcal.add_event(title, location, e_start, e_end,
                  description, who, reminder)


@click.command("delete")
@click.argument("title")
@click.option("--start-date", "-s", default=None,
              help="The starting date to start deleting events from")
@click.option("--end-date", "-e", default=None,
              help="The ending date to start deleting events to")
@click.option("--force", "-f", default=False,
              help="Force delete events. USE WITH CAUTION")
@click.option("--cache/--no-cache", default=True,
              help="Execute command without using cache")
@click.option("--calendar", default=[], help="Which calendars to use;" +
                                             "repeat this option to specify a list of values")
@click.option("--client-id", default=None, help="API client_id")
@click.option("--client-secret", default=None, help="API client_secret")
@click.option("--color/--no-color", default=True,
              help="Enabled/Disable all color output")
@click.option("--set-color", nargs=2, default=[], multiple=True,
              callback=validators.validate_set_color)
@click.option("--config-folder", default=None,
              help="Optional directory to load/store all configuration information")
@click.option("--conky/--no-conky", default=False,
              help="Use Conky color codes")
@click.option("--default-calendar", default=[],
              help="Optional default calendar to use if no --calendar options are given; " +
                   "repeat this this option to speciy a list of values")
@click.option("--include-config/--no-include-config", default=False,
              help="Whether to include ~/.gcalapi.gcalapirc when using --config-folder")
@click.option("--locale", "user_locale", default=None, help="System locale")
@click.option("--military/--no-military",
              default=False, help="Use 24 hour display")
@click.option("--monday/--no-monday", default=False,
              help="Start the week on Monday")
@click.option("--refresh/--no-refresh", default=False,
              help="Delete and refresh cached data")
@click.option("--started/--no-started", default=True,
              help="Show events that have started")
@click.option("--verbose", "-v", default=False, help="Show logs")
def delete_events(title, start_date, end_date, force, cache, calendar, client_id, client_secret, color, set_color,
                  config_folder, conky,
                  default_calendar, include_config, user_locale, military, monday, refresh, started,
                  verbose):
    """Shows the current agenda. Uses the default calendar unless otherwise specified"""

    cal_names, cal_name_colors = gcalapi.setup_gcal(
        color, False, conky, user_locale, calendar, default_calendar)
    gcal = gcalapi.Gcalapi(cal_names=cal_names,
                           cal_name_colors=cal_name_colors)
    gcal.load()

    e_start = None
    e_end = None

    if start_date is not None:
        e_start = gcal.date_parser.from_string(start_date)
    elif start_date is not None and end_date is not None:
        e_start = gcal.date_parser.from_string(start_date)
        e_end = gcal.date_parser.from_string(end_date)

    gcal.delete_events(str(title), force, e_start, e_end)


@click.command("edit")
@click.argument("title")
@click.option("--cache/--no-cache", default=True,
              help="Execute command without using cache")
@click.option("--calendar", default=[], help="Which calendars to use;" +
                                             "repeat this option to specify a list of values")
@click.option("--client-id", default=None, help="API client_id")
@click.option("--client-secret", default=None, help="API client_secret")
@click.option("--color/--no-color", default=True,
              help="Enabled/Disable all color output")
@click.option("--set-color", nargs=2, default=[], multiple=True,
              callback=validators.validate_set_color)
@click.option("--config-folder", default=None,
              help="Optional directory to load/store all configuration information")
@click.option("--conky/--no-conky", default=False,
              help="Use Conky color codes")
@click.option("--default-calendar", default=[],
              help="Optional default calendar to use if no --calendar options are given; " +
                   "repeat this this option to speciy a list of values")
@click.option("--include-config/--no-include-config", default=False,
              help="Whether to include ~/.gcalapi.gcalapirc when using --config-folder")
@click.option("--locale", "user_locale", default=None, help="System locale")
@click.option("--military/--no-military",
              default=False, help="Use 24 hour display")
@click.option("--monday/--no-monday", default=False,
              help="Start the week on Monday")
@click.option("--refresh/--no-refresh", default=False,
              help="Delete and refresh cached data")
@click.option("--started/--no-started", default=True,
              help="Show events that have started")
@click.option("--verbose", "-v", default=False, help="Show logs")
def edit_events(title, cache, calendar, client_id, client_secret, color, set_color, config_folder, conky,
                default_calendar, include_config, user_locale, military, monday, refresh, started,
                verbose):
    """Shows the current agenda. Uses the default calendar unless otherwise specified"""

    cal_names, cal_name_colors = gcalapi.setup_gcal(
        color, False, conky, user_locale, calendar, default_calendar)
    gcal = gcalapi.Gcalapi(cal_names=cal_names,
                           cal_name_colors=cal_name_colors)
    gcal.load()
    gcal.edit_events(str(title))


@click.command("remind")
@click.option("--minutes", default=None,
              help="Extends the range of events to be notified for")
@click.option("--command", default=None, help="The command to notify with")
@click.option("--use-reminders", default=False, help="Use reminders")
@click.option("--cache/--no-cache", default=True,
              help="Execute command without using cache")
@click.option("--calendar", default=[], help="Which calendars to use;" +
                                             "repeat this option to specify a list of values")
@click.option("--client-id", default=None, help="API client_id")
@click.option("--client-secret", default=None, help="API client_secret")
@click.option("--color/--no-color", default=True,
              help="Enabled/Disable all color output")
@click.option("--set-color", nargs=2, default=[], multiple=True,
              callback=validators.validate_set_color)
@click.option("--config-folder", default=None,
              help="Optional directory to load/store all configuration information")
@click.option("--conky/--no-conky", default=False,
              help="Use Conky color codes")
@click.option("--default-calendar", default=[],
              help="Optional default calendar to use if no --calendar options are given; " +
                   "repeat this this option to speciy a list of values")
@click.option("--include-config/--no-include-config", default=False,
              help="Whether to include ~/.gcalapi.gcalapirc when using --config-folder")
@click.option("--locale", "user_locale", default=None, help="System locale")
@click.option("--military/--no-military",
              default=False, help="Use 24 hour display")
@click.option("--monday/--no-monday", default=False,
              help="Start the week on Monday")
@click.option("--refresh/--no-refresh", default=False,
              help="Delete and refresh cached data")
@click.option("--started/--no-started", default=True,
              help="Show events that have started")
@click.option("--verbose", "-v", default=False, help="Show logs")
def remind_events(minutes, command, use_reminders, cache, calendar, client_id, client_secret, color, set_color,
                  config_folder, conky,
                  default_calendar, include_config, user_locale, military, monday, refresh, started,
                  verbose):
    """Shows the current agenda. Uses the default calendar unless otherwise specified"""

    cal_names, cal_name_colors = gcalapi.setup_gcal(
        color, False, conky, user_locale, calendar, default_calendar)
    gcal = gcalapi.Gcalapi(cal_names=cal_names,
                           cal_name_colors=cal_name_colors)
    gcal.load()
    if minutes is not None and command is not None:
        gcal.remind(int(minutes), command, use_reminders=use_reminders)
    elif minutes is not None:
        gcal.remind(int(minutes), use_reminders=use_reminders)
    else:
        gcal.remind(use_reminders=use_reminders)


@click.command("import")
@click.argument("path")
@click.option("--dump", default=False, help="Dump events to screen")
@click.option("--cache/--no-cache", default=True,
              help="Execute command without using cache")
@click.option("--calendar", default=[], help="Which calendars to use;" +
                                             "repeat this option to specify a list of values")
@click.option("--client-id", default=None, help="API client_id")
@click.option("--client-secret", default=None, help="API client_secret")
@click.option("--color/--no-color", default=True,
              help="Enabled/Disable all color output")
@click.option("--set-color", nargs=2, default=[], multiple=True,
              callback=validators.validate_set_color)
@click.option("--config-folder", default=None,
              help="Optional directory to load/store all configuration information")
@click.option("--conky/--no-conky", default=False,
              help="Use Conky color codes")
@click.option("--default-calendar", default=[],
              help="Optional default calendar to use if no --calendar options are given; " +
                   "repeat this this option to speciy a list of values")
@click.option("--include-config/--no-include-config", default=False,
              help="Whether to include ~/.gcalapi.gcalapirc when using --config-folder")
@click.option("--locale", "user_locale", default=None, help="System locale")
@click.option("--military/--no-military",
              default=False, help="Use 24 hour display")
@click.option("--monday/--no-monday", default=False,
              help="Start the week on Monday")
@click.option("--refresh/--no-refresh", default=False,
              help="Delete and refresh cached data")
@click.option("--started/--no-started", default=True,
              help="Show events that have started")
@click.option("--verbose", "-v", default=False, help="Show logs")
@click.option("--reminder", "-r", multiple=True, callback=validators.validate_reminder, default=False,
              help="Reminders in the form 'TIME METH' or 'TIME'.  TIME " +
                   "is a number which may be followed by an optional " +
                   "'w', 'd', 'h', or 'm' (meaning weeks, days, hours, " +
                   "minutes) and default to minutes.  METH is a string " +
                   "'popup', 'email', or 'sms' and defaults to popup.")
def import_ics(path, dump, cache, calendar, client_id, client_secret, color, set_color,
               config_folder, conky,
               default_calendar, include_config, user_locale, military, monday, refresh, started,
               verbose, reminder):
    """Shows the current agenda. Uses the default calendar unless otherwise specified"""

    cal_names, cal_name_colors = gcalapi.setup_gcal(
        color, False, conky, user_locale, calendar, default_calendar)
    gcal = gcalapi.Gcalapi(cal_names=cal_names,
                           cal_name_colors=cal_name_colors)
    gcal.load()
    gcal.ImportICS(verbose=verbose, dump=dump, ics_file=path, reminder=reminder)


@click.group()
def gcal():
    """Commands to interact with a Google Calendar"""
    pass


gcal.add_command(show_agenda)  # agenda
gcal.add_command(list_calendars)  # cal
gcal.add_command(search_events)  # events
gcal.add_command(show_calendar_week)  # cal
gcal.add_command(show_calendar_month)  # cal
gcal.add_command(quick_add_event)  # events
gcal.add_command(add_event)  # events
gcal.add_command(delete_events)  # events
gcal.add_command(edit_events)  # events
gcal.add_command(remind_events)  # remind

if __name__ == '__main__':
    signal.signal(signal.SIGINT, utils.sigint_handler)
    gcal()
