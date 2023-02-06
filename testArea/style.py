# External import
from openpyxl.styles import Alignment, Font, PatternFill

# Local import

def execute(ws, total_policy_number, width_rate):
    # 넓이 비율

    # 셀 높이
    ws.row_dimensions[2].height = 30
    li = ['B','C','D','E','F','G','H','I','J','K','L','M','N','O','P']


    # 모든 행에 적용
    for i in li :
        width = 0
        for j in range(3, total_policy_number + 3) :
            ws[i + str(j)].alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)

            # 제일 큰 행을 기준으로 넣기
            for k in str(ws[i + str(j)].value).split('\n') :
                if width < len(k) :
                    width = len(k)

        # 넓이 고정
        ws.column_dimensions[i].width = (width * width_rate) + 3


    # 타이틀 만들기
    for i in range(0, len(li)) :
        li[i] = li[i] + "2"

    # 타이틀 꾸미기
    for item in li :
        ws[item].alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        ws[item].font = Font(size=11, bold=True)
        ws[item].fill = PatternFill(start_color = '00ff00', end_color = '00ff00', patternType='solid')

