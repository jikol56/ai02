# VBA Code Blocker

## 소개
이 프로젝트는 Windows 환경에서 VBA(Visual Basic for Applications) 코드의 실행을 차단하여 보안을 강화하고 시스템 오류를 방지하는 프로그램입니다.

## 주요 기능
- VBA 매크로 실행 차단
- Office 문서의 VBA 코드 실행 방지
- 시스템 레벨에서의 VBA 관련 프로세스 모니터링
- 사용자 친화적인 인터페이스로 VBA 차단 상태 관리

## 기술 스택
- Python 3.x
- Windows API (win32api)
- PyQt6 (GUI 인터페이스)
- Windows Registry 관리

## 프로젝트 구조
```
.
├── src/
│   ├── core/              # 핵심 기능 구현
│   │   ├── vba_blocker.py # VBA 차단 로직
│   │   └── registry.py    # 레지스트리 관리
│   ├── gui/               # 사용자 인터페이스
│   │   └── main_window.py # 메인 윈도우
│   └── utils/             # 유틸리티 함수
│       └── logger.py      # 로깅 기능
├── tests/                 # 테스트 코드
├── docs/                  # 문서
└── requirements.txt       # 의존성 패키지
```

## 시작하기
### 필수 조건
- Windows 10/11
- Python 3.8 이상
- 관리자 권한

### 설치
```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 실행
```bash
python src/main.py
```

## 보안 주의사항
- 이 프로그램은 관리자 권한이 필요합니다
- 시스템 레벨에서 VBA를 차단하므로 신중하게 사용해야 합니다
- Office 프로그램 사용에 영향을 줄 수 있습니다

## 라이선스
이 프로젝트는 MIT 라이선스 하에 있습니다. 