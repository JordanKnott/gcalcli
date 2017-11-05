from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen

"""A asciimatics based TUI for interacting with a Google calendar. Currently only supports week view."""


def chunkstring(string, length):
    """Splits a string into equal parts based on the given length"""
    return (string[0 + i:length + i] for i in range(0, len(string), length))


def generate_key_list():
    """Returns a list of keycodes for all letters and numbers"""
    letters = [
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k',
        'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v',
        'w', 'x', 'y', 'z'
    ]
    key_codes = []
    for letter in letters:
        key_codes.append(ord(letter))
        key_codes.append(ord(letter.upper()))
    for number in range(0, 10):
        key_codes.append(ord(str(number)))
    return key_codes


def is_alphanumeric_key(key_code):
    """Returns true if the given keycode is a letter or a number. False otherwise"""
    return key_code in generate_key_list()


def get_color(color):
    colors = {
        "magenta": Screen.COLOUR_MAGENTA,
        "black": Screen.COLOUR_BLACK,
        "blue": Screen.COLOUR_BLUE,
        "green": Screen.COLOUR_GREEN,
        "yellow": Screen.COLOUR_YELLOW,
        "red": Screen.COLOUR_RED,
        "cyan": Screen.COLOUR_CYAN,
        "white": Screen.COLOUR_WHITE
    }
    return colors[color]


def write_event(screen, event, col_width, x, event_y_pos, is_highlighted=False):
    if len(event['summary']) > col_width:
        e_chunks = chunkstring(event['summary'], int(col_width - 2))
        for e_chunk in e_chunks:
            if is_highlighted:
                screen.print_at(e_chunk, int(x + 2), event_y_pos, bg=Screen.COLOUR_CYAN)
            else:
                screen.print_at(e_chunk, int(x + 2), event_y_pos)
            event_y_pos += 1
    else:
        if is_highlighted:
            screen.print_at(event['summary'], x + 2, event_y_pos, bg=Screen.COLOUR_CYAN)
        else:
            screen.print_at(event['summary'], x + 2, event_y_pos)
        event_y_pos += 1
    event_y_pos += 1
    return event_y_pos


def demo(screen: Screen):
    current_event = {"x": 0, "y": 0, "summary": "10:30 am - LCD SM Post", "color": "magenta"}
    current_day = ""

    events = {
        "Monday": [
            {
                "summary": "10:30 am - LCD SM Post", "color": "magenta"
            }, {
                "summary": "11:00am - DD Blog Post", "color": "magenta"
            }, {
                "summary": "1:00pm - DD SM POST", "color": "magenta"
            }, {
                "summary": "2:00pm - Weekly Meeting", "color": "green"
            }
        ],
        "Tuesday": [
            {
                "summary": "All Day - PHILIPPINES OFFICES CLOSED", "color": "green"
            }, {
                "summary": "All Day - ORDER THANKSGIVING CARDS", "color": "green"
            }, {
                "summary": "All Day - Halloween", "color": "magenta"
            }, {
                "summary": "10:00am - ROUND TABLE", "color": "green"
            }, {
                "summary": "10:30am - DM/JF/JM Marketing Meeting", "color": "green"
            }, {
                "summary": "10:30 am - LCD SM Post", "color": "magenta"
            }, {
                "summary": "11:00am - DD Blog Post", "color": "magenta"
            }, {
                "summary": "1:00pm - DD SM POST", "color": "magenta"
            }, {
                "summary": "2:00pm - Meeting with consultant Mike Powell", "color": "green"
            }
        ]
    }

    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

    dates = ["Oct 29", "30 Oct", "31 Oct", "01 Nov", "02 Nov", "03 Nov", "04 Nov"]

    first_event = True
    event_dialog_focused = False
    current_text_buffer = ""
    current_selected_field = None
    selectable_fields = {
        "title": {
            "x": 0,
            "y": 0,
            "contents": ""
        },
        "when": {
            "x": 0,
            "y": 0,
            "contents": ""
        }
    }
    while True:
        col_width = screen.width / 7
        points = []
        for i in range(0, 8):
            x = int(i * col_width)
            for y in range(1, screen.height):
                screen.print_at("|", x, y)
            if i != 7:
                screen.print_at(days[i], x + int(col_width / 2) - int(len(days[i]) / 2), 1)
                screen.print_at(dates[i], x + int(col_width / 2) - int(len(dates[i]) / 2), 3)
                event_y_pos = 5
                if days[i] in events:
                    for event in events[days[i]]:
                        event['x'] = x
                        event['y'] = event_y_pos
                        if first_event:
                            first_event = False
                            current_event = event
                            current_day = days[i]
                        event_y_pos = write_event(screen, event, col_width, x, event_y_pos)

        screen.print_at("-" * screen.width, 0, 0)
        screen.print_at("-" * screen.width, 0, 2)

        ke = screen.get_event()
        if ke is not None and isinstance(ke, KeyboardEvent):
            screen.print_at(str(ke.key_code), int(screen.width / 2), int(screen.height / 2))
            if not event_dialog_focused:
                if ke.key_code == ord('q'):
                    return
                elif ke.key_code == Screen.KEY_DOWN:
                    index = events[current_day].index(current_event)
                    if index + 1 != len(events[current_day]):
                        current_event = events[current_day][index + 1]
                elif ke.key_code == Screen.KEY_UP:
                    index = events[current_day].index(current_event)
                    if index - 1 != -1:
                        current_event = events[current_day][index - 1]
                elif ke.key_code == Screen.KEY_RIGHT:
                    index = days.index(current_day) + 1
                    if index != len(days):
                        if days[index] in events:
                            current_day = days[index]
                            current_event = events[current_day][0]
                elif ke.key_code == Screen.KEY_LEFT:
                    index = days.index(current_day) - 1
                    if index != -1:
                        if days[index] in events:
                            current_day = days[index]
                            current_event = events[current_day][0]
            if ke.key_code == 10:
                if event_dialog_focused:
                    event_dialog_focused = False
                    current_event['summary'] = current_event['summary'].split('-')[
                                                   0].strip() + " - " + current_text_buffer
                    screen.clear()
                else:
                    event_dialog_focused = True
                    current_text_buffer = current_event['summary'].split("-")[1].strip()
        if event_dialog_focused:
            if ke is not None and isinstance(ke, KeyboardEvent):
                if is_alphanumeric_key(ke.key_code):
                    current_text_buffer += chr(ke.key_code)
                elif ke.key_code == Screen.KEY_BACK:
                    current_text_buffer = current_text_buffer[:-1]
                elif ke.key_code == Screen.KEY_TAB:
                    current_event['summary'] = current_event['summary'].split('-')[
                                                   0].strip() + " - " + current_text_buffer

        write_event(screen, current_event, col_width, int(current_event['x']), current_event['y'], True)

        screen.move(0, screen.height - 10)
        screen.draw(screen.width, screen.height - 10, char='-')
        for y in range(0, 10):
            screen.move(0, screen.height - y)
            screen.draw(screen.width, screen.height - y, char=' ')

        screen.print_at("Title: ", 0 + 5, screen.height - 8)
        selectable_fields['title']['x'] = 0 + 5
        selectable_fields['title']['y'] = screen.height - 8

        screen.print_at("When: ", 0 + 5, screen.height - 7)
        selectable_fields['when']['x'] = 0 + 5
        selectable_fields['when']['y'] = screen.height - 7

        screen.print_at("Location: ", 0 + 5, screen.height - 6)
        screen.print_at("Attendees: ", 0 + 5, screen.height - 5)

        if event_dialog_focused:
            # screen.print_at(current_event['summary'].split('-')[1].strip(), 0 + 5 + len("Title: "), screen.height - 8)
            # screen.print_at(current_event['summary'].split('-')[0].strip(), 0 + 5 + len("When: "), screen.height - 7)
            screen.print_at(current_text_buffer, selectable_fields['title']['x'] + len("Title: "),
                            selectable_fields['title']['y'],
                            bg=Screen.COLOUR_CYAN)
        else:
            screen.print_at(current_event['summary'].split('-')[1].strip(), 0 + 5 + len("Title: "), screen.height - 8)
            screen.print_at(current_event['summary'].split('-')[0].strip(), 0 + 5 + len("When: "), screen.height - 7)

        screen.refresh()


Screen.wrapper(demo)
