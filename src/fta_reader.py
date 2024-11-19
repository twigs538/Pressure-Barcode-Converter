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
        self.setGeometry(100, 100, 800, 600)

        # Set window icon
        self.setWindowIcon(QIcon("assets/logo.png"))

        # UI Components
        self.status_label = QLabel("Status: Ready")
        self.table = QTableWidget(10, 3)  # 3 columns for reading_id, pressure_level, timestamp
        self.generate_qr_button = QPushButton("Generate QR")
        self.read_button = QPushButton("Read Data")
        self.clear_button = QPushButton("Clear")
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
        button_layout.addWidget(self.generate_qr_button)
        button_layout.addWidget(self.read_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.quit_button)
        main_layout.addLayout(button_layout)

        # Central Widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Apply green theme
        self.apply_green_theme()

        # Button Connections
        self.generate_qr_button.clicked.connect(self.generate_qr_from_table)
        self.read_button.clicked.connect(self.read_data)
        self.clear_button.clicked.connect(self.clear_data)
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
        row_count = len(data)
        self.table.setRowCount(row_count)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Reading ID", "Pressure Level", "Timestamp"])

        for row_idx, row in data.iterrows():
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(row["reading_id"])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(row["pressure_level"])))
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(row["timestamp"])))

        # Resize table to fit content dynamically
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

    def generate_qr_from_table(self):
        rows = self.table.rowCount()
        cols = self.table.columnCount()

        # Collect data from the table
        table_data = []
        for row in range(rows):
            row_data = []
            for col in range(cols):
                item = self.table.item(row, col)
                if item is not None:
                    row_data.append(item.text())
                else:
                    row_data.append("")  # Fill empty cells with empty strings
            if any(row_data):  # Ignore completely empty rows
                table_data.append(row_data)

        # Convert to DataFrame
        data = pd.DataFrame(table_data, columns=["reading_id", "pressure_level", "timestamp"])
        self.generate_qr_code(data)
        self.status_label.setText("Status: QR Code Generated from Table Data")

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

    def clear_data(self):
        # Clear table data
        self.table.clearContents()
        self.table.setRowCount(10)
        self.qr_code_label.clear()
        self.qr_code_label.setText("QR Code will appear here")
        self.status_label.setText("Status: Cleared")

# Application Entry Point
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = FTAReader()
    window.show()
    sys.exit(app.exec_())
