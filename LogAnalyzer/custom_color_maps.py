import common
from enums import SIG_QUALITY

ordered_bs_s = [76, 219, 198, 192, 171, 31] # BSs in decreasing order of connection duration
ordered_bs_s.reverse()

bs_colors = common.generate_discrete_color_map(ordered_bs_s)
other_color = "#A6CEE3"

# key = PCI
bs_colors = {76:"#E41A1C", 219: "#377EB8", 198: "#4DAF4A", 192: "#984EA3", 171:"#FF7F00", 31: "#A65628"}

# first key = RSRQ quality, second key = RSRP quality
sig_qual_indices = {SIG_QUALITY.POOR:{SIG_QUALITY.POOR:0, SIG_QUALITY.ACCEPTABLE:1, SIG_QUALITY.GOOD:2},
                   SIG_QUALITY.ACCEPTABLE:{SIG_QUALITY.POOR:3, SIG_QUALITY.ACCEPTABLE:4, SIG_QUALITY.GOOD:5},
                   SIG_QUALITY.GOOD:{SIG_QUALITY.POOR:6, SIG_QUALITY.ACCEPTABLE:7, SIG_QUALITY.GOOD:8}}

sig_qual_colors = [{'r': 0.8941176, 'g': 0.10196, 'b': 0.1098},
                   {'r': 0.0, 'g': 1, 'b': 0},
                   {'r': 0, 'g': 0, 'b': 1.0}]

def get_bs_color(id):
    if id in bs_colors:
        color = bs_colors[id]
    else:
        color = other_color
    return color

def get_sig_qual_color(rsrp_qual, rsrq_qual):
    color = None
    if rsrq_qual == SIG_QUALITY.POOR or rsrp_qual == SIG_QUALITY.POOR:
        color = sig_qual_colors[2]
    elif rsrq_qual == SIG_QUALITY.ACCEPTABLE and rsrp_qual == SIG_QUALITY.ACCEPTABLE:
        color = sig_qual_colors[1]
    else:
        color = sig_qual_colors[0]
    return color

