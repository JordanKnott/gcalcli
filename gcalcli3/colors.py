class CLR:
    use_color = True
    conky = False

    def __str__(self):
        return self.color if self.use_color else ""


class ClrNrm(CLR):
    color = "\033[0m"


class ClrBlk(CLR):
    color = "\033[0;30m"


class ClrBrblk(CLR):
    color = "\033[30;1m"


class ClrRed(CLR):
    color = "\033[0;31m"


class ClrBrred(CLR):
    color = "\033[31;1m"


class ClrGrn(CLR):
    color = "\033[0;32m"


class ClrBrgrn(CLR):
    color = "\033[32;1m"


class ClrYlw(CLR):
    color = "\033[0;33m"


class ClrBrylw(CLR):
    color = "\033[33;1m"


class ClrBlu(CLR):
    color = "\033[0;34m"


class ClrBrblu(CLR):
    color = "\033[34;1m"


class ClrMag(CLR):
    color = "\033[0;35m"


class ClrBrmag(CLR):
    color = "\033[35;1m"


class ClrCyn(CLR):
    color = "\033[0;36m"


class ClrBrcyn(CLR):
    color = "\033[36;1m"


class ClrWht(CLR):
    color = "\033[0;37m"


class ClrBrwht(CLR):
    color = "\033[37;1m"


def set_conky_colors():
    # XXX these colors should be configurable
    CLR.conky = True
    ClrNrm.color = ""
    ClrBlk.color = "${color black}"
    ClrBrblk.color = "${color black}"
    ClrRed.color = "${color red}"
    ClrBrred.color = "${color red}"
    ClrGrn.color = "${color green}"
    ClrBrgrn.color = "${color green}"
    ClrYlw.color = "${color yellow}"
    ClrBrylw.color = "${color yellow}"
    ClrBlu.color = "${color blue}"
    ClrBrblu.color = "${color blue}"
    ClrMag.color = "${color magenta}"
    ClrBrmag.color = "${color magenta}"
    ClrCyn.color = "${color cyan}"
    ClrBrcyn.color = "${color cyan}"
    ClrWht.color = "${color white}"
    ClrBrwht.color = "${color white}"


def get_color(value):
    c = {'default': ClrNrm(),
         'black': ClrBlk(),
         'brightblack': ClrBrblk(),
         'red': ClrRed(),
         'brightred': ClrBrred(),
         'green': ClrGrn(),
         'brightgreen': ClrBrgrn(),
         'yellow': ClrYlw(),
         'brightyellow': ClrBrylw(),
         'blue': ClrBlu(),
         'brightblue': ClrBrblu(),
         'magenta': ClrMag(),
         'brightmagenta': ClrBrmag(),
         'cyan': ClrCyn(),
         'brightcyan': ClrBrcyn(),
         'white': ClrWht(),
         'brightwhite': ClrBrwht(),
         None: ClrNrm()}

    if value in c:
        return c[value]
    else:
        return None


def get_cal_colors(cal_names):
    cal_colors = {}
    for cal_name in cal_names:
        cal_name_parts = cal_name.split("#")
        cal_name_simple = cal_name_parts[0]
        cal_color = cal_colors.get(cal_name_simple)
        if len(cal_name_parts) > 0:
            cal_color_raw = cal_name_parts[-1]
            cal_color_new = get_color(cal_color_raw)
            if cal_color_new is not None:
                cal_color = cal_color_new
        cal_colors[cal_name_simple] = cal_color
    return cal_colors
