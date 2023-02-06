import os

XLSX_PATH = './xlsx-dir/'
def get_xlsx_list():
    return os.listdir(XLSX_PATH)
