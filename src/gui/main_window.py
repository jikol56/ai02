import sys
import logging
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                           QPushButton, QLabel, QMessageBox, QHBoxLayout,
                           QTextEdit, QTabWidget, QGroupBox, QScrollArea,
                           QComboBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon
from ..core.vba_blocker import VBABlocker

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.vba_blocker = VBABlocker()
        self.init_ui()
        
        # 상태 업데이트 타이머
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(5000)  # 5초마다 상태 업데이트
        
    def init_ui(self):
        self.setWindowTitle('VBA Code Blocker')
        self.setGeometry(100, 100, 800, 600)
        
        # 중앙 위젯 생성
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        main_layout = QVBoxLayout(central_widget)
        
        # 탭 위젯 생성
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # 메인 탭
        main_tab = QWidget()
        tab_widget.addTab(main_tab, "메인")
        
        # 메인 탭 레이아웃
        main_tab_layout = QVBoxLayout(main_tab)
        
        # 상태 표시 그룹
        status_group = QGroupBox("VBA 차단 상태")
        status_layout = QVBoxLayout()
        
        self.status_label = QLabel("VBA 차단 상태: 확인 중...")
        self.status_label.setFont(QFont('Arial', 12))
        status_layout.addWidget(self.status_label)
        
        status_group.setLayout(status_layout)
        main_tab_layout.addWidget(status_group)
        
        # 버튼 레이아웃
        button_layout = QHBoxLayout()
        
        self.block_button = QPushButton('VBA 차단')
        self.block_button.setFont(QFont('Arial', 10))
        self.block_button.clicked.connect(self.toggle_vba_block)
        button_layout.addWidget(self.block_button)
        
        self.restore_button = QPushButton('VBA 복원')
        self.restore_button.setFont(QFont('Arial', 10))
        self.restore_button.clicked.connect(self.restore_vba)
        self.restore_button.setEnabled(False)
        button_layout.addWidget(self.restore_button)
        
        main_tab_layout.addLayout(button_layout)
        
        # 시스템 변경 사항 탭
        changes_tab = QWidget()
        tab_widget.addTab(changes_tab, "시스템 변경 사항")
        
        # 변경 사항 탭 레이아웃
        changes_layout = QVBoxLayout(changes_tab)
        
        # 변경 사항 표시 영역
        changes_group = QGroupBox("시스템 변경 사항")
        changes_group_layout = QVBoxLayout()
        
        self.changes_text = QTextEdit()
        self.changes_text.setReadOnly(True)
        changes_group_layout.addWidget(self.changes_text)
        
        changes_group.setLayout(changes_group_layout)
        changes_layout.addWidget(changes_group)
        
        # 변경 사항 관리 버튼
        changes_button_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton('새로고침')
        self.refresh_button.setFont(QFont('Arial', 10))
        self.refresh_button.clicked.connect(self.refresh_changes)
        changes_button_layout.addWidget(self.refresh_button)
        
        self.clear_button = QPushButton('변경 사항 지우기')
        self.clear_button.setFont(QFont('Arial', 10))
        self.clear_button.clicked.connect(self.clear_changes)
        changes_button_layout.addWidget(self.clear_button)
        
        changes_layout.addLayout(changes_button_layout)
        
        # 로그 탭
        log_tab = QWidget()
        tab_widget.addTab(log_tab, "로그")
        
        # 로그 탭 레이아웃
        log_layout = QVBoxLayout(log_tab)
        
        # 로그 타입 선택
        log_type_layout = QHBoxLayout()
        log_type_label = QLabel("로그 타입:")
        log_type_label.setFont(QFont('Arial', 10))
        log_type_layout.addWidget(log_type_label)
        
        self.log_type_combo = QComboBox()
        self.log_type_combo.addItems(['모든 로그', 'VBA 차단 로그', '디버그 로그', '시스템 변경 로그'])
        self.log_type_combo.currentTextChanged.connect(self.refresh_logs)
        log_type_layout.addWidget(self.log_type_combo)
        
        log_layout.addLayout(log_type_layout)
        
        # 로그 표시 영역
        log_group = QGroupBox("로그 내용")
        log_group_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_group_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_group_layout)
        log_layout.addWidget(log_group)
        
        # 로그 관리 버튼
        log_button_layout = QHBoxLayout()
        
        self.refresh_log_button = QPushButton('새로고침')
        self.refresh_log_button.setFont(QFont('Arial', 10))
        self.refresh_log_button.clicked.connect(self.refresh_logs)
        log_button_layout.addWidget(self.refresh_log_button)
        
        self.clear_log_button = QPushButton('로그 지우기')
        self.clear_log_button.setFont(QFont('Arial', 10))
        self.clear_log_button.clicked.connect(self.clear_logs)
        log_button_layout.addWidget(self.clear_log_button)
        
        log_layout.addLayout(log_button_layout)
        
        # 초기 상태 업데이트
        self.update_status()
        
    def toggle_vba_block(self):
        try:
            if self.vba_blocker.block_vba_execution():
                self.status_label.setText("VBA 차단 상태: 차단됨")
                self.block_button.setText('VBA 차단 해제')
                self.restore_button.setEnabled(True)
                QMessageBox.information(self, '성공', 'VBA가 성공적으로 차단되었습니다.')
            else:
                QMessageBox.warning(self, '경고', 'VBA 차단에 실패했습니다.')
        except Exception as e:
            QMessageBox.critical(self, '오류', f'VBA 차단 중 오류가 발생했습니다: {str(e)}')
            
    def restore_vba(self):
        reply = QMessageBox.question(self, '확인', 
                                   'VBA를 복원하시겠습니까?',
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                if self.vba_blocker.restore_vba():
                    self.status_label.setText("VBA 차단 상태: 차단 해제됨")
                    self.block_button.setText('VBA 차단')
                    self.restore_button.setEnabled(False)
                    QMessageBox.information(self, '성공', 'VBA가 성공적으로 복원되었습니다.')
                else:
                    QMessageBox.warning(self, '경고', 'VBA 복원에 실패했습니다.')
            except Exception as e:
                QMessageBox.critical(self, '오류', f'VBA 복원 중 오류가 발생했습니다: {str(e)}')
                
    def update_status(self):
        try:
            is_blocked = self.vba_blocker.is_vba_blocked()
            self.status_label.setText(f"VBA 차단 상태: {'차단됨' if is_blocked else '차단 해제됨'}")
            self.block_button.setText('VBA 차단 해제' if is_blocked else 'VBA 차단')
            self.restore_button.setEnabled(is_blocked)
            
            # 변경 사항 업데이트
            self.refresh_changes()
        except Exception as e:
            logging.error(f"상태 업데이트 중 오류 발생: {str(e)}")
            
    def refresh_changes(self):
        try:
            changes = self.vba_blocker.get_system_changes()
            if changes:
                changes_text = "\n".join([
                    f"[{change['timestamp']}] {change['type']}: {change['description']}"
                    for change in changes
                ])
                self.changes_text.setText(changes_text)
            else:
                self.changes_text.setText("변경 사항이 없습니다.")
        except Exception as e:
            logging.error(f"변경 사항 새로고침 중 오류 발생: {str(e)}")
            
    def clear_changes(self):
        reply = QMessageBox.question(self, '확인', 
                                   '모든 변경 사항을 지우시겠습니까?',
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                self.vba_blocker.clear_system_changes()
                self.changes_text.clear()
                QMessageBox.information(self, '성공', '변경 사항이 모두 지워졌습니다.')
            except Exception as e:
                QMessageBox.critical(self, '오류', f'변경 사항 지우기 중 오류가 발생했습니다: {str(e)}')
                
    def refresh_logs(self):
        try:
            log_type = self.log_type_combo.currentText()
            log_type_map = {
                '모든 로그': 'all',
                'VBA 차단 로그': 'vba_blocker',
                '디버그 로그': 'debug',
                '시스템 변경 로그': 'system_changes'
            }
            
            logs = self.vba_blocker.logger.get_recent_logs(log_type_map[log_type])
            if logs:
                self.log_text.setText("".join(logs))
            else:
                self.log_text.setText("로그가 없습니다.")
        except Exception as e:
            logging.error(f"로그 새로고침 중 오류 발생: {str(e)}")
            
    def clear_logs(self):
        reply = QMessageBox.question(self, '확인', 
                                   '모든 로그를 지우시겠습니까?',
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                log_type = self.log_type_combo.currentText()
                log_type_map = {
                    '모든 로그': 'all',
                    'VBA 차단 로그': 'vba_blocker',
                    '디버그 로그': 'debug',
                    '시스템 변경 로그': 'system_changes'
                }
                
                self.vba_blocker.logger.clear_logs(log_type_map[log_type])
                self.log_text.clear()
                QMessageBox.information(self, '성공', '로그가 모두 지워졌습니다.')
            except Exception as e:
                QMessageBox.critical(self, '오류', f'로그 지우기 중 오류가 발생했습니다: {str(e)}')

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_()) 