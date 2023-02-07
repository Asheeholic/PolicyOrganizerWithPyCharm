# 20221111 nutanix update, windows update

# External import
from openpyxl.styles import Alignment

# Local import
from analyzeTools import scheduleTools

# 정의 함수
def execute(sheet_name, ws, lines):

    # 시트 이름 (왼쪽 하단 이름)
    ws.title = sheet_name

    # 엑셀 스타일을 위한 정책 개수 리턴하기
    total_policy_num = 0

    # 배열 선언
    rows = 0
    cols = 0
    cols_temp = 0

    for line in lines :
        line = line.strip()
        if '---------------------------------------------------------' in line :
            rows += 1
            cols_temp = 0

        cols_temp += 1
        if cols <= cols_temp :
            cols = cols_temp

    analyze_txt_lines = [["HANJAEHO" for a in range(cols)] for b in range(rows + 1)]

    line_i = 0
    line_j = 0


    # 2차원 배열 집어넣기
    for line in lines :
        line = line.strip()
        analyze_txt_lines[line_i][line_j] = line

        line_j += 1
        if line == '------------------------------------------------------------' :
            line_i += 1
            line_j = 0


    ### 엑셀에 집어 넣기

    # 1. 열 별 제목 만들기
    column_titles = [
        '정책명', '정책 유형', '사용', '스토리지 유닛', '볼륨 풀',
        '엑셀러레이터 사용', '하드웨어', 'OS',
        '클라이언트 명', '백업 경로',
        '스케줄 이름', '스케줄 유형',
        '캘린더 날짜', '백업보관일', '윈도우 시간'
    ]
    title_name_i = 0
    for title_name in column_titles :
        ws.cell(column=(2+title_name_i), row=2, value=title_name)
        title_name_i += 1

    # 2. 정책 별 정보 넣기

    # 정책 번호

    # print(analyze_txt_lines[3])
    ## 들어가면 안되는 문자들
    not_in_the_list = [
        'HANJAEHO',
        'No specific exclude dates entered',
        'No exclude days of week entered',
        'Excluded Dates----------',
        '',
        '------------------------------------------------------------'
    ]

    for policy_num in range(1, len(analyze_txt_lines)):

        datas = []

        # for include
        include_in_boolean = False

        for line_num in range(0, len(analyze_txt_lines[policy_num])):

            # 짧게 요약
            analyzed_txt = analyze_txt_lines[policy_num][line_num]
            data = {}

            # 공란 및 쓸데없는 문자 제외하고 시작하기
            if analyzed_txt in not_in_the_list:
                continue
            if 'Schedule:' in analyzed_txt:
                include_in_boolean = False

            ## include 관련 예외 처리
            if 'Include:' in analyzed_txt:
                data = {analyzed_txt.split(' ')[0].strip() \
                            : analyzed_txt.split('Include:')[1].strip()}
                include_in_boolean = True

            elif include_in_boolean:
                data = analyzed_txt
            ## include 관련 예외 처리 끝

            elif ':' in analyzed_txt \
                    and '-->' not in analyzed_txt \
                    and 'Include:' not in analyzed_txt :
                data = { analyzed_txt.split(':')[0].strip() \
                             : analyzed_txt.split(':')[1].strip() }


            else:
                data = analyzed_txt

            datas.append(data)

        #1. 데일리 윈도우 정리
        #2. include 정리

        # 마지막 정책 번호 더하기
        total_policy_num = policy_num
        policy_num += 1




    return total_policy_num

    # #### 한 셀 줄바꿈 방법
    # ws['A1'] = "Line 1\nLine 2"
    # ws['A1'].alignment = Alignment(wrap_text=True) # 하나의 셀에 여러 행을 넣을 수 있게 만듬.
