# 마일스톤 4: 버그 수정 및 안정화

**진행 일시:** YYYY-MM-DD

## 주요 내용
- GUI에서 VBA 차단 기능 호출 시 함수명 불일치 오류 수정 (`block_vba` → `block_vba_execution`)
- Logger 클래스 사용 시 name 인자 누락 오류 수정
- 각 핵심 클래스(`VBABlocker`, `SecurityManager`, `ProcessMonitor`, `RegistryManager`, `ChangeTracker`)의 로거 초기화 방식 통일
- 관리자 권한 실행 및 오류 메시지 안내 강화
- tkinter 기반 GUI 정상 표시 및 예외 처리 개선

## 기술적 상세
- `main_window.py`에서 `self.vba_blocker.block_vba()`를 `self.vba_blocker.block_vba_execution()`으로 변경
- Logger 인스턴스 생성 시 name 인자 필수화 및 각 클래스별 고유 name 적용
- 각 클래스에서 `logging.getLogger(__name__)` 대신 `Logger('클래스명')` 사용
- 관리자 권한 체크 및 안내 메시지 일관성 유지

## 문제 및 해결
- 함수명 불일치로 인한 AttributeError → 함수명 일치시켜 해결
- Logger 인자 누락으로 인한 TypeError → name 인자 추가로 해결
- GUI가 바로 꺼지는 현상 → 관리자 권한 안내 및 오류 메시지 확인 절차 안내

## 향후 계획
- 사용자 피드백 반영한 추가 안정화
- 예외 상황별 상세 안내 및 로그 강화 