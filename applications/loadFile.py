# import os
# import time
# from datetime import datetime
# from flask import send_file
# from werkzeug.utils import secure_filename

# # local
# from applications.analyzeBppllistTxt import makeXlsx

# UPLOAD_PATH = './txt-dir/'
# XLSX_PATH = './xlsx-dir/'
# timeout = 60

# ## 파일 업로드 과정

# # 텍스트 파일 체크
# ALLOWED_FILE_TYPE_MAPPING = {
#     'txt': 'text/plain'
# }

# ALLOWED_EXTENSIONS = set(ALLOWED_FILE_TYPE_MAPPING.keys())
# ALLOWED_MIME_TYPES = set(ALLOWED_FILE_TYPE_MAPPING.values())


# # 파일 마임 체크
# def allowed_mime(mime_type):
#     return mime_type in ALLOWED_MIME_TYPES


# # 파일 확장자 체크
# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# # 파일 업로드
# def upload_file(file, filename):
#     if not file or not filename:
#         return "NOT EXIST FILE"

#     if upload_file and allowed_file(filename):
#         os.makedirs(UPLOAD_PATH, exist_ok=True)
#         os.makedirs(XLSX_PATH, exist_ok=True)
#         file_save_path = os.path.join(UPLOAD_PATH, filename)
#         print('file_save_path : {}'.format(file_save_path))
#         file.save(file_save_path)

#         mime_type = file.mimetype
#         content_type = file.content_type

#         if mime_type and allowed_mime(mime_type) and allowed_mime(content_type):
#             return "Saved : {}".format(filename)
#         else:
#             os.remove(file_save_path)
#             return "INVALID MIMETYPE : {}".format(mime_type)

#     else:
#         return 'INVALID FILE'

# # 전체 프로세스 진행
# def process(file):
#     filename = secure_filename(file.filename)

#     # 시간용
#     timestamp = time.mktime(datetime.today().timetuple())
#     filename_with_timestamp =  str(timestamp).split('.')[0] + '_' + filename

#     result = upload_file(file, filename_with_timestamp)

#     if 'INVALID' in result or 'NOT EXIST FILE' in result:
#         return result
#     else:
#         ##### 엑셀 만들기 시작 #####
#         makeXlsx.execute(UPLOAD_PATH, XLSX_PATH, filename_with_timestamp)
#         ##### 엑셀 만들기 끝 #####

#         return result

# def send_file_in_way(file_dir, file_name):
#     return send_file(
#         path_or_file=f'{file_dir}',
#         download_name=f'{file_name}',
#         as_attachment=True
#     )

# # 파일 다운로드 (import 전용)
# def download_file(file_name):
#     print('download Test!!')
#     # filename = secure_filename(file.filename)
#     # sheet_name = filename.split('.')[0] + '.xlsx'
#     # return send_file(path_or_file = f'{XLSX_PATH}{sheet_name}',
#     #                                 attachment_filename = f'{sheet_name}',
#     #                                 as_attachment = True)
#     file_dir = ''
#     if file_name[-4:] in '.txt' :
#         file_dir = './txt-dir/' + file_name
#     elif file_name[-4:] in 'xlsx' :
#         file_dir = './xlsx-dir/' + file_name
#     else:
#         return "/"

#     return send_file_in_way(file_dir, file_name)

import os
from datetime import datetime
from flask import send_file, current_app
from werkzeug.utils import secure_filename
from typing import Optional

# local
from applications.analyzeBppllistTxt import makeXlsx

class FileError(Exception):
    """Custom exception for file handling errors"""
    pass

class FileHandler:
    ALLOWED_FILE_TYPE_MAPPING = {
        'txt': 'text/plain'
    }
    ALLOWED_EXTENSIONS = set(ALLOWED_FILE_TYPE_MAPPING.keys())
    ALLOWED_MIME_TYPES = set(ALLOWED_FILE_TYPE_MAPPING.values())

    @staticmethod
    def allowed_mime(mime_type: str) -> bool:
        return mime_type in FileHandler.ALLOWED_MIME_TYPES

    @staticmethod
    def allowed_file(filename: str) -> bool:
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in FileHandler.ALLOWED_EXTENSIONS

    @staticmethod
    def upload_file(file, filename: str) -> str:
        """
        Upload and validate file
        Returns: Status message
        Raises: FileError if validation fails
        """
        if not file or not filename:
            raise FileError("File not provided")

        if not FileHandler.allowed_file(filename):
            raise FileError(f"Invalid file type: {filename}")

        try:
            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
            os.makedirs(current_app.config['XLSX_FOLDER'], exist_ok=True)
            
            file_save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            current_app.logger.info(f'Saving file to: {file_save_path}')
            file.save(file_save_path)

            mime_type = file.mimetype
            content_type = file.content_type

            if not (mime_type and FileHandler.allowed_mime(mime_type) and 
                   FileHandler.allowed_mime(content_type)):
                os.remove(file_save_path)
                raise FileError(f"Invalid MIME type: {mime_type}")

            return f"Saved: {filename}"

        except Exception as e:
            current_app.logger.error(f"File upload error: {str(e)}")
            raise FileError(f"Upload failed: {str(e)}")

    @staticmethod
    def process(file) -> str:
        """Process uploaded file and generate xlsx"""
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename_with_timestamp = f"{timestamp}_{filename}"

        try:
            result = FileHandler.upload_file(file, filename_with_timestamp)
            makeXlsx.execute(
                current_app.config['UPLOAD_FOLDER'],
                current_app.config['XLSX_FOLDER'],
                filename_with_timestamp
            )
            return result
        except FileError as e:
            return str(e)
        except Exception as e:
            current_app.logger.error(f"Process error: {str(e)}")
            return "Processing failed"

    @staticmethod
    def download_file(file_name: str):
        """Download file based on extension"""
        try:
            if file_name.endswith('.txt'):
                file_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], file_name)
            elif file_name.endswith('.xlsx'):
                file_dir = os.path.join(current_app.config['XLSX_FOLDER'], file_name)
            else:
                raise FileError("Invalid file extension")

            if not os.path.exists(file_dir):
                raise FileError("File not found")

            return send_file(
                path_or_file=file_dir,
                download_name=file_name,
                as_attachment=True
            )

        except Exception as e:
            current_app.logger.error(f"Download error: {str(e)}")
            return str(e)
