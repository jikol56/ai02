# VBA Code Blocker 설치 가이드

이 문서는 VBA Code Blocker의 설치 방법을 안내합니다.

## 시스템 요구사항
- Windows 10 이상
- Python 3.8 이상
- 관리자 권한

## 설치 단계

### 1. 저장소 클론
```bash
git clone https://github.com/jikol56/ai02.git
cd ai02
```

### 2. 가상환경 생성 및 활성화(권장)
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. 필수 패키지 설치
```bash
pip install -r requirements.txt
```

### 4. 관리자 권한으로 실행
- 프로그램은 레지스트리 및 시스템 변경을 위해 관리자 권한이 필요합니다.
- Windows에서 `cmd` 또는 `PowerShell`을 "관리자 권한으로 실행" 후 아래 명령을 입력하세요.

```bash
python main.py
```

## 설치 후 확인
- GUI가 정상적으로 실행되는지 확인합니다.
- 로그(`logs/` 폴더)와 설정 파일(`config/`)이 정상적으로 생성되는지 확인합니다.

## 참고
- 설치 중 문제가 발생하면 [문제 해결 가이드](troubleshooting.md)를 참고하세요. 