# External import
from openpyxl.styles import Alignment, Font, PatternFill

# Local import
from styleTools import dataStyling
from styleTools import titleStyling
from styleTools import titleFunctions

def execute(ws, row_num, width_rate):

    li = ['A','B','C','D','E','F','G','H','I','J','K','L','M']

    dataStyling.data_styling(ws, row_num, li, width_rate)
    dataStyling.data_merge_with_empty(ws, row_num, li)
    titleStyling.title_styling(ws, li)
    titleFunctions.title_filter(ws)
    titleFunctions.title_freeze_panes(ws, 'E2')

