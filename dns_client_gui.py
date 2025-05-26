#!/usr/bin/env python3
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QLineEdit, QPushButton, QLabel, QListWidget)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QPalette, QColor
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

class DNSClientGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DNS Client")
        self.setMinimumSize(400, 500)
        self.setup_ui()

    def setup_ui(self):
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Title
        title = QLabel("DNS Lookup")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Domain input
        self.domain_input = QLineEdit()
        self.domain_input.setPlaceholderText("Enter domain name (e.g., google.com)")
        self.domain_input.setFont(QFont("Arial", 12))
        self.domain_input.setMinimumHeight(40)
        layout.addWidget(self.domain_input)

        # Lookup button
        self.lookup_button = QPushButton("Lookup")
        self.lookup_button.setFont(QFont("Arial", 12))
        self.lookup_button.setMinimumHeight(40)
        self.lookup_button.clicked.connect(self.perform_lookup)
        layout.addWidget(self.lookup_button)

        # Results label
        self.results_label = QLabel("Results will appear here")
        self.results_label.setFont(QFont("Arial", 12))
        self.results_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.results_label)

        # IP addresses list
        self.ip_list = QListWidget()
        self.ip_list.setFont(QFont("Arial", 12))
        layout.addWidget(self.ip_list)

        # Query time label
        self.query_time_label = QLabel("")
        self.query_time_label.setFont(QFont("Arial", 12))
        self.query_time_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.query_time_label)

        # Set dark theme
        self.set_dark_theme()

    def set_dark_theme(self):
        """Apply a dark theme to the application"""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)

        self.setPalette(palette)

    def perform_lookup(self):
        """Perform DNS lookup when the button is clicked"""
        domain = self.domain_input.text().strip()
        if not domain:
            self.results_label.setText("Please enter a domain name")
            return

        # Clear previous results
        self.ip_list.clear()
        self.query_time_label.clear()
        self.results_label.setText("Looking up...")
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
        
        # Add IP addresses to the list
        for ip in ip_addresses:
            self.ip_list.addItem(ip)
        
        # Show query time
        self.query_time_label.setText(f"Query time: {query_time} ms")

    def handle_error(self, error_message):
        """Handle DNS lookup errors"""
        self.lookup_button.setEnabled(True)
        self.results_label.setText("Error occurred")
        self.ip_list.clear()
        self.ip_list.addItem(f"Error: {error_message}")
        self.query_time_label.clear()

def main():
    app = QApplication(sys.argv)
    window = DNSClientGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 