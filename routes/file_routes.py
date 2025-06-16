from flask import Blueprint, jsonify, request, current_app
from typing import Dict, Any
from werkzeug.utils import secure_filename
# import applications.loadFile as loadFile
from applications.loadFile import FileHandler
import applications.loadTxtList as loadTxtList
import applications.loadXlsxList as loadXlsxList
from flask_login import login_required

file_bp = Blueprint('file', __name__)

@file_bp.route('/fileTextList', methods=['GET'])
@login_required
def file_txt_get_list() -> Dict[str, Any]:
    """Get list of text files
    
    Returns:
        JSON response with list of text files
    """
    try:
        result = {'result': loadTxtList.get_txt_list()}
        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f"Error getting text file list: {str(e)}")
        return jsonify({'error': 'Failed to get file list'}), 500

@file_bp.route('/fileXlsxList', methods=['GET'])
@login_required
def file_xlsx_get_list() -> Dict[str, Any]:
    """Get list of Excel files
    
    Returns:
        JSON response with list of Excel files
    """
    try:
        result = {'result': loadXlsxList.get_xlsx_list()}
        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f"Error getting Excel file list: {str(e)}")
        return jsonify({'error': 'Failed to get file list'}), 500

@file_bp.route('/fileupload', methods=['POST'])
@login_required
def file_upload() -> Dict[str, Any]:
    """Upload a file
    
    Returns:
        JSON response with upload result
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
            
        filename = secure_filename(file.filename)
        result = {'result': FileHandler.process(file)}
        current_app.logger.info(f"File uploaded successfully: {filename}")
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error uploading file: {str(e)}")
        return jsonify({'error': 'Failed to upload file'}), 500

@file_bp.route('/filedownload/<file_name>', methods=['GET'])
@login_required
def file_download(file_name: str):
    """Download a file
    
    Args:
        file_name: Name of file to download
        
    Returns:
        File download response
    """
    try:
        current_app.logger.info(f"Downloading file: {file_name}")
        return FileHandler.download_file(secure_filename(file_name))
    except Exception as e:
        current_app.logger.error(f"Error downloading file {file_name}: {str(e)}")
        return jsonify({'error': 'Failed to download file'}), 500

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed
    
    Args:
        filename: Name of file to check
        
    Returns:
        bool: True if file extension is allowed
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']