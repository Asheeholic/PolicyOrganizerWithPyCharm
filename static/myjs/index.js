/**
 * draw txt List for
 * fileTextListFunc, fileXlsxListFunc and file GetAllFunc
  */
const drawTextListFunc = (divClassString, fileList) => {
    const fileListDiv = document.querySelector(".fileList");
    const selectListDiv = fileListDiv.querySelector("." + divClassString);

    for (let i=fileList.length-1; i>=0; i--) {
        const fileLi = document.createElement("div");
        const fileA = document.createElement("a");
        fileA.classList.add("font-monospace", "text-decoration-none");
        fileA.innerText = fileList[i];
        fileA.href = "/filedownload/" + fileList[i];

        // append
        fileLi.appendChild(fileA);
        selectListDiv.appendChild(fileLi);
    }
}

// get txt list
const fileTextListFunc = () => {
    let result = '';
    $.ajax({
        type: "GET",
        url: "/fileTextList",
        contentType: "application/json; charset=utf-8",
        // 파일 전송시 false, 기본은 true, json 전송시 "application/json; charset=utf-8"
        async: true,
        // async를 끈다. 동기적으로 실행하게 됨.
        success : function (responce) {
            console.log(responce.result)
            result = responce.result.sort()
            drawTextListFunc("txtList", result)
        },
        error : function() {
            alert("텍스트 로드 실패!");
        }
    });
    return result;
}

// get xlsx list
const fileXlsxListFunc = () => {
    let result = '';
    $.ajax({
        type: "GET",
        url: "/fileXlsxList",
        contentType: "application/json; charset=utf-8",
        // 파일 전송시 false, 기본은 true, json 전송시 "application/json; charset=utf-8"
        async: true,
        // async를 끈다. 동기적으로 실행하게 됨.
        success : function (responce) {
            console.log(responce.result)
            result = responce.result.sort()

            drawTextListFunc("xlsxList", result)
        },
        error : function() {
            alert("엑셀 로드 실패!");
        }
    });
    return result;
}

// get Both list
const fileGetAllFunc = () => {
    // 기존 리스트 삭제
    const txtList = document.querySelector(".txtList");
    const xlsxList = document.querySelector(".xlsxList");

    txtList.querySelectorAll('a').forEach( a => a.remove())
    xlsxList.querySelectorAll('a').forEach( a => a.remove())

    // 불러오기
    fileTextListFunc(); fileXlsxListFunc();
}

/**
 * Upload Function
 * This function with python is file check for '.txt' file
 * and send flask server and save it.
  */
const fileUploadFunc = (fileSource, fileSourceName) => {
    // console.log(fileSource);
    // 파일을 보내기 위해서는 formData 안에 모든 정보를 담아서 보낸다.
    const fileDetails = JSON.stringify({
        name : fileSourceName
    })
    
    let formData = new FormData();
    formData.append('body', fileDetails);
    formData.append('file', fileSource);

    let result = false;

    $.ajax({
        type: "POST",
        url: "/fileupload",
        processData: false, 
        // 파일 전송시 false, 기본은 true
        contentType: false, 
        // 파일 전송시 false, 기본은 true, json 전송시 "application/json; charset=utf-8"
        data : formData,
        async: false,
        // async를 끈다. 동기적으로 실행하게 됨.
        success : function (responce) {
            let resultUploadTest = responce.result;
            console.log(responce)
            console.log(resultUploadTest);
            if (!resultUploadTest.startsWith('INVALID') &&
                !resultUploadTest.startsWith('NOT EXIST FILE')) {
                result = true
            } else {
                alert("파일이 .txt 로 끝나지 않거나 txt 파일이 아닙니다.")
            }
        },
        error : function() {
            alert("파일 업로드 실패!");
        }
    });
    return result;
}

// const fileDownloadFunc = (filename) => {}

// Error Alert
const alertActive = () => {

    if (document.querySelector(".alert-danger")) {
        return;
    }

    const alertContainer = document.querySelector(".alertContainer");

    /**
     * <div class="alert alert-warning alert-dismissible fade show" role="alert">
     *   <strong>Holy guacamole!</strong> You should check in on some of those fields below.
     *   <button type="button" class="close" data-dismiss="alert" aria-label="Close">
     *     <span aria-hidden="true">&times;</span>
     *   </button>
     * </div>
      */
    const alertDiv = document.createElement("div");
    alertDiv.classList.add("alert", "alert-danger", "alert-dismissible", "fade", "show");
    alertDiv.setAttribute("role", "alert")

    const alertStrongInDiv = document.createElement("strong");
    alertStrongInDiv.innerText += " Holy guacamole! "

    const alertButtonInDiv = document.createElement("button");

    alertButtonInDiv.classList.add("btn-close");
    alertButtonInDiv.setAttribute("data-bs-dismiss", "alert");
    alertButtonInDiv.setAttribute("aria-label", "Close");
    const alertHidden = document.createElement("span");

    alertHidden.setAttribute("aria-hidden", "true")

    // 버튼 차일드
    alertButtonInDiv.appendChild(alertHidden);

    // 얼럿 차일드
    alertDiv.appendChild(alertStrongInDiv);
    alertDiv.innerHTML += " 파일명이나 파일을 체크해 주세요! "
    alertDiv.appendChild(alertButtonInDiv)

    alertContainer.appendChild(alertDiv)
}

// process active 
const active = () => {
    const fileUploadForm = document.querySelector(".fileUploadForm");
    const fileSourceTag = fileUploadForm.querySelector("input");
    const fileSource = fileSourceTag.files[0]
    const fileSourceName = fileSourceTag.files[0].name;

    // 값 초기화
    fileSourceTag.value = ''
    // file upload and checking
    if (fileUploadFunc(fileSource, fileSourceName)) {
        console.log('uploading success!') // true
        fileGetAllFunc();
    } else {
        console.log('uploading fail!')
        alertActive();
    }
}

// initial javascript
const init = () => {
    fileGetAllFunc();
}

init();
