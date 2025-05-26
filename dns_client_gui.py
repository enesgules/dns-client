#!/usr/bin/env python3
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QLineEdit, QPushButton, QLabel, QListWidget, QFrame)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont
from dns_client import dns_lookup

class DNSLookupThread(QThread):
    """Thread for performing DNS lookups without freezing the GUI"""
    finished = Signal(list, int)
    error = Signal(str)

    def __init__(self, domain):
        super().__init__()
        self.domain = domain

    def run(self):
        try:
            ip_addresses, query_time = dns_lookup(self.domain)
            self.finished.emit(ip_addresses, query_time)
        except Exception as e:
            self.error.emit(str(e))

class StyledLineEdit(QLineEdit):
    def __init__(self, placeholder=""):
        super().__init__()
        self.setPlaceholderText(placeholder)
        self.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                background-color: white;
                color: #2C3E50;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #3498DB;
            }
        """)

class StyledButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QPushButton:pressed {
                background-color: #2472A4;
            }
            QPushButton:disabled {
                background-color: #BDC3C7;
            }
        """)

class StyledListWidget(QListWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                padding: 8px;
                color: #2C3E50;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #E0E0E0;
            }
            QListWidget::item:selected {
                background-color: #EBF5FB;
                color: #2C3E50;
            }
        """)

class DNSClientGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DNS Lookup")
        self.setMinimumSize(500, 600)
        self.setup_ui()

    def setup_ui(self):
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        # Title
        title = QLabel("DNS Lookup")
        title.setFont(QFont("SF Pro Display", 32, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2C3E50; margin-bottom: 20px;")
        layout.addWidget(title)

        # Input container
        input_container = QFrame()
        input_container.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        input_layout = QVBoxLayout(input_container)
        input_layout.setSpacing(15)

        # Domain input
        self.domain_input = StyledLineEdit("Enter domain name (e.g., google.com)")
        input_layout.addWidget(self.domain_input)

        # Lookup button
        self.lookup_button = StyledButton("Lookup")
        self.lookup_button.clicked.connect(self.perform_lookup)
        input_layout.addWidget(self.lookup_button)

        layout.addWidget(input_container)

        # Results container
        results_container = QFrame()
        results_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        results_layout = QVBoxLayout(results_container)
        results_layout.setSpacing(15)

        # Results label
        self.results_label = QLabel("Results will appear here")
        self.results_label.setFont(QFont("SF Pro Text", 14))
        self.results_label.setAlignment(Qt.AlignCenter)
        self.results_label.setStyleSheet("color: #7F8C8D;")
        results_layout.addWidget(self.results_label)

        # IP addresses list
        self.ip_list = StyledListWidget()
        results_layout.addWidget(self.ip_list)

        # Query time label
        self.query_time_label = QLabel("")
        self.query_time_label.setFont(QFont("SF Pro Text", 12))
        self.query_time_label.setAlignment(Qt.AlignCenter)
        self.query_time_label.setStyleSheet("color: #7F8C8D;")
        results_layout.addWidget(self.query_time_label)

        layout.addWidget(results_container)

        # Set window background
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F8F9FA;
            }
        """)

    def perform_lookup(self):
        """Perform DNS lookup when the button is clicked"""
        domain = self.domain_input.text().strip()
        if not domain:
            self.results_label.setText("Please enter a domain name")
            self.results_label.setStyleSheet("color: #E74C3C;")
            return

        # Clear previous results
        self.ip_list.clear()
        self.query_time_label.clear()
        self.results_label.setText("Looking up...")
        self.results_label.setStyleSheet("color: #3498DB;")
        self.lookup_button.setEnabled(False)

        # Create and start lookup thread
        self.lookup_thread = DNSLookupThread(domain)
        self.lookup_thread.finished.connect(self.handle_results)
        self.lookup_thread.error.connect(self.handle_error)
        self.lookup_thread.start()

    def handle_results(self, ip_addresses, query_time):
        """Handle successful DNS lookup results"""
        self.lookup_button.setEnabled(True)
        self.results_label.setText(f"Found {len(ip_addresses)} IP address(es):")
        self.results_label.setStyleSheet("color: #27AE60;")
        
        # Add IP addresses to the list
        for ip in ip_addresses:
            self.ip_list.addItem(ip)
        
        # Show query time
        self.query_time_label.setText(f"Query time: {query_time} ms")
        self.query_time_label.setStyleSheet("color: #7F8C8D;")

    def handle_error(self, error_message):
        """Handle DNS lookup errors"""
        self.lookup_button.setEnabled(True)
        self.results_label.setText("Error occurred")
        self.results_label.setStyleSheet("color: #E74C3C;")
        self.ip_list.clear()
        self.ip_list.addItem(f"Error: {error_message}")
        self.query_time_label.clear()

def main():
    app = QApplication(sys.argv)
    
    # Set application-wide font
    app.setFont(QFont("SF Pro Text", 12))
    
    window = DNSClientGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 