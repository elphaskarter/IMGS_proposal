# -*- coding: UTF -8 -*-
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QFileDialog, QTextEdit, QHBoxLayout)

class MODTRAN_GUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        button_layout = QHBoxLayout()
        self.load_button = QPushButton('Load TAPE5 File', self)
        self.load_button.clicked.connect(self.load_file)
        button_layout.addWidget(self.load_button)
        
        self.save_button = QPushButton('Save Changes', self)
        self.save_button.clicked.connect(self.save_file)
        button_layout.addWidget(self.save_button)
        
        self.exit_button = QPushButton('Exit', self)
        self.exit_button.clicked.connect(self.close)
        button_layout.addWidget(self.exit_button)
        
        layout.addLayout(button_layout)
        
        self.text_area = QTextEdit(self)
        self.text_area.setFontFamily("Courier")  # Preserve character alignment
        layout.addWidget(self.text_area)
        
        self.setLayout(layout)
        self.setWindowTitle('MODTRAN TAPE5 Editor')
        self.setGeometry(200, 200, 600, 400)
    
    def load_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open TAPE5 File', '', 'Text Files (*.tp5);;All Files (*)', options=options)
        if file_name:
            with open(file_name, 'r') as file:
                self.text_area.setText(file.read())
    
    def save_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, 'Save TAPE5 File', '', 'Text Files (*.tp5);;All Files (*)', options=options)
        if file_name:
            with open(file_name, 'w') as file:
                file.write(self.text_area.toPlainText())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MODTRAN_GUI()
    ex.show()
    sys.exit(app.exec_())
