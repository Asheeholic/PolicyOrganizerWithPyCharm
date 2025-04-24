# External import
from openpyxl.styles import Alignment, Font, PatternFill

# Local import
from applications.analyzeBppllistTxt.styleTools import dataStyling
from applications.analyzeBppllistTxt.styleTools import titleStyling
from applications.analyzeBppllistTxt.styleTools import titleFunctions

def execute(ws, row_num, width_rate, font_size, font_family):

    # Added for Network Directory Backup ## 2025.04.24 
    li = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N']

    dataStyling.data_styling(
        ws, row_num, li, width_rate, font_size, font_family
        )
    dataStyling.data_merge_with_empty(ws, row_num, li)
    titleStyling.title_styling(ws, li, font_size, font_family)
    titleFunctions.title_filter(ws)
    titleFunctions.title_freeze_panes(ws, 'E2')

