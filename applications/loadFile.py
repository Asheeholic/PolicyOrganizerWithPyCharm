# -*- coding: utf-8 -*-
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
                current_app.config['UPLOAD_FOLDER'] + '/',
                current_app.config['XLSX_FOLDER'] + '/',
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
