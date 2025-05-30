from flask import Blueprint, jsonify, request
import applications.loadFile as loadFile
import applications.loadTxtList as loadTxtList
import applications.loadXlsxList as loadXlsxList

file_bp = Blueprint('file', __name__)

@file_bp.route('/fileTextList', methods=['GET'])
def file_txt_get_list():
    result = {'result': loadTxtList.get_txt_list()}
    return jsonify(result)

@file_bp.route('/fileXlsxList', methods=['GET'])
def file_xlsx_get_list():
    result = {'result': loadXlsxList.get_xlsx_list()}
    return jsonify(result)

@file_bp.route('/fileupload', methods=['GET', 'POST'])
def file_upload():
    file = request.files['file']
    result = {'result': loadFile.process(file)}
    return jsonify(result)

@file_bp.route('/filedownload/<file_name>', methods=['GET', 'POST'])
def file_download(file_name):
    print(f"Downloading: {file_name}")
    return loadFile.download_file(file_name)