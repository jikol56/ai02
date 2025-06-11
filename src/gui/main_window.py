import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt
from core.vba_blocker import VBABlocker

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.vba_blocker = VBABlocker()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('VBA Code Blocker')
        self.setGeometry(100, 100, 400, 300)

        # 중앙 위젯 생성
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 상태 표시 레이블
        self.status_label = QLabel('VBA 차단 상태: 확인 중...')
        layout.addWidget(self.status_label)

        # VBA 차단 버튼
        self.block_button = QPushButton('VBA 차단')
        self.block_button.clicked.connect(self.toggle_vba_block)
        layout.addWidget(self.block_button)

        # 상태 업데이트
        self.update_status()

    def toggle_vba_block(self):
        if self.vba_blocker.block_vba_execution():
            self.status_label.setText('VBA 차단 상태: 차단됨')
            self.block_button.setText('VBA 차단 해제')
        else:
            self.status_label.setText('VBA 차단 상태: 차단 실패')
        self.update_status()

    def update_status(self):
        is_blocked = self.vba_blocker.is_vba_blocked()
        self.status_label.setText(f'VBA 차단 상태: {"차단됨" if is_blocked else "차단되지 않음"}')
        self.block_button.setText('VBA 차단 해제' if is_blocked else 'VBA 차단')

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 