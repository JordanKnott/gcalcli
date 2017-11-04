class ART:
    use_art = True
    fancy = ''
    plain = ''

    def __str__(self):
        return self.fancy if self.use_art else self.plain


class ArtHrz(ART):
    fancy = '\033(0\x71\033(B'
    plain = '-'


class ArtVrt(ART):
    fancy = '\033(0\x78\033(B'
    plain = '|'


class ArtLrc(ART):
    fancy = '\033(0\x6A\033(B'
    plain = '+'


class ArtUrc(ART):
    fancy = '\033(0\x6B\033(B'
    plain = '+'


class ArtUlc(ART):
    fancy = '\033(0\x6C\033(B'
    plain = '+'


class ArtLlc(ART):
    fancy = '\033(0\x6D\033(B'
    plain = '+'


class ArtCrs(ART):
    fancy = '\033(0\x6E\033(B'
    plain = '+'


class ArtLte(ART):
    fancy = '\033(0\x74\033(B'
    plain = '+'


class ArtRte(ART):
    fancy = '\033(0\x75\033(B'
    plain = '+'


class ArtBte(ART):
    fancy = '\033(0\x76\033(B'
    plain = '+'


class ArtUte(ART):
    fancy = '\033(0\x77\033(B'
    plain = '+'
