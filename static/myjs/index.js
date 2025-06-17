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

////// created by claude agent start //////
// 알림 표시 유틸리티
const showToast = async (message, type = 'success') => {
    const alertArea = document.getElementById('alertArea');
    const alert = document.createElement('div');
    
    const iconClass = {
        'success': 'check-circle',
        'danger': 'times-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    }[type];

    // opacity: 0으로 시작해서 트랜지션 효과 적용
    alert.style.transition = 'opacity 0.5s ease-in-out';
    alert.style.opacity = '0';
    
    alert.className = `alert alert-${type} d-flex align-items-center alert-dismissible`;
    alert.setAttribute('role', 'alert');
    
    alert.innerHTML = `
        <i class="fas fa-${iconClass} me-2"></i>
        <div>${message}</div>
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="닫기"></button>
    `;
      // 이전 알림이 있다면 페이드 아웃 후 제거를 기다림
    const existingAlerts = Array.from(alertArea.querySelectorAll('.alert'));
    if (existingAlerts.length > 0) {
        await Promise.all(existingAlerts.map(oldAlert => {
            return new Promise(resolve => {
                oldAlert.style.opacity = '0';
                setTimeout(() => {
                    oldAlert.remove();
                    resolve();
                }, 500);
            });
        }));
    }
    
    // 모든 이전 알림이 제거된 후 새 알림 추가
    alertArea.appendChild(alert);
    
    // DOM에 추가된 후 페이드 인
    setTimeout(() => {
        alert.style.opacity = '1';
    }, 10);
    
    // 성공/실패 메시지는 자동으로 사라지게 함
    if (type === 'success' || type === 'danger') {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 500);
        }, 3000);
    }
    
    // 닫기 버튼에 페이드 아웃 효과 추가
    const closeButton = alert.querySelector('.btn-close');
    closeButton.addEventListener('click', (e) => {
        e.preventDefault();
        alert.style.opacity = '0';
        setTimeout(() => {
            alert.remove();
        }, 500);
    });
};

// 파일 카드 생성 함수
const createFileCard = (fileName, type) => {
    const card = document.createElement('div');
    card.className = 'mb-2 w-100';
    
    card.innerHTML = `
        <div class="d-flex align-items-center justify-content-between p-2 border rounded">
            <div class="flex-grow-1 me-3 text-break">
                ${fileName}
            </div>
            <div class="d-flex gap-2 flex-shrink-0">
                <a href="/filedownload/${fileName}" class="btn btn-sm btn-outline-primary">
                    <i class="fas fa-download">Download</i>
                </a>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteFile('${fileName}')">
                    <i class="fas fa-trash-alt">Delete</i>
                </button>
            </div>
        </div>
    `;
    
    return card;
};

// 파일 리스트 렌더링 함수
const renderFileList = (divClassString, fileList) => {
    const fileListDiv = document.querySelector("." + divClassString);
    fileListDiv.innerHTML = ''; // 기존 내용 삭제
    
    if (fileList.length === 0) {
        const emptyMessage = document.createElement('div');
        emptyMessage.className = 'text-center text-muted my-4';
        emptyMessage.innerHTML = '파일이 없습니다.';
        fileListDiv.appendChild(emptyMessage);
        return;
    }
    
    const listContainer = document.createElement('div');
    listContainer.className = 'list-group list-group-flush';
    fileListDiv.appendChild(listContainer);
    
    const type = divClassString === 'txtList' ? 'txt' : 'xlsx';
    fileList.sort().reverse().forEach(fileName => {
        listContainer.appendChild(createFileCard(fileName, type));
    });
};

////// created by claude agent end //////

// CSRF 토큰 가져오기 함수
const getCSRFToken = () => {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
};

// fetch 요청에 CSRF 토큰을 포함하는 기본 헤더 설정
const fetchWithCSRF = async (url, options = {}) => {
    const csrfToken = getCSRFToken();
    const defaultHeaders = {
        'X-CSRFToken': csrfToken
    };
    
    options.headers = {
        ...defaultHeaders,
        ...options.headers
    };
    
    return fetch(url, options);
};

// get txt list
const fileTextListFunc = async () => {
    try {
        const response = await fetchWithCSRF('/fileTextList');
        if (!response.ok) throw new Error('텍스트 파일 목록을 가져오는데 실패했습니다.');
        
        const data = await response.json();
        renderFileList('txtList', data.result);
    } catch (error) {
        showToast(error.message, 'danger');
    }
}

// get xlsx list
const fileXlsxListFunc = async () => {
    try {
        const response = await fetchWithCSRF('/fileXlsxList');
        if (!response.ok) throw new Error('엑셀 파일 목록을 가져오는데 실패했습니다.');
        
        const data = await response.json();
        renderFileList('xlsxList', data.result);
    } catch (error) {
        showToast(error.message, 'danger');
    }
}

// get Both list
const fileGetAllFunc = () => {
    fileTextListFunc();
    fileXlsxListFunc();
}

// 파일 업로드 함수
const fileUploadFunc = async (fileSource, fileSourceName) => {
    try {
        const fileDetails = JSON.stringify({ name: fileSourceName });
        const formData = new FormData();
        formData.append('body', fileDetails);
        formData.append('file', fileSource);

        const response = await fetchWithCSRF('/fileupload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('파일 업로드에 실패했습니다.');
        
        const data = await response.json();
        showToast('파일이 성공적으로 업로드되었습니다.');
        fileGetAllFunc(); // 목록 새로고침
        return true;
    } catch (error) {
        showToast(error.message, 'danger');
        return false;
    }
};

// 파일 삭제 함수
const deleteFile = async (fileName) => {
    if (!confirm(`${fileName} 파일을 삭제하시겠습니까?`)) return;
    
    try {
        showToast('파일 삭제 중...', 'info');
        
        const response = await fetchWithCSRF(`/delete/${fileName}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || '파일 삭제에 실패했습니다.');
        }
        
        showToast(data.message || '파일이 삭제되었습니다.', 'success');
        
        // DOM에서 실제 파일 항목 제거
        const fileCard = document.querySelector(`[data-filename="${fileName}"]`);
        if (fileCard) {
            fileCard.remove();
        }
        
        // 파일 목록 새로고침
        fileGetAllFunc();
    } catch (error) {
        showToast(error.message, 'danger');
    }
};

// 페이지 로드 시 파일 목록 가져오기
document.addEventListener('DOMContentLoaded', () => {
    fileGetAllFunc();
});
