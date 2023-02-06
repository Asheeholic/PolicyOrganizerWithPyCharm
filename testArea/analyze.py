# 20221111 nutanix update, windows update

# External import
from openpyxl.styles import Alignment

# Local import

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

    i = 0
    j = 0


    # 2차원 배열 집어넣기
    for line in lines :
        line = line.strip()
        analyze_txt_lines[i][j] = line

        j += 1
        if line == '------------------------------------------------------------' :
            i += 1
            j = 0


    ### 엑셀에 집어 넣기

    # 1. 열 별 제목 만들기
    column_titles = [
        '번호', '정책명', '정책 유형', '사용', '스토리지 유닛', '볼륨 풀',
        '엑셀러레이터 사용', '하드웨어', 'OS',
        '클라이언트 명', '백업 경로', '스케줄 형태',
        '캘린더 날짜', '백업보관일', '윈도우 시간'
    ]
    i = 0
    for title_name in column_titles :
        ws.cell(column=(2+i), row=2, value=title_name)
        i += 1

    # 2. 정책 별 정보 넣기

    # 정책 번호
    for policy_num in range(1, len(analyze_txt_lines)):
        # print(policy_num)

        policy_name = ''
        policy_type = ''
        active_policy = ''
        storage_unit = ''
        volume_pool = ''
        use_accelerator = ''
        hardware = ''
        os = ''
        client = ''
        backup_selection = ''
        schedule_type = ''
        calendar = ''
        retention = ''
        daily_windows = ''

        # 각 라인별 실행
        for line_num in range(0, len(analyze_txt_lines[policy_num])) :
            if analyze_txt_lines[policy_num][line_num] != 'HANJAEHO' : # 공란 제외하고 시작하기
                # print(line_num)

                # 정책명
                if 'Policy Name:' in analyze_txt_lines[policy_num][line_num] :
                    policy_name = analyze_txt_lines[policy_num][line_num].split(':')[1].strip()

                # 정책명
                if 'Policy Type:' in analyze_txt_lines[policy_num][line_num]:
                    policy_type = analyze_txt_lines[policy_num][line_num].split(':')[1].strip()

                # Active 구별
                if 'Active:' in analyze_txt_lines[policy_num][line_num] :
                    active_policy = analyze_txt_lines[policy_num][line_num].split(':')[1].strip()

                # 스토리지 유닛 -> 변경 필요
                # 변경이 무조건적으로 필요함.
                if 'Residence:' in analyze_txt_lines[policy_num][line_num] \
                        and '(specific storage unit not required)' not in analyze_txt_lines[policy_num][line_num]:
                    storage_unit = analyze_txt_lines[policy_num][line_num].split(':')[1].strip()

                # 볼륨 풀
                if 'Volume Pool:' in analyze_txt_lines[policy_num][line_num] \
                        and '(same as policy volume pool)' not in analyze_txt_lines[policy_num][line_num]:
                    volume_pool = analyze_txt_lines[policy_num][line_num].split(':')[1].strip()

                # 엑셀러레이터 사용 여부
                if 'Use Accelerator:' in analyze_txt_lines[policy_num][line_num] :
                    use_accelerator = analyze_txt_lines[policy_num][line_num].split(':')[1].strip()

                # 하드웨어, OS, Clinet
                if 'HW/OS/Client:' in analyze_txt_lines[policy_num][line_num] :
                    r0 = analyze_txt_lines[policy_num][line_num].split(':')[1]
                    r1 = ' '.join(r0.split())
                    hardware_os_client = r1.split(' ')
                    hardware = hardware_os_client[0].strip()
                    os = hardware_os_client[1].strip()
                    client = hardware_os_client[2].strip()

                    if 'Include:' not in analyze_txt_lines[policy_num][line_num + 2] :
                        i = 1
                        while 'Include:' not in analyze_txt_lines[policy_num][line_num + i] \
                                and '' != analyze_txt_lines[policy_num][line_num + i] :
                            r2 = ' '.join(analyze_txt_lines[policy_num][line_num + i].split())
                            hardware_os_client2 = r2.split(' ')
                            hardware += '\n' + hardware_os_client2[0]
                            os += '\n' + hardware_os_client2[1]
                            client += '\n' + hardware_os_client2[2]
                            i += 1

                    hardware = hardware.strip()
                    os = os.strip()
                    client = client.strip()

                # Backup Selection
                if 'Include:' in analyze_txt_lines[policy_num][line_num] :
                    backup_selection = analyze_txt_lines[policy_num][line_num].split('Include:')[1].strip()

                    if 'Schedule:' not in analyze_txt_lines[policy_num][line_num + 2]:
                        i = 1
                        while 'Schedule:' not in analyze_txt_lines[policy_num][line_num + i]:
                            backup_selection += '\n' + analyze_txt_lines[policy_num][line_num + i].strip()
                            i += 1

                    backup_selection = backup_selection.strip()

                # Schedule Type
                if 'Type:' in analyze_txt_lines[policy_num][line_num] \
                        and 'Schedule:' in analyze_txt_lines[policy_num][line_num - 1] :
                    schedule_type += "\n" + analyze_txt_lines[policy_num][line_num].split(':')[1].strip()
                    schedule_type = schedule_type.strip('\n')

                # Calendar
                if 'Calendar sched: Enabled' in analyze_txt_lines[policy_num][line_num] :
                    i = 1
                    while 'Excluded Dates----------' not in analyze_txt_lines[policy_num][line_num + i]:
                        calendar += '\n' + analyze_txt_lines[policy_num][line_num + i].strip()
                        i += 1

                # Retention
                if 'Retention Level: ' in analyze_txt_lines[policy_num][line_num]:
                    retention += "\n" + analyze_txt_lines[policy_num][line_num].split(':')[1].strip()
                    retention = retention.strip('\n')

                # Daily Window
                if 'Daily Windows:' in analyze_txt_lines[policy_num][line_num]:
                    i = 1
                    date_list = []
                    while 'HANJAEHO' not in analyze_txt_lines[policy_num][line_num + i] \
                            and analyze_txt_lines[policy_num][line_num + i] != '' :
                        date_list.append(analyze_txt_lines[policy_num][line_num + i].split('  -->  ')[0])
                        i += 1

                    # 매일이면
                    if len(date_list) == 7 :
                        daily_windows += '\n' + "매일 "+ date_list[1].split()[-1]
                    # 매일이 아니라면
                    else :
                        for d in date_list :
                            r0 = ' '.join(d.split())
                            if "Sunday" in d :
                                daily_windows += '\n' + "일요일 " + r0.split()[-1]
                            if "Monday" in d :
                                daily_windows += '\n' + "월요일 " + r0.split()[-1]
                            if "Tuesday" in d :
                                daily_windows += '\n' + "화요일 " + r0.split()[-1]
                            if "Wednesday" in d :
                                daily_windows += '\n' + "수요일 " + r0.split()[-1]
                            if "Thursday" in d :
                                daily_windows += '\n' + "목요일 " + r0.split()[-1]
                            if "Friday" in d :
                                daily_windows += '\n' + "금요일 " + r0.split()[-1]
                            if "Saturday" in d :
                                daily_windows += '\n' + "토요일 " + r0.split()[-1]

                    daily_windows += '\n...'

                    daily_windows = daily_windows.strip('\n')

        # 데이터들
        datas = [
            policy_num,
            policy_name,
            policy_type,
            active_policy,
            storage_unit,
            volume_pool,
            use_accelerator,
            hardware,
            os,
            client,
            backup_selection,
            schedule_type,
            calendar,
            retention,
            daily_windows,
        ]

        # 데이터 집어넣기
        i = 0
        for data in datas :
            ws.cell(column=(i+2), row=policy_num+2, value=data)
            i += 1

        # 마지막 정책 번호 더하기
        total_policy_num = policy_num
        policy_num += 1

    return total_policy_num

    # #### 한 셀 줄바꿈 방법
    # ws['A1'] = "Line 1\nLine 2"
    # ws['A1'].alignment = Alignment(wrap_text=True) # 하나의 셀에 여러 행을 넣을 수 있게 만듬.
