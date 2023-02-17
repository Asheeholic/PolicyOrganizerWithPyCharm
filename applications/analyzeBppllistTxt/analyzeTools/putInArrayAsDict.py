def put_in_array_as_dict(analyze_txt_lines, not_in_the_list):
    datas = []

    # for include
    include_in_boolean = False

    for line_num in range(0, len(analyze_txt_lines)):

        # 짧게 요약
        analyzed_txt = analyze_txt_lines[line_num]
        data = {}

        # 공란 및 쓸데없는 문자 제외하고 시작하기
        if analyzed_txt in not_in_the_list:
            continue
        if 'Schedule:' in analyzed_txt:
            include_in_boolean = False

        ## include 관련 예외 처리
        if 'Include:' in analyzed_txt:
            data = {
                analyzed_txt.split(':')[0].strip() \
                        : analyzed_txt.split('Include:')[1].strip()
            }
            include_in_boolean = True

        elif include_in_boolean:
            data = analyzed_txt
        ## include 관련 예외 처리 끝

        elif ':' in analyzed_txt \
                and '-->' not in analyzed_txt \
                and 'Include:' not in analyzed_txt:
            data = {analyzed_txt.split(':')[0].strip() \
                        : analyzed_txt.split(':')[1].strip()}


        else:
            data = analyzed_txt

        datas.append(data)

    return datas