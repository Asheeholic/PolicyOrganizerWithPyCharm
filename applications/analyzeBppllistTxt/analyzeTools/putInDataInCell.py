# putInDataInCell.py
"""
 column_titles = [
        'Policy Name',
        'Policy Type',
        'Active',
        'Residence', # storage unit
        'HW/OS/Client',
        'Network Directory Backup', # Network Directory Backup ## 2025.04.24
        'Include', # backup selection
        'Schedule', # Schedule name
        'Type', # schedule type
        'Retention Level', # retention (레벨은 안찍히고 뒤에 날짜만)
        'Frequency', # Frequency / calendar
        'Calendar sched',
        'Daily Windows'
    ]
"""
def put_in_data_in_cell(ws, column_titles, data_param, row_num):

    # 스케줄 카운트
    schedule_count = 0
    for data_unit_for_sched_count in data_param:
        if type(data_unit_for_sched_count) == dict \
            and list(data_unit_for_sched_count.keys())[0] == 'Schedule':
                schedule_count += 1

    # cell_data = []
    # for_extra_schedule_data = []

    row_num_added = row_num
    cell_col_num = 1
    j_for_total_schedule_row = 0
    for title in column_titles:

        # for schedule count
        i_for_schedule_row = 0
        same_column_title_count = 1

        for i in range(0, len(data_param)):
            data_unit = data_param[i]
            # 우선 dict 아닌 것 제외
            if type(data_unit) != dict \
                    or list(data_unit.keys())[0] != title:
                continue

            # 여기서 부터 다시해보기
            if type(data_unit.get(title)) == list \
                    and len(data_unit.get(title)) >= 1 :
                to_one_string = ''
                for li_data in data_unit.get(title):
                    to_one_string += li_data
                    to_one_string += '\n'
                data_unit[title] = to_one_string.strip('\n')

            # 스케줄이 2개 이상일 때 아니면 이미 그 셀 자리에 데이터가 있을 때
            ## row를 증가 시켜 그 밑에 두게 한다.
            # print(data_unit.get(title))
            if data_unit.get(title) == [] \
                    or data_unit.get(title) is None:
                pass

            # 이것도 나중에 봐야겠음. 데이터가 제대로 안들어감.
            elif schedule_count >= 2 and same_column_title_count >= 2 :
                i_for_schedule_row += 1
                ws.cell(row=row_num_added + i_for_schedule_row,
                        column=cell_col_num,
                        value=data_unit.get(title))

                # 토탈 플러스 해서 넘김
                if j_for_total_schedule_row < i_for_schedule_row :
                    j_for_total_schedule_row = i_for_schedule_row

            # 캘린더가 있을 때

            else:
                ws.cell(column=cell_col_num, row=row_num_added, value=data_unit.get(title))
                same_column_title_count += 1

        cell_col_num += 1
            # print(cell_col_num)
    row_num_added = row_num_added + 1 + j_for_total_schedule_row

    return row_num_added
    # 마지막 row를 찾아서 데이터가 없다면 맨 마지막에 넣기
    # 이거 수정 필요
    # ws.cell(column=(policy_num+2), row=policy_num+2, value=data_param)