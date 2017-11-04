gcalcli3
=======

#### Google Calendar Command Line Interface

gcalcli3 is a fork of the orignal version, found at [insanum/gcalcli](https://github.com/insanum/gcalcli).
This version has been refactored to support Python, create a cleaner interface, and clean up the code.

__Be warned, not backwards compatible with many options!__

Currently this a list of the differences between the original and this fork:

* Works on Python 3+
* Source code is PEP-8 compliant
* Uses click instead of argparse or gflags
* Fuzzy date parsing is default enabled behavior (no more optional package)
* Source code is split across multiple files instead of one massive one
* Removed configFolder support
* Remove flag file support. Instead supports INI style configuration

As for what gcalcli3 does, this is the description given from the original application

> gcalcli is a Python application that allows you to access your Google
> Calendar(s) from a command line. It's easy to get your agenda, search for
> events, add new events, delete events, edit events, and even import those
> annoying ICS/vCal invites from Microsoft Exchange and/or other sources.
> Additionally, gcalcli can be used as a reminder service and execute any
> application you want when an event is coming up.


gcalcli3 uses the [Google Calendar API version 3](https://developers.google.com/google-apps/calendar/).

Requirements
------------

* [Python](http://www.python.org) (2.6+, 3+)
* [dateutil](http://www.labix.org/python-dateutil)
* [Google API Client](https://developers.google.com/api-client-library/python)
* [httplib2](https://github.com/httplib2/httplib2)
* [oauth2client](https://github.com/google/oauth2client)
* [click]()
* A love for the command line (that borders on obsessive)!

### Optional packages

* [vobject](http://vobject.skyhouseconsulting.com) Python module  
  Used for ics/vcal importing.


Installation
------------

### Install from source

```sh
git clone https://github.com/insanum/gcalcli.git
cd gcalcli3
python setup.py install
```

### Install optional packages

```sh
pip install vobject
```

Features
--------

 * OAuth2 authention with your Google account
 * list your calendars
 * show an agenda using a specified start/end date and time
 * ascii text graphical calendar display with variable width
 * search for past and/or future events
 * "quick add" new events to a specified calendar
 * "add" a new event to a specified calendar (interactively or automatically)
 * "delete" event(s) from a calendar(s) (interactively or automatically)
 * "edit" event(s) interactively
 * import events from ICS/vCal files to a specified calendar
 * support for URL shortening via goo.gl
 * easy integration with your favorite mail client (attachment handler)
 * run as a cron job and execute a command for reminders
 * work against specific calendars (by calendar name w/ regex)
 * colored output and unicode character support
 * super fun hacking with shell scripts, cron, screen, tmux, conky, etc


Roadmap
-------

__Below is a roadmap of all future planned features__

* Curses like interface for better event viewing/editing
* Support multiple accounts
* Saner defaults

Screenshots
-----------

TODO

HowTo
-----

#### Usage

TODO

#### Login Information

OAuth2 is used for authenticating with your Google account. The resulting token
is placed in the ~/.gcalcli_oauth file. When you first start gcalcli the
authentication process will proceed. Simply follow the instructions.

If desired, you can use your own Calendar API instead of the default API values.
*NOTE*: these steps are optional!

* Go to the [Google developer console](https://console.developers.google.com/)
* Make a new project for gcalcli3
* On the sidebar under APIs & Auth, click APIs
* Enable the Calendar API
* On the sidebar click Credentials
* Create a new Client ID. Set the type to Installed Application and the subtype
  to Other. You will be asked to fill in some consent form information, but what
  you put here isn't important. It's just what will show up when gcalcli opens
  up the OAuth website. Anything optional can safely be left blank.
* Go back to the credentials page and grab your ID and Secret.
* If desired, add the client_id and client_secret to your .gcalclirc:

        --client_id=xxxxxxxxxxxxxxx.apps.googleusercontent.com
        --client_secret=xxxxxxxxxxxxxxxxx

* Remove your existing OAuth information (typically ~/.gcalcli_oauth).
* Run gcalcli with any desired argument, making sure the new client_id and
  client_secret are passed on the command line or placed in your .gcalclirc. The
  OAuth authorization page should be opened automatically in your default
  browser.

#### HTTP Proxy Support

gcalcli will automatically work with an HTTP Proxy simply by setting up some
environment variables used by the gdata Python module:

```
http_proxy
https_proxy
proxy-username or proxy_username
proxy-password or proxy_password
```

Note that these environment variables must be lowercase.

#### Configuration File

TODO

#### Importing VCS/VCAL/ICS Files from Exchange (or other)

Importing events from files is easy with gcalcli. The 'import' command accepts
a filename on the command line or can read from standard input. Here is a script
that can be used as an attachment handler for Thunderbird or in a mailcap entry
with Mutt (or in Mutt you could just use the attachment viewer and pipe command):

```
#!/bin/bash

TERMINAL=evilvte
CONFIG=~/.gcalclirc

$TERMINAL -e bash -c "echo 'Importing invite...' ; \
                      gcalcli --detail-url=short \
                              --calendar='Eric Davis' \
                              import -v \"$1\" ; \
                      read -p 'press enter to exit: '"
```

Note that with Thunderbird you'll have to have the 'Show All Body Parts'
extension installed for seeing the calendar attachments when not using
'Lightning'. See this
[bug report](https://bugzilla.mozilla.org/show_bug.cgi?id=505024)
for more details.

#### Event Popup Reminders

The 'remind' command for gcalcli is used to execute any command as an event
notification. This can be a notify-send or an xmessage-like popup or whatever
else you can think of. gcalcli does not contain a daemon so you'll have to use
some other tool to ensure gcalcli is run in a timely manner for notifications.
Two options are using cron or a loop inside a shell script.

Cron:
```
% crontab -l
*/10 * * * * /usr/bin/gcalcli remind
```

Shell script like your .xinitrc so notifications only occur when you're logged
in via X:
```
#!/bin/bash

[[ -x /usr/bin/dunst ]] && /usr/bin/dunst -config ~/.dunstrc &

if [ -x /usr/bin/gcalcli ]; then
  while true; do
    /usr/bin/gcalcli --calendar="davis" remind
    sleep 300
  done &
fi

exec herbstluftwm # :-)
```

By default gcalcli executes the notify-send command for notifications. Most
common Linux desktop enviroments already contain a DBUS notification daemon
that supports libnotify so it should automagically just work. If you're like
me and use nothing that is common I highly recommend the
[dunst](https://github.com/knopwob/dunst) dmenu'ish notification daemon.

#### Agenda On Your Root Desktop

Put your agenda on your desktop using Conky. The '--conky' option causes
gcalcli to output Conky color sequences. Note that you need to use the Conky
'execpi' command for the gcalcli output to be parsed for color sequences. Add
the following to your .conkyrc:

```
${execpi 300 gcalcli --conky agenda}
```

To also get a graphical calendar that shows the next three weeks add:

```
${execpi 300 gcalcli --conky calw 3}
```

You may need to increase the `text_buffer_size` in your conkyrc file.  Users
have reported that the default of 256 bytes is too small for busy calendars.

#### Agenda Integration With tmux

Put your next event in the left of your 'tmux' status line.  Add the following
to your tmux.conf file:

```
set-option -g status-interval 60
set-option -g status-left "#[fg=blue,bright]#(gcalcli agenda | head -2 | tail -1)#[default]"
```

#### Agenda Integration With screen

Put your next event in your 'screen' hardstatus line.  First add a cron job
that will dump you agenda to a text file:

```
% crontab -e
```

Then add the following line:

```
*/5 * * * * gcalcli --nocolor --nostarted agenda "`date`" > /tmp/gcalcli_agenda.txt
```

Next create a simple shell script that will extract the first agenda line.
Let's call this script 'screen_agenda':

```
#!/bin/bash
head -2 /tmp/gcalcli_agenda.txt | tail -1
```

Next configure screen's hardstatus line to gather data from a backtick command.
Of course your hardstatus line is most likely very different than this (Mine
is!):

```
backtick 1 60 60 screen_agenda
hardstatus "[ %1` ]"
```
