from enum import Enum

class SIG_QUALITY(Enum):
    POOR = 0
    ACCEPTABLE = 5
    GOOD = 7
    EXCELLENT = 10


class SIG_QUALITY_COLOR():
    POOR = {'r': 0.8941176, 'g': 0.10196, 'b': 0.1098}
    ACCEPTABLE = {'r': 0.96862745098, 'g': 0.59607843137, 'b': 0.11372549019}
    GOOD = {'r': 0.4, 'g': 1, 'b': 0}