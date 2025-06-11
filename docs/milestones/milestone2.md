# 마일스톤 2: 시스템 변경 사항 추적 및 로깅 시스템 구현

## 목표
- 시스템 변경 사항 추적 기능 구현
- 로깅 시스템 강화
- GUI 개선

## 구현된 기능

### 1. 시스템 변경 사항 추적
- 레지스트리 변경 사항 모니터링
- 프로세스 상태 변경 추적
- 변경 사항 로깅 및 저장
- 변경 사항 조회 및 초기화 기능

### 2. 로깅 시스템
- 다양한 로그 타입 지원
  - 일반 로그 (vba_blocker.log)
  - 디버그 로그 (debug.log)
  - 시스템 변경 로그 (system_changes.log)
- 로그 파일 자동 로테이션
  - 일별 로테이션 (일반 로그)
  - 크기 기반 로테이션 (디버그, 시스템 변경 로그)
- 로그 조회 및 관리 기능

### 3. GUI 개선
- 탭 인터페이스 구현
  - 메인 탭: VBA 차단 상태 및 제어
  - 시스템 변경 사항 탭: 변경 이력 조회
  - 로그 탭: 로그 조회 및 관리
- 사용자 피드백 개선
  - 상태 표시 개선
  - 오류 메시지 상세화
  - 작업 확인 대화상자

## 기술적 구현

### 1. ChangeTracker 클래스
```python
class ChangeTracker:
    def __init__(self):
        self.changes = []
        self.is_tracking = False
        self.tracking_thread = None
```

주요 기능:
- 변경 사항 추적 시작/중지
- 레지스트리 변경 모니터링
- 프로세스 상태 변경 추적
- 변경 사항 저장 및 관리

### 2. Logger 클래스
```python
class Logger:
    def __init__(self, name="vba_blocker"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
```

주요 기능:
- 다양한 로그 타입 지원
- 로그 파일 자동 로테이션
- 로그 조회 및 초기화
- 시스템 변경 사항 특별 로깅

### 3. GUI 개선
```python
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.vba_blocker = VBABlocker()
        self.init_ui()
```

주요 기능:
- 탭 기반 인터페이스
- 실시간 상태 업데이트
- 로그 조회 및 관리
- 사용자 피드백 개선

## 테스트 결과
- 시스템 변경 사항 추적 테스트 통과
- 로깅 시스템 테스트 통과
- GUI 기능 테스트 통과

## 다음 단계
1. 보안 기능 강화
2. 성능 최적화
3. 사용자 매뉴얼 작성

## 참고 사항
- 로그 파일은 `logs` 디렉토리에 저장됩니다.
- 시스템 변경 사항은 JSON 형식으로 저장됩니다.
- 로그 파일은 자동으로 로테이션되며, 오래된 로그는 자동으로 삭제됩니다. 