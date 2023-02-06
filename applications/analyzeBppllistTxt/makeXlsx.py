# External import
import openpyxl


# Local import
from . import analyze
from . import style

# 정의 함수
def execute(txt_dir, xlsx_dir, txt_file):
    wb = openpyxl.Workbook()
    ws = wb.active
    # 스타일 만들기

    # 필수 파라미터
    # txt_dir = 'txt-dir/'
    # xlsx_dir = 'xlsx-dir/'
    # txt_file = 'bppllist.txt'

    width_rate = 1.3 # 엑셀 가로 넓이 배율

    # 파일 열기
    file = open(txt_dir + txt_file)
    sheet_name = txt_file.split('.')[0]
    lines = file.readlines()

    # 분석기 실행 (analyze.py)
    total_policy_number = analyze.execute(sheet_name, ws, lines)

    # 스타일러 실행 (style.py)
    style.execute(ws, total_policy_number, width_rate)

    # 저장
    file.close()

    filename = str(xlsx_dir + sheet_name + '.xlsx')
    wb.save(filename)