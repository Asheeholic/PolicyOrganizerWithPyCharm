# find all schedule count
def find_all_schedule_count(analyze_txt_lines):
    count = 0

    for line in analyze_txt_lines :
        if "Policy Name: " in line:
            print(line)

        if "Schedule:" not in line:
            continue

        count += 1

    return count
