## dataRefine.py

# 1. Daily Window 정리
# 2. Include 정리
"""
unit_name = string
data_param = array => ['a', 'b']
"""
def data_refine(unit_name, data_param):

    unit_name_restrict = ['Include', 'Daily Windows', 'HW/OS/Client']
    if unit_name not in unit_name_restrict:
        print("조건에 없는 내용입니다.")
        return data_param

    for i in range(0, len(data_param)):

        if unit_name in data_param[i] \
                and type(data_param[i]) == dict:
            insert_array = []

            if data_param[i][unit_name] != '' :
                insert_array.append(data_param[i][unit_name])

            ## 추가
            not_in_word = ""
            if unit_name == 'HW/OS/Client':
                not_in_word = 'Include'
            elif unit_name == 'Include':
                not_in_word = 'Schedule'
            else:
                not_in_word = 'Schedule'

            j = 1
            while i+j < len(data_param) \
                and not_in_word not in data_param[i+j] \
                and type(data_param[i+j]) != dict:
                insert_array.append(data_param[i+j])
                j += 1

            # 추가
            data_param[i][unit_name] = insert_array
        # i 추가
        i += 1

    return data_param

def residence_refine(data_param):
    # (specific storage unit not required) 이것도 나중에 처리
    residence_count = 0
    for data in data_param:
        if type(data) != dict:
            continue

        keyname = list(data.keys())[0]
        if keyname != 'Residence':
            continue

        residence_count += 1

        if residence_count >= 2:
            data['Other Residence'] = data.pop('Residence')

    return data_param

def retention_refine(data_param):
    # 보관주기 바꾸기
    for data in data_param:
        if type(data) != dict or \
                'Retention Level' != list(data.keys())[0]:
            continue

        data['Retention Level'] = \
            data['Retention Level'].split('(')[1].split(')')[0].upper()

    return data_param

def calendar_refine(data_param):
    # calendar 있으면 처리
    for i in range(0, len(data_param)):
        if type(data_param[i]) != dict:
            continue

        keyname = list(data_param[i].keys())[0]
        if keyname != 'Calendar sched':
            continue

        insert_array = []
        j = 2
        while type(data_param[i+j]) != dict \
                and 'Excluded Dates----------' not in data_param[i+j] :
            insert_array.append(data_param[i+j])
            j += 1

        data_param[i]['Calendar sched'] = insert_array

    return data_param

# 여기서 다시 시작
def daily_windows_refine_for_7days(data_param):
    # daily windows 정리
    daily_windows_str = 'Daily Windows'
    none_defined_str = '(none defined)'
    everyday_str = 'Everyday '

    for data in data_param:
        if type(data) != dict \
                or list(data.keys())[0] != daily_windows_str \
                or data.get(daily_windows_str) == [] \
                or data.get(daily_windows_str)[0] == none_defined_str :
            continue

        for i in range(0, len(data.get(daily_windows_str))):
            data.get(daily_windows_str)[i] = \
                data.get(daily_windows_str)[i].split()[0] \
                + ' ' + \
                data.get(daily_windows_str)[i].split()[1]

        if len(data.get(daily_windows_str)) == 7:
            j = 0
            measure_str = data.get(daily_windows_str)[0].split()[1]
            for d in data.get(daily_windows_str):
                if d.split()[1] != measure_str:
                    j = 0
                j += 1

            if j == 7:
                data[daily_windows_str] = [everyday_str + measure_str]


    return data_param


## 2025.04.24 Network Directory Backup Added start
def network_backup_refine(data_param):

    windows_network_backup_str = 'Backup network drvs'
    standard_network_backup_str = 'Follow NFS Mounts'

    combined_key = 'Network Directory Backup'

    for data in data_param:
        if type(data) != dict:
            continue

        if windows_network_backup_str in data:
            data[combined_key] = data.pop(windows_network_backup_str)
        elif standard_network_backup_str in data:
            data[combined_key] = data.pop(standard_network_backup_str)

    return data_param

## 2025.04.24 Network Directory Backup Added end

def none_refine(data_param):
    # none 이나 [] 처리
    residence_count = 0
    for data in data_param:
        if type(data) != dict:
            continue

        keyname = list(data.keys())[0]
        if not data[keyname]:
            data[keyname] = ['(none defined)']

    return data_param