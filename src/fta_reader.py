import pandas as pd
import qrcode
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QFileDialog,
)
from PyQt5.QtGui import QPixmap, QIcon
import os

class FTAReader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FTA Reader with QR Code")
        self.setGeometry(100, 100, 800, 600)  # Ensure the window is properly sized

        # Set window icon
        self.setWindowIcon(QIcon("assets/logo.png"))

        # UI Components
        self.status_label = QLabel("Status: Ready")
        self.table = QTableWidget(10, 3)  # 3 columns for reading_id, pressure_level, timestamp
        self.connect_button = QPushButton("Connect to FTA")
        self.read_button = QPushButton("Read Data")
        self.quit_button = QPushButton("Quit")
        self.qr_code_label = QLabel("QR Code will appear here")
        self.qr_code_label.setScaledContents(True)
        self.qr_code_label.setFixedSize(200, 200)

        # Set table column headers
        self.table.setHorizontalHeaderLabels(["Reading ID", "Pressure Level", "Timestamp"])

        # Layout configuration
        main_layout = QVBoxLayout()

        # Status Label Layout
        status_layout = QHBoxLayout()
        status_layout.addWidget(self.status_label)
        main_layout.addLayout(status_layout)

        # Table and QR Code Layout
        data_layout = QHBoxLayout()
        data_layout.addWidget(self.table)
        data_layout.addWidget(self.qr_code_label)
        main_layout.addLayout(data_layout)

        # Buttons Layout (stacked vertically)
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.connect_button)
        button_layout.addWidget(self.read_button)
        button_layout.addWidget(self.quit_button)
        main_layout.addLayout(button_layout)

        # Central Widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Apply green theme
        self.apply_green_theme()

        # Button Connections
        self.connect_button.clicked.connect(self.do_connect)
        self.read_button.clicked.connect(self.read_data)
        self.quit_button.clicked.connect(self.close)

    def apply_green_theme(self):
        # Green-themed stylesheet
        green_style = """
        QMainWindow {
            background-color: #e8f5e9;
        }
        QPushButton {
            background-color: #66bb6a;
            color: white;
            border-radius: 5px;
            padding: 10px;
        }
        QPushButton:hover {
            background-color: #4caf50;
        }
        QLabel {
            font-size: 14px;
            color: #2e7d32;
        }
        QTableWidget {
            background-color: #f1f8e9;
            gridline-color: #c5e1a5;
            color: #1b5e20;
        }
        QHeaderView::section {
            background-color: #aed581;
            color: #1b5e20;
            padding: 4px;
            border: 1px solid #c5e1a5;
        }
        """
        self.setStyleSheet(green_style)

    def do_connect(self):
        self.status_label.setText("Status: Connected")

    def read_data(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)", options=options)
        if file_path:
            try:
                data = pd.read_csv(file_path)
                self.populate_table(data)
                self.generate_qr_code(data)
                self.status_label.setText("Status: Data Loaded and QR Code Generated")
            except Exception as e:
                self.status_label.setText(f"Error: {str(e)}")

    def populate_table(self, data):
        self.table.setRowCount(len(data))
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Reading ID", "Pressure Level", "Timestamp"])

        for row_idx, row in data.iterrows():
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(row["reading_id"])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(row["pressure_level"])))
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(row["timestamp"])))

    def generate_qr_code(self, data):
        csv_string = data.to_csv(index=False)
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(csv_string)
        qr.make(fit=True)

        qr_img = qr.make_image(fill="black", back_color="white")
        temp_path = "temp_qr_code.png"
        qr_img.save(temp_path)

        pixmap = QPixmap(temp_path)
        self.qr_code_label.setPixmap(pixmap)
        os.remove(temp_path)

# Application Entry Point
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = FTAReader()
    window.show()
    sys.exit(app.exec_())
