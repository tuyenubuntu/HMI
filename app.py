import sys
import snap7
from snap7.util import *
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, 
                             QHBoxLayout, QWidget, QGroupBox, QTextEdit, QDialog, 
                             QLineEdit, QFormLayout, QDialogButtonBox, QScrollArea, QGridLayout)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont

class ConnectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Device")
        self.setFixedSize(300, 250)

        layout = QFormLayout()

        self.plc_name = QLineEdit(self)
        self.plc_name.setText("S7-1214C")
        layout.addRow("PLC Name:", self.plc_name)

        self.ip_address = QLineEdit(self)
        self.ip_address.setText("127.0.0.1")
        layout.addRow("IP Address:", self.ip_address)

        self.rack = QLineEdit(self)
        self.rack.setText("0")
        layout.addRow("Rack:", self.rack)

        self.slot = QLineEdit(self)
        self.slot.setText("1")
        layout.addRow("Slot:", self.slot)

        self.num_inputs = QLineEdit(self)
        self.num_inputs.setText("10")
        layout.addRow("Number of Inputs:", self.num_inputs)

        self.num_outputs = QLineEdit(self)
        self.num_outputs.setText("10")
        layout.addRow("Number of Outputs:", self.num_outputs)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.setLayout(layout)

    def get_connection_info(self):
        return {
            "name": self.plc_name.text(),
            "ip": self.ip_address.text(),
            "rack": int(self.rack.text()),
            "slot": int(self.slot.text()),
            "inputs": int(self.num_inputs.text()),
            "outputs": int(self.num_outputs.text())
        }

class TagNameDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tag Name Configuration")
        self.setFixedSize(400, 500)

        self.parent = parent
        layout = QVBoxLayout()

        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        # Inputs
        input_group = QGroupBox("Inputs")
        input_layout = QFormLayout()
        self.input_tags = []
        for i in range(parent.connection_info["inputs"]):
            byte, bit = divmod(i, 8)
            addr = f"I{byte}.{bit}"
            addr_label = QLabel(addr, self)
            addr_label.setFont(QFont("Arial", 8))
            tag_input = QLineEdit(self)
            tag_input.setText(parent.input_tags.get(addr, ""))
            input_layout.addRow(addr_label, tag_input)
            self.input_tags.append((addr, tag_input))
        input_group.setLayout(input_layout)
        scroll_layout.addWidget(input_group)

        # Outputs
        output_group = QGroupBox("Outputs")
        output_layout = QFormLayout()
        self.output_tags = []
        for i in range(parent.connection_info["outputs"]):
            byte, bit = divmod(i, 8)
            addr = f"Q{byte}.{bit}"
            addr_label = QLabel(addr, self)
            addr_label.setFont(QFont("Arial", 8))
            tag_output = QLineEdit(self)
            tag_output.setText(parent.output_tags.get(addr, ""))
            output_layout.addRow(addr_label, tag_output)
            self.output_tags.append((addr, tag_output))
        output_group.setLayout(output_layout)
        scroll_layout.addWidget(output_group)

        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_tags(self):
        input_tags = {addr: tag.text() for addr, tag in self.input_tags if tag.text()}
        output_tags = {addr: tag.text() for addr, tag in self.output_tags if tag.text()}
        return input_tags, output_tags

class PLC_HMI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PLC HMI - Trực Quan")
        self.setGeometry(100, 100, 1000, 600)

        self.connection_info = {"inputs": 10, "outputs": 10}
        self.input_tags = {}
        self.output_tags = {}
        self.init_ui()

        self.plc = snap7.client.Client()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_status)
        self.timer.start(500)

    def connect_plc(self):
        if not self.connection_info or "ip" not in self.connection_info:
            self.log_message("Chưa có thông tin kết nối. Nhấn 'Add Device' để thiết lập.")
            return

        try:
            self.plc.connect(self.connection_info["ip"], 
                            self.connection_info["rack"], 
                            self.connection_info["slot"])
            if self.plc.get_connected():
                self.log_message(f"Kết nối {self.connection_info['name']} thành công!")
                self.update_plc_info()
            else:
                self.log_message("Kết nối thất bại!")
                self.update_plc_info()
        except Exception as e:
            self.log_message(f"Lỗi kết nối: {e}")
            self.update_plc_info()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout()

        header_layout = QHBoxLayout()
        self.title = QLabel("HMI Giám Sát PLC", self)
        self.title.setFont(QFont("Arial", 14, QFont.Bold))
        header_layout.addWidget(self.title)
        header_layout.addStretch()
        add_device_btn = QPushButton("Add Device", self)
        add_device_btn.setFont(QFont("Arial", 10))
        add_device_btn.clicked.connect(self.show_connection_dialog)
        header_layout.addWidget(add_device_btn)
        tag_name_btn = QPushButton("Tag Name", self)
        tag_name_btn.setFont(QFont("Arial", 10))
        tag_name_btn.clicked.connect(self.show_tag_name_dialog)
        header_layout.addWidget(tag_name_btn)
        self.main_layout.addLayout(header_layout)

        self.status_display = QTextEdit(self)
        self.status_display.setReadOnly(True)
        self.status_display.setFixedHeight(100)
        self.status_display.setFont(QFont("Arial", 10))
        self.main_layout.addWidget(self.status_display)

        self.io_container = QHBoxLayout()
        self.update_io_layout()
        self.main_layout.addLayout(self.io_container)

        self.central_widget.setLayout(self.main_layout)

    def get_last_address(self, count):
        if count <= 1:
            return "0.0"
        last_idx = count - 1
        byte = last_idx // 8
        bit = last_idx % 8
        return f"{byte}.{bit}"

    def update_io_layout(self):
        while self.io_container.count():
            item = self.io_container.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        # Inputs với thanh cuộn
        last_input = self.get_last_address(self.connection_info["inputs"])
        input_group = QGroupBox(f"Inputs (0.0 - {last_input})")
        input_group.setFixedWidth(200)  # Tăng chiều rộng lên 200px
        input_widget = QWidget()
        input_layout = QGridLayout()
        self.input_labels = []
        self.input_status_labels = []
        for i in range(self.connection_info["inputs"]):
            byte, bit = divmod(i, 8)
            addr = f"I{byte}.{bit}"
            tag = self.input_tags.get(addr, "")
            display_text = f"{addr} - {tag}" if tag else addr

            label = QLabel(display_text, self)
            label.setFont(QFont("Arial", 8))
            label.setFixedWidth(150)  # Tăng chiều rộng ô tag name
            label.setStyleSheet("border: 1px solid gray; padding: 2px;")
            self.input_labels.append(label)
            input_layout.addWidget(label, i, 0)

            status_label = QLabel("OFF", self)
            status_label.setFont(QFont("Arial", 8))
            status_label.setFixedWidth(40)
            status_label.setStyleSheet("border: 1px solid gray; padding: 2px; background-color: #F44336; color: white;")
            self.input_status_labels.append(status_label)
            input_layout.addWidget(status_label, i, 1)

        input_widget.setLayout(input_layout)
        input_scroll = QScrollArea()
        input_scroll.setWidget(input_widget)
        input_scroll.setWidgetResizable(True)
        input_group.setLayout(QVBoxLayout())
        input_group.layout().addWidget(input_scroll)
        self.io_container.addWidget(input_group)

        # Outputs với thanh cuộn
        last_output = self.get_last_address(self.connection_info["outputs"])
        output_group = QGroupBox(f"Outputs (0.0 - {last_output})")
        output_group.setFixedWidth(250)  # Tăng chiều rộng lên 250px
        output_widget = QWidget()
        output_layout = QGridLayout()
        self.output_labels = []
        self.output_status_labels = []
        self.output_buttons = []
        for i in range(self.connection_info["outputs"]):
            byte, bit = divmod(i, 8)
            addr = f"Q{byte}.{bit}"
            tag = self.output_tags.get(addr, "")
            display_text = f"{addr} - {tag}" if tag else addr

            label = QLabel(display_text, self)
            label.setFont(QFont("Arial", 8))
            label.setFixedWidth(150)  # Tăng chiều rộng ô tag name
            label.setStyleSheet("border: 1px solid gray; padding: 2px;")
            self.output_labels.append(label)
            output_layout.addWidget(label, i, 0)

            status_label = QLabel("OFF", self)
            status_label.setFont(QFont("Arial", 8))
            status_label.setFixedWidth(40)
            status_label.setStyleSheet("border: 1px solid gray; padding: 2px; background-color: #F44336; color: white;")
            self.output_status_labels.append(status_label)
            output_layout.addWidget(status_label, i, 1)

            button = QPushButton("T", self)
            button.setFont(QFont("Arial", 7))
            button.setFixedWidth(20)
            button.setStyleSheet("background-color: #4CAF50; color: white; padding: 2px;")
            button.clicked.connect(lambda checked, b=byte, i=bit: self.toggle_output(b, i))
            self.output_buttons.append(button)
            output_layout.addWidget(button, i, 2)

        output_widget.setLayout(output_layout)
        output_scroll = QScrollArea()
        output_scroll.setWidget(output_widget)
        output_scroll.setWidgetResizable(True)
        output_group.setLayout(QVBoxLayout())
        output_group.layout().addWidget(output_scroll)
        self.io_container.addWidget(output_group)

        # Thêm layout PLC Info
        self.plc_info_group = QGroupBox("PLC Info")
        self.plc_info_group.setFixedWidth(200)  # Tăng chiều rộng lên 200px
        self.plc_info_widget = QWidget()
        self.plc_info_layout = QVBoxLayout()
        
        self.plc_name_label = QLabel("PLC Name: N/A")
        self.plc_name_label.setFont(QFont("Arial", 8))
        self.plc_name_label.setStyleSheet("border: 1px solid gray; padding: 2px;")
        self.plc_info_layout.addWidget(self.plc_name_label)

        self.plc_ip_label = QLabel("IP: N/A")
        self.plc_ip_label.setFont(QFont("Arial", 8))
        self.plc_ip_label.setStyleSheet("border: 1px solid gray; padding: 2px;")
        self.plc_info_layout.addWidget(self.plc_ip_label)

        self.plc_rack_slot_label = QLabel("Rack/Slot: N/A")
        self.plc_rack_slot_label.setFont(QFont("Arial", 8))
        self.plc_rack_slot_label.setStyleSheet("border: 1px solid gray; padding: 2px;")
        self.plc_info_layout.addWidget(self.plc_rack_slot_label)

        self.plc_inputs_label = QLabel("Number of Inputs: N/A")
        self.plc_inputs_label.setFont(QFont("Arial", 8))
        self.plc_inputs_label.setStyleSheet("border: 1px solid gray; padding: 2px;")
        self.plc_info_layout.addWidget(self.plc_inputs_label)

        self.plc_outputs_label = QLabel("Number of Outputs: N/A")
        self.plc_outputs_label.setFont(QFont("Arial", 8))
        self.plc_outputs_label.setStyleSheet("border: 1px solid gray; padding: 2px;")
        self.plc_info_layout.addWidget(self.plc_outputs_label)

        self.plc_status_label = QLabel("Status: Offline")
        self.plc_status_label.setFont(QFont("Arial", 8))
        self.plc_status_label.setStyleSheet("border: 1px solid gray; padding: 2px; background-color: #F44336; color: white;")
        self.plc_info_layout.addWidget(self.plc_status_label)

        self.plc_info_layout.addStretch()
        self.plc_info_widget.setLayout(self.plc_info_layout)

        plc_info_scroll = QScrollArea()
        plc_info_scroll.setWidget(self.plc_info_widget)
        plc_info_scroll.setWidgetResizable(True)
        self.plc_info_group.setLayout(QVBoxLayout())
        self.plc_info_group.layout().addWidget(plc_info_scroll)
        self.io_container.addWidget(self.plc_info_group)

        self.io_container.addStretch()

    def update_plc_info(self):
        if "name" in self.connection_info:
            self.title.setText(f"HMI Giám Sát {self.connection_info['name']}")
            self.plc_name_label.setText(f"PLC Name: {self.connection_info['name']}")
            self.plc_ip_label.setText(f"IP: {self.connection_info['ip']}")
            self.plc_rack_slot_label.setText(f"Rack/Slot: {self.connection_info['rack']}/{self.connection_info['slot']}")
            self.plc_inputs_label.setText(f"Number of Inputs: {self.connection_info['inputs']}")
            self.plc_outputs_label.setText(f"Number of Outputs: {self.connection_info['outputs']}")
        else:
            self.title.setText("HMI Giám Sát PLC")
            self.plc_name_label.setText("PLC Name: N/A")
            self.plc_ip_label.setText("IP: N/A")
            self.plc_rack_slot_label.setText("Rack/Slot: N/A")
            self.plc_inputs_label.setText("Number of Inputs: N/A")
            self.plc_outputs_label.setText("Number of Outputs: N/A")

        if self.plc.get_connected():
            self.plc_status_label.setText("Status: Online")
            self.plc_status_label.setStyleSheet("border: 1px solid gray; padding: 2px; background-color: #4CAF50; color: white;")
        else:
            self.plc_status_label.setText("Status: Offline")
            self.plc_status_label.setStyleSheet("border: 1px solid gray; padding: 2px; background-color: #F44336; color: white;")

    def show_connection_dialog(self):
        dialog = ConnectionDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.connection_info = dialog.get_connection_info()
            self.input_tags.clear()
            self.output_tags.clear()
            self.update_io_layout()
            self.connect_plc()

    def show_tag_name_dialog(self):
        dialog = TagNameDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.input_tags, self.output_tags = dialog.get_tags()
            self.update_io_layout()

    def log_message(self, message):
        if hasattr(self, 'status_display'):
            current_text = self.status_display.toPlainText()
            self.status_display.setText(f"{current_text}\n{message}")
            self.status_display.verticalScrollBar().setValue(
                self.status_display.verticalScrollBar().maximum()
            )

    def update_status(self):
        if self.plc.get_connected() and "ip" in self.connection_info:
            self.status_display.setStyleSheet("background-color: #4CAF50; color: white;")
            if "Connected" not in self.status_display.toPlainText().split("\n")[-1]:
                self.log_message("Connected")

            num_input_bytes = (self.connection_info["inputs"] + 7) // 8
            input_data = self.plc.read_area(snap7.types.S7AreaPE, 0, 0, num_input_bytes)
            for i in range(self.connection_info["inputs"]):
                byte, bit = divmod(i, 8)
                addr = f"I{byte}.{bit}"
                tag = self.input_tags.get(addr, "")
                display_text = f"{addr} - {tag}" if tag else addr
                status = get_bool(input_data, byte, bit)
                text = "ON" if status else "OFF"
                color = "background-color: #4CAF50;" if status else "background-color: #F44336;"
                self.input_labels[i].setText(display_text)
                self.input_status_labels[i].setText(text)
                self.input_status_labels[i].setStyleSheet(f"{color} border: 1px solid gray; padding: 2px; color: white;")

            num_output_bytes = (self.connection_info["outputs"] + 7) // 8
            output_data = self.plc.read_area(snap7.types.S7AreaPA, 0, 0, num_output_bytes)
            for i in range(self.connection_info["outputs"]):
                byte, bit = divmod(i, 8)
                addr = f"Q{byte}.{bit}"
                tag = self.output_tags.get(addr, "")
                display_text = f"{addr} - {tag}" if tag else addr
                status = get_bool(output_data, byte, bit)
                text = "ON" if status else "OFF"
                color = "background-color: #4CAF50;" if status else "background-color: #F44336;"
                self.output_labels[i].setText(display_text)
                self.output_status_labels[i].setText(text)
                self.output_status_labels[i].setStyleSheet(f"{color} border: 1px solid gray; padding: 2px; color: white;")
        else:
            self.status_display.setStyleSheet("background-color: #F44336; color: white;")
            if "Disconnected" not in self.status_display.toPlainText().split("\n")[-1]:
                self.log_message("Disconnected")
        self.update_plc_info()

    def toggle_output(self, byte, bit):
        if self.plc.get_connected():
            num_output_bytes = (self.connection_info["outputs"] + 7) // 8
            data = self.plc.read_area(snap7.types.S7AreaPA, 0, 0, num_output_bytes)
            current_state = get_bool(data, byte, bit)
            new_data = bytearray(num_output_bytes)
            for i in range(num_output_bytes):
                new_data[i] = data[i]
            set_bool(new_data, byte, bit, not current_state)
            self.plc.write_area(snap7.types.S7AreaPA, 0, 0, new_data)
            addr = f"Q{byte}.{bit}"
            tag = self.output_tags.get(addr, addr)
            self.log_message(f"Đã thay đổi {tag} thành {not current_state}")
        else:
            self.log_message("Không thể thay đổi: PLC chưa kết nối")

    def closeEvent(self, event):
        if self.plc.get_connected():
            self.plc.disconnect()
            self.log_message("Đã ngắt kết nối PLC")
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PLC_HMI()
    window.show()
    sys.exit(app.exec_())