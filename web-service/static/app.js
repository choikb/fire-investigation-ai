// 소방 AI 화재조사 시스템 - 프론트엔드
const API_BASE = window.location.origin;

// 상태 관리
let state = {
    currentImage: null,
    isDrawing: false,
    startX: 0,
    startY: 0,
    selectedArea: null,
    canvas: null,
    ctx: null,
    evidenceData: null
};

// DOM 요소 (초기화는 DOMContentLoaded에서)
let elements = {};

// 초기화
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM 로드 완료, 요소 초기화 시작');
    
    // DOM 요소 초기화
    elements = {
        uploadZone: document.getElementById('uploadZone'),
        fileInput: document.getElementById('fileInput'),
        imageZone: document.getElementById('imageZone'),
        sourceImage: document.getElementById('sourceImage'),
        drawCanvas: document.getElementById('drawCanvas'),
        actionButtons: document.getElementById('actionButtons'),
        resetBtn: document.getElementById('resetBtn'),
        analyzeBtn: document.getElementById('analyzeBtn'),
        initialState: document.getElementById('initialState'),
        loadingState: document.getElementById('loadingState'),
        evidenceResult: document.getElementById('evidenceResult'),
        evidenceList: document.getElementById('evidenceList'),
        analysisResult: document.getElementById('analysisResult'),
        analysisContent: document.getElementById('analysisContent'),
        reportSection: document.getElementById('reportSection'),
        reportBtn: document.getElementById('reportBtn'),
        reportResult: document.getElementById('reportResult')
    };
    
    // 요소 확인
    console.log('uploadZone:', elements.uploadZone);
    console.log('fileInput:', elements.fileInput);
    
    initEventListeners();
});

function initEventListeners() {
    console.log('이벤트 리스너 등록 시작');
    
    // 업로드 존 클릭
    if (elements.uploadZone) {
        elements.uploadZone.addEventListener('click', (e) => {
            console.log('업로드 존 클릭됨');
            e.preventDefault();
            e.stopPropagation();
            if (elements.fileInput) {
                elements.fileInput.click();
            }
        });
    }
    
    // 파일 선택
    if (elements.fileInput) {
        elements.fileInput.addEventListener('change', (e) => {
            console.log('파일 선택됨:', e.target.files);
            handleFileSelect(e);
        });
    }
    
    // 드래그 앤 드롭
    if (elements.uploadZone) {
        elements.uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
            elements.uploadZone.style.borderColor = '#d32f2f';
            elements.uploadZone.style.background = '#fff5f5';
        });
        
        elements.uploadZone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            elements.uploadZone.style.borderColor = '#ddd';
            elements.uploadZone.style.background = '#fafafa';
        });
        
        elements.uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            elements.uploadZone.style.borderColor = '#ddd';
            elements.uploadZone.style.background = '#fafafa';
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                processFile(files[0]);
            }
        });
    }
    
    // 버튼 이벤트
    if (elements.resetBtn) {
        elements.resetBtn.addEventListener('click', resetSelection);
    }
    if (elements.analyzeBtn) {
        elements.analyzeBtn.addEventListener('click', analyzeEvidence);
    }
    if (elements.reportBtn) {
        elements.reportBtn.addEventListener('click', generateReport);
    }
    
    console.log('이벤트 리스너 등록 완료');
}

function handleFileSelect(e) {
    console.log('handleFileSelect 호출됨');
    const file = e.target.files[0];
    if (file) {
        processFile(file);
    }
}

function processFile(file) {
    console.log('processFile 호출됨:', file.name);
    
    if (!file.type.startsWith('image/')) {
        alert('이미지 파일만 업로드 가능합니다.');
        return;
    }
    
    const reader = new FileReader();
    reader.onload = (e) => {
        console.log('FileReader 로드 완료');
        state.currentImage = new Image();
        state.currentImage.onload = displayImage;
        state.currentImage.src = e.target.result;
    };
    reader.onerror = (e) => {
        console.error('FileReader 오류:', e);
        alert('파일 읽기 오류가 발생했습니다.');
    };
    reader.readAsDataURL(file);
}

function displayImage() {
    console.log('displayImage 호출됨');
    
    if (!elements.uploadZone || !elements.imageZone || !elements.actionButtons) {
        console.error('필요한 요소가 없습니다');
        return;
    }
    
    // 업로드 존 숨기고 이미지 존 보이기
    elements.uploadZone.style.display = 'none';
    elements.imageZone.style.display = 'flex';
    elements.actionButtons.style.display = 'flex';
    
    // 이미지 표시
    elements.sourceImage.src = state.currentImage.src;
    
    // 캔버스 설정
    state.canvas = elements.drawCanvas;
    state.canvas.width = state.currentImage.width;
    state.canvas.height = state.currentImage.height;
    
    // 이미지 크기 조정
    const maxWidth = elements.imageZone.clientWidth - 50;
    const scale = Math.min(1, maxWidth / state.currentImage.width);
    elements.sourceImage.style.width = (state.currentImage.width * scale) + 'px';
    elements.sourceImage.style.height = (state.currentImage.height * scale) + 'px';
    state.canvas.style.width = (state.currentImage.width * scale) + 'px';
    state.canvas.style.height = (state.currentImage.height * scale) + 'px';
    
    state.ctx = state.canvas.getContext('2d');
    
    // Circle-to-Search 이벤트 설정
    setupCanvasEvents();
    
    // 단계 업데이트
    updateStep(2);
}

function setupCanvasEvents() {
    console.log('Canvas 이벤트 설정');
    
    if (!state.canvas) return;
    
    state.canvas.addEventListener('mousedown', startDrawing);
    state.canvas.addEventListener('mousemove', draw);
    state.canvas.addEventListener('mouseup', stopDrawing);
    state.canvas.addEventListener('mouseleave', stopDrawing);
}

function startDrawing(e) {
    state.isDrawing = true;
    const rect = state.canvas.getBoundingClientRect();
    const scaleX = state.canvas.width / rect.width;
    const scaleY = state.canvas.height / rect.height;
    state.startX = (e.clientX - rect.left) * scaleX;
    state.startY = (e.clientY - rect.top) * scaleY;
}

function draw(e) {
    if (!state.isDrawing) return;
    
    const rect = state.canvas.getBoundingClientRect();
    const scaleX = state.canvas.width / rect.width;
    const scaleY = state.canvas.height / rect.height;
    const currentX = (e.clientX - rect.left) * scaleX;
    const currentY = (e.clientY - rect.top) * scaleY;
    
    // 캔버스 초기화
    state.ctx.clearRect(0, 0, state.canvas.width, state.canvas.height);
    
    // 원 그리기
    const radius = Math.sqrt(
        Math.pow(currentX - state.startX, 2) + 
        Math.pow(currentY - state.startY, 2)
    );
    
    state.ctx.beginPath();
    state.ctx.arc(state.startX, state.startY, radius, 0, 2 * Math.PI);
    state.ctx.strokeStyle = '#d32f2f';
    state.ctx.lineWidth = 4;
    state.ctx.stroke();
    
    // 반투명 채우기
    state.ctx.fillStyle = 'rgba(211, 47, 47, 0.2)';
    state.ctx.fill();
    
    // 중심점
    state.ctx.beginPath();
    state.ctx.arc(state.startX, state.startY, 6, 0, 2 * Math.PI);
    state.ctx.fillStyle = '#d32f2f';
    state.ctx.fill();
}

function stopDrawing(e) {
    if (!state.isDrawing) return;
    state.isDrawing = false;
    
    const rect = state.canvas.getBoundingClientRect();
    const scaleX = state.canvas.width / rect.width;
    const scaleY = state.canvas.height / rect.height;
    const endX = (e.clientX - rect.left) * scaleX;
    const endY = (e.clientY - rect.top) * scaleY;
    
    const radius = Math.sqrt(
        Math.pow(endX - state.startX, 2) + 
        Math.pow(endY - state.startY, 2)
    );
    
    state.selectedArea = {
        centerX: state.startX / state.canvas.width,
        centerY: state.startY / state.canvas.height,
        radius: radius / Math.max(state.canvas.width, state.canvas.height)
    };
    
    console.log('선택 영역:', state.selectedArea);
}

function resetSelection() {
    console.log('resetSelection 호출됨');
    state.selectedArea = null;
    if (state.ctx && state.canvas) {
        state.ctx.clearRect(0, 0, state.canvas.width, state.canvas.height);
    }
}

async function analyzeEvidence() {
    console.log('analyzeEvidence 호출됨');
    
    if (!elements.initialState || !elements.loadingState) {
        console.error('필요한 요소가 없습니다');
        return;
    }
    
    // 로딩 상태 표시
    elements.initialState.style.display = 'none';
    elements.loadingState.style.display = 'block';
    elements.evidenceResult.style.display = 'none';
    elements.analysisResult.style.display = 'none';
    elements.reportSection.style.display = 'none';
    
    if (elements.analyzeBtn) {
        elements.analyzeBtn.disabled = true;
        elements.analyzeBtn.textContent = '⏳ 분석 중...';
    }
    
    try {
        // Mock 데이터 사용
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        state.evidenceData = {
            objects: [
                {
                    type: '전열기',
                    shape: '원통형 가열 장치',
                    material: '금속 + 세라믹',
                    purpose: '액체 가열용',
                    confidence: 0.92
                },
                {
                    type: '전원 케이블',
                    shape: '코일 형태',
                    material: '구리 + PVC 절연체',
                    purpose: '전력 공급',
                    confidence: 0.88
                },
                {
                    type: '연소 흔적',
                    shape: '불규칙한 탄화 패턴',
                    material: '탄화 물질',
                    purpose: '화재 확산 증거',
                    confidence: 0.95
                }
            ]
        };
        
        displayEvidenceResult(state.evidenceData);
        await performAIAnalysis(state.evidenceData);
        
    } catch (error) {
        console.error('분석 오류:', error);
        alert('분석 중 오류가 발생했습니다.');
    }
    
    if (elements.analyzeBtn) {
        elements.analyzeBtn.disabled = false;
        elements.analyzeBtn.textContent = '🔍 증거 식별 분석';
    }
}

function displayEvidenceResult(data) {
    console.log('displayEvidenceResult 호출됨');
    
    if (!elements.loadingState || !elements.evidenceResult || !elements.evidenceList) {
        console.error('필요한 요소가 없습니다');
        return;
    }
    
    elements.loadingState.style.display = 'none';
    elements.evidenceResult.style.display = 'block';
    
    let html = '';
    data.objects.forEach((obj, index) => {
        const confidenceClass = obj.confidence >= 0.9 ? 'confidence-high' : 'confidence-medium';
        html += `
            <div class="evidence-item">
                <div class="evidence-header">
                    <span class="evidence-type">${index + 1}. ${obj.type}</span>
                    <span class="confidence-badge ${confidenceClass}">신뢰도: ${(obj.confidence * 100).toFixed(0)}%</span>
                </div>
                <div class="evidence-details">
                    <div class="evidence-detail">
                        <span class="detail-label">형상</span>
                        <span class="detail-value">${obj.shape}</span>
                    </div>
                    <div class="evidence-detail">
                        <span class="detail-label">재질</span>
                        <span class="detail-value">${obj.material}</span>
                    </div>
                    <div class="evidence-detail" style="grid-column: 1 / -1;">
                        <span class="detail-label">용도</span>
                        <span class="detail-value">${obj.purpose}</span>
                    </div>
                </div>
            </div>
        `;
    });
    
    elements.evidenceList.innerHTML = html;
    updateStep(3);
}

async function performAIAnalysis(evidenceData) {
    console.log('performAIAnalysis 호출됨');
    
    try {
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        const analysisHTML = `
            <h4>🔍 분석 개요</h4>
            <p>제공된 현장 사진과 증거물 식별 결과를 바탕으로 <strong>전기적 요인</strong>에 의한 화재로 추정됩니다.</p>
            
            <h4>📊 감지된 주요 증거</h4>
            <ul>
                <li>전열기 (신뢰도: 92%) - 과열 흔적 관찰</li>
                <li>전원 케이블 (신뢰도: 88%) - 절연체 손상</li>
                <li>연소 흔적 (신뢰도: 95%) - V자형 연소 패턴</li>
            </ul>
            
            <h4>🔥 발화지점 추정</h4>
            <p>전열기 본체와 전원 케이블 연결 부위 근처로 추정됩니다.</p>
            
            <h4>⚠️ 화재 원인 분석</h4>
            <p>AI 분석 결과, 다음과 같은 원인이 가능성이 높습니다:</p>
            <ul>
                <li><strong>전열기 과부하</strong>: 정격 용량 이상의 과부하 사용</li>
                <li><strong>전원 케이블 단선</strong>: 반복적 구부림으로 인한 단선</li>
                <li><strong>열전달</strong>: 주변 가연물과의 접촉으로 인한 점화</li>
            </ul>
            
            <h4>📝 권장 사항</h4>
            <ul>
                <li>전열기 정격 전압 및 용량 확인</li>
                <li>케이블 및 플러그 교체 권장</li>
                <li>주변 가연물 정리 및 안전거리 확보</li>
            </ul>
            
            <p style="color: #666; font-size: 12px; margin-top: 20px;">
                * 본 분석은 ChatGPT AI 기반 추론 결과이며, 최종 판단은 담당 조사관이 수행해야 합니다.
            </p>
        `;
        
        if (elements.analysisResult) {
            elements.analysisResult.style.display = 'block';
        }
        if (elements.analysisContent) {
            elements.analysisContent.innerHTML = analysisHTML;
        }
        if (elements.reportSection) {
            elements.reportSection.style.display = 'block';
        }
        updateStep(4);
        
    } catch (error) {
        console.error('AI 분석 오류:', error);
    }
}

async function generateReport() {
    console.log('generateReport 호출됨');
    
    if (!elements.reportBtn || !elements.reportResult) {
        console.error('필요한 요소가 없습니다');
        return;
    }
    
    elements.reportBtn.disabled = true;
    elements.reportBtn.textContent = '⏳ 보고서 생성 중...';
    
    try {
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        const report = `화재조사 보고서

■ 사건 개요
- 사걸번호: FIRE-2024-001A
- 발생일시: 2024년 4월 6일
- 발생장소: 아파트 주방
- 조사관: 화재조사관

■ 현장 상황
싱크대 인근에서 화재가 발생하였으며, 주변 전열기 및 전원 케이블에서 
심각한 전기적 손상이 관찰되었습니다.

■ 증거 수집
1. 현장 사진 (3장) - 연소 흔적 및 증거물 촬영
2. 증거물 식별 결과:
   - 전열기 (형상: 원통형, 재질: 금속+세라믹)
   - 전원 케이블 (재질: 구리+PVC, 손상 상태)
   - 연소 흔적 (V자형 패턴)

■ AI 분석 결과
Circle-to-Search 기반 증거 분석 및 ChatGPT AI 원인 추론 결과,
전기적 요인에 의한 화재로 추정됩니다.

주요 원인:
1. 전열기 과부하 또는 과열
2. 전원 케이블 단선
3. 주변 가연물과의 접촉

■ 결론
본 화재는 전기적 요인으로 인한 발화로 추정되며, 
전열기 및 전원 케이블의 정상적인 사용 관리가 필요합니다.

■ 조치 사항
1. 전열기 정격 확인 및 교체
2. 전원 케이블 교체
3. 주변 가연물 정리

작성일: 2024년 4월 6일
AI 분석 시스템 v1.0 / 담당 조사관`;
        
        elements.reportResult.style.display = 'block';
        elements.reportResult.textContent = report;
        
    } catch (error) {
        console.error('보고서 생성 오류:', error);
        alert('보고서 생성 중 오류가 발생했습니다.');
    }
    
    elements.reportBtn.disabled = false;
    elements.reportBtn.textContent = '📝 조사보고서 생성';
}

function updateStep(step) {
    const steps = document.querySelectorAll('.step');
    steps.forEach((el, index) => {
        if (index < step) {
            el.classList.add('active');
        } else {
            el.classList.remove('active');
        }
    });
}
