class ART:
    useArt = True
    fancy = ''
    plain = ''

    def __str__(self):
        return self.fancy if self.useArt else self.plain


class ART_HRZ(ART):
    fancy = '\033(0\x71\033(B'
    plain = '-'


class ART_VRT(ART):
    fancy = '\033(0\x78\033(B'
    plain = '|'


class ART_LRC(ART):
    fancy = '\033(0\x6A\033(B'
    plain = '+'


class ART_URC(ART):
    fancy = '\033(0\x6B\033(B'
    plain = '+'


class ART_ULC(ART):
    fancy = '\033(0\x6C\033(B'
    plain = '+'


class ART_LLC(ART):
    fancy = '\033(0\x6D\033(B'
    plain = '+'


class ART_CRS(ART):
    fancy = '\033(0\x6E\033(B'
    plain = '+'


class ART_LTE(ART):
    fancy = '\033(0\x74\033(B'
    plain = '+'


class ART_RTE(ART):
    fancy = '\033(0\x75\033(B'
    plain = '+'


class ART_BTE(ART):
    fancy = '\033(0\x76\033(B'
    plain = '+'


class ART_UTE(ART):
    fancy = '\033(0\x77\033(B'
    plain = '+'