import tkinter as tk
from tkinter import ttk, messagebox
from src.core.vba_blocker import VBABlocker
from src.core.logger import logger

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("VBA Code Blocker")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        self.vba_blocker = VBABlocker()
        self.setup_ui()
        
    def setup_ui(self):
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 버튼 프레임
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=0, column=0, columnspan=2, pady=10)
        
        # VBA 차단 버튼
        block_button = ttk.Button(
            button_frame,
            text="VBA 차단",
            command=self.block_vba
        )
        block_button.grid(row=0, column=0, padx=5)
        
        # VBA 복원 버튼
        restore_button = ttk.Button(
            button_frame,
            text="VBA 복원",
            command=self.restore_vba
        )
        restore_button.grid(row=0, column=1, padx=5)
        
        # 상태 표시 레이블
        self.status_label = ttk.Label(
            main_frame,
            text="대기 중...",
            font=("Arial", 10)
        )
        self.status_label.grid(row=1, column=0, columnspan=2, pady=5)
        
        # 로그 표시 영역
        log_frame = ttk.LabelFrame(main_frame, text="로그", padding="5")
        log_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.log_text = tk.Text(
            log_frame,
            height=15,
            width=60,
            wrap=tk.WORD
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 스크롤바
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text['yscrollcommand'] = scrollbar.set
        
        # 초기 로그 표시
        self.log_text.insert(tk.END, "프로그램이 시작되었습니다.\n")
        self.log_text.config(state=tk.DISABLED)
        
    def block_vba(self):
        try:
            self.status_label.config(text="VBA 차단 중...")
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, "\nVBA 차단을 시작합니다...\n")
            self.log_text.config(state=tk.DISABLED)
            
            self.vba_blocker.block_vba_execution()
            
            self.status_label.config(text="VBA가 차단되었습니다.")
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, "VBA가 성공적으로 차단되었습니다.\n")
            self.log_text.config(state=tk.DISABLED)
            
            messagebox.showinfo("성공", "VBA가 성공적으로 차단되었습니다.")
            
        except Exception as e:
            self.status_label.config(text="오류 발생")
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, f"오류 발생: {str(e)}\n")
            self.log_text.config(state=tk.DISABLED)
            
            messagebox.showerror("오류", f"VBA 차단 중 오류가 발생했습니다:\n{str(e)}")
    
    def restore_vba(self):
        try:
            self.status_label.config(text="VBA 복원 중...")
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, "\nVBA 복원을 시작합니다...\n")
            self.log_text.config(state=tk.DISABLED)
            
            self.vba_blocker.restore_vba()
            
            self.status_label.config(text="VBA가 복원되었습니다.")
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, "VBA가 성공적으로 복원되었습니다.\n")
            self.log_text.config(state=tk.DISABLED)
            
            messagebox.showinfo("성공", "VBA가 성공적으로 복원되었습니다.")
            
        except Exception as e:
            self.status_label.config(text="오류 발생")
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, f"오류 발생: {str(e)}\n")
            self.log_text.config(state=tk.DISABLED)
            
            messagebox.showerror("오류", f"VBA 복원 중 오류가 발생했습니다:\n{str(e)}")
    
    def run(self):
        self.root.mainloop() 