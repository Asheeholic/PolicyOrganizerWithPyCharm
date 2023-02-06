import os
import time
from datetime import datetime
from flask import send_file
from werkzeug.utils import secure_filename

# local
from applications.analyzeBppllistTxt import makeXlsx

UPLOAD_PATH = './txt-dir/'
XLSX_PATH = './xlsx-dir/'
timeout = 60

## 파일 업로드 과정

# 텍스트 파일 체크
ALLOWED_FILE_TYPE_MAPPING = {
    'txt': 'text/plain'
}

ALLOWED_EXTENSIONS = set(ALLOWED_FILE_TYPE_MAPPING.keys())
ALLOWED_MIME_TYPES = set(ALLOWED_FILE_TYPE_MAPPING.values())


# 파일 마임 체크
def allowed_mime(mime_type):
    return mime_type in ALLOWED_MIME_TYPES


# 파일 확장자 체크
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# 파일 업로드
def upload_file(file, filename):
    if not file or not filename:
        return "NOT EXIST FILE"

    if upload_file and allowed_file(filename):
        os.makedirs(UPLOAD_PATH, exist_ok=True)
        os.makedirs(XLSX_PATH, exist_ok=True)
        file_save_path = os.path.join(UPLOAD_PATH, filename)
        print('file_save_path : {}'.format(file_save_path))
        file.save(file_save_path)

        mime_type = file.mimetype
        content_type = file.content_type

        if mime_type and allowed_mime(mime_type) and allowed_mime(content_type):
            return "Saved : {}".format(filename)
        else:
            os.remove(file_save_path)
            return "INVALID MIMETYPE : {}".format(mime_type)

    else:
        return 'INVALID FILE'

# 전체 프로세스 진행
def process(file):
    filename = secure_filename(file.filename)

    # 시간용
    timestamp = time.mktime(datetime.today().timetuple())
    filename_with_timestamp =  str(timestamp).split('.')[0] + '_' + filename

    result = upload_file(file, filename_with_timestamp)

    if 'INVALID' in result or 'NOT EXIST FILE' in result:
        return result
    else:
        ##### 엑셀 만들기 시작 #####
        makeXlsx.execute(UPLOAD_PATH, XLSX_PATH, filename_with_timestamp)
        ##### 엑셀 만들기 끝 #####

        return result

def send_file_in_way(file_dir, file_name):
    return send_file(
        path_or_file=f'{file_dir}',
        download_name=f'{file_name}',
        as_attachment=True
    )

# 파일 다운로드 (import 전용)
def download_file(file_name):
    print('download Test!!')
    # filename = secure_filename(file.filename)
    # sheet_name = filename.split('.')[0] + '.xlsx'
    # return send_file(path_or_file = f'{XLSX_PATH}{sheet_name}',
    #                                 attachment_filename = f'{sheet_name}',
    #                                 as_attachment = True)
    file_dir = ''
    if file_name[-4:] in '.txt' :
        file_dir = './txt-dir/' + file_name
    elif file_name[-4:] in 'xlsx' :
        file_dir = './xlsx-dir/' + file_name
    else:
        return "/"

    return send_file_in_way(file_dir, file_name)
