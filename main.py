# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
# Global
from flask import *

# local
from applications.analyzeBppllistTxt import makeXlsx
import applications.loadFile as loadFile
import applications.loadTxtList as loadTxtList
import applications.loadXlsxList as loadXlsxList

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

    # 분석 파이썬
    # makeXlsx.execute()

# Press the green button in the gutter to run the script.

@app.route('/')
def hello_world():
    return redirect(url_for('go_home'))

@app.route('/home')
def go_home():
    return render_template('index.html')

@app.route('/solution')
def go_solution():
    return render_template('solution.html')

## 텍스트 파일 리스트들
@app.route('/fileTextList', methods=['GET'])
def file_txt_get_list():
    result = { 'result' : loadTxtList.get_txt_list() }
    return jsonify(result)

## 엑셀 파일 리스트들
@app.route('/fileXlsxList', methods=['GET'])
def file_xlsx_get_list():
    result = { 'result' : loadXlsxList.get_xlsx_list() }
    return jsonify(result)

@app.route('/fileupload', methods=['GET', 'POST'])
def file_upload():
    file = request.files['file']
    result = { 'result' : loadFile.process(file) }
    return jsonify(result)

@app.route('/filedownload/<file_name>', methods=['GET', 'POST'])
def file_download(file_name):
    print("Downloading : " + file_name)
    return loadFile.download_file(file_name) # 리턴해야 파일을 줌..

if __name__ == '__main__':
    print_hi('PyCharm')
    print(app.config)
    app.run(host='0.0.0.0', port=8000)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
