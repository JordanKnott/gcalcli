class CLR:
    useColor = True
    conky = False

    def __str__(self):
        return self.color if self.useColor else ""


class CLR_NRM(CLR):
    color = "\033[0m"


class CLR_BLK(CLR):
    color = "\033[0;30m"


class CLR_BRBLK(CLR):
    color = "\033[30;1m"


class CLR_RED(CLR):
    color = "\033[0;31m"


class CLR_BRRED(CLR):
    color = "\033[31;1m"


class CLR_GRN(CLR):
    color = "\033[0;32m"


class CLR_BRGRN(CLR):
    color = "\033[32;1m"


class CLR_YLW(CLR):
    color = "\033[0;33m"


class CLR_BRYLW(CLR):
    color = "\033[33;1m"


class CLR_BLU(CLR):
    color = "\033[0;34m"


class CLR_BRBLU(CLR):
    color = "\033[34;1m"


class CLR_MAG(CLR):
    color = "\033[0;35m"


class CLR_BRMAG(CLR):
    color = "\033[35;1m"


class CLR_CYN(CLR):
    color = "\033[0;36m"


class CLR_BRCYN(CLR):
    color = "\033[36;1m"


class CLR_WHT(CLR):
    color = "\033[0;37m"


class CLR_BRWHT(CLR):
    color = "\033[37;1m"


def SetConkyColors():
    # XXX these colors should be configurable
    CLR.conky = True
    CLR_NRM.color = ""
    CLR_BLK.color = "${color black}"
    CLR_BRBLK.color = "${color black}"
    CLR_RED.color = "${color red}"
    CLR_BRRED.color = "${color red}"
    CLR_GRN.color = "${color green}"
    CLR_BRGRN.color = "${color green}"
    CLR_YLW.color = "${color yellow}"
    CLR_BRYLW.color = "${color yellow}"
    CLR_BLU.color = "${color blue}"
    CLR_BRBLU.color = "${color blue}"
    CLR_MAG.color = "${color magenta}"
    CLR_BRMAG.color = "${color magenta}"
    CLR_CYN.color = "${color cyan}"
    CLR_BRCYN.color = "${color cyan}"
    CLR_WHT.color = "${color white}"
    CLR_BRWHT.color = "${color white}"


def GetColor(value):
    c = {'default': CLR_NRM(),
              'black': CLR_BLK(),
              'brightblack': CLR_BRBLK(),
              'red': CLR_RED(),
              'brightred': CLR_BRRED(),
              'green': CLR_GRN(),
              'brightgreen': CLR_BRGRN(),
              'yellow': CLR_YLW(),
              'brightyellow': CLR_BRYLW(),
              'blue': CLR_BLU(),
              'brightblue': CLR_BRBLU(),
              'magenta': CLR_MAG(),
              'brightmagenta': CLR_BRMAG(),
              'cyan': CLR_CYN(),
              'brightcyan': CLR_BRCYN(),
              'white': CLR_WHT(),
              'brightwhite': CLR_BRWHT(),
              None: CLR_NRM()}

    if value in c:
        return c[value]
    else:
        return None


def GetCalColors(calNames):
    calColors = {}
    for calName in calNames:
        calNameParts = calName.split("#")
        calNameSimple = calNameParts[0]
        calColor = calColors.get(calNameSimple)
        if len(calNameParts) > 0:
            calColorRaw = calNameParts[-1]
            calColorNew = GetColor(calColorRaw)
            if calColorNew is not None:
                calColor = calColorNew
        calColors[calNameSimple] = calColor
    return calColors