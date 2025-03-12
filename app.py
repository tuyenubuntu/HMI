import os
import sys
import snap7
from snap7.util import *  # Import các hàm tiện ích của snap7 (get_bool, set_bool, v.v.)
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, 
                             QHBoxLayout, QWidget, QGroupBox, QTextEdit, QDialog, 
                             QLineEdit, QFormLayout, QDialogButtonBox, QScrollArea, QGridLayout, QSizePolicy)
from PyQt5.QtCore import QTimer, Qt  # QtCore cho timer và các thuộc tính Qt
from PyQt5.QtGui import QFont, QIcon, QPixmap  # QtGui cho font, icon, và hình ảnh
import time  # Sử dụng để delay trong kết nối
from datetime import datetime  # Sử dụng để ghi log với timestamp

# Line 1-13: Import các thư viện cần thiết

class ConnectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Device")  # Đặt tiêu đề cho dialog
        self.setFixedSize(300, 250)  # Kích thước cố định của dialog (300x250 pixel)

        layout = QFormLayout()  # Layout dạng form để sắp xếp các trường nhập liệu

        self.plc_name = QLineEdit(self)
        self.plc_name.setText("S7-1214C")  # Giá trị mặc định cho tên PLC
        layout.addRow("PLC Name:", self.plc_name)

        self.ip_address = QLineEdit(self)
        self.ip_address.setText("192.168.0.1")  # Giá trị mặc định cho IP
        layout.addRow("IP Address:", self.ip_address)

        self.rack = QLineEdit(self)
        self.rack.setText("0")  # Giá trị mặc định cho rack
        layout.addRow("Rack:", self.rack)

        self.slot = QLineEdit(self)
        self.slot.setText("1")  # Giá trị mặc định cho slot
        layout.addRow("Slot:", self.slot)

        self.num_inputs = QLineEdit(self)
        self.num_inputs.setText("10")  # Số lượng inputs mặc định
        layout.addRow("Number of Inputs:", self.num_inputs)

        self.num_outputs = QLineEdit(self)
        self.num_outputs.setText("10")  # Số lượng outputs mặc định
        layout.addRow("Number of Outputs:", self.num_outputs)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)  # Nút OK và Cancel
        buttons.accepted.connect(self.accept)  # Xử lý khi nhấn OK
        buttons.rejected.connect(self.reject)  # Xử lý khi nhấn Cancel
        layout.addRow(buttons)

        self.setLayout(layout)  # Áp dụng layout cho dialog

    # Line 15-48: Class ConnectionDialog - Hiển thị dialog để nhập thông tin kết nối PLC

    def get_connection_info(self):
        return {
            "name": self.plc_name.text(),
            "ip": self.ip_address.text(),
            "rack": int(self.rack.text()),  # Chuyển rack thành số nguyên
            "slot": int(self.slot.text()),  # Chuyển slot thành số nguyên
            "inputs": int(self.num_inputs.text()),  # Chuyển số inputs thành số nguyên
            "outputs": int(self.num_outputs.text())  # Chuyển số outputs thành số nguyên
        }
    # Line 50-62: Phương thức get_connection_info - Trả về thông tin kết nối dưới dạng dictionary

class TagNameDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tag Name Configuration")  # Tiêu đề dialog cấu hình tag
        self.setFixedSize(400, 500)  # Kích thước cố định (400x500 pixel)

        self.parent = parent  # Lưu tham chiếu đến cửa sổ chính
        layout = QVBoxLayout()

        scroll = QScrollArea()  # Sử dụng scroll area để cuộn khi có nhiều tag
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        input_group = QGroupBox("Inputs")  # Nhóm cho inputs
        input_layout = QFormLayout()
        self.input_tags = []  # Danh sách lưu các cặp (địa chỉ, ô nhập liệu) cho inputs
        for i in range(parent.connection_info["inputs"]):  # Lặp qua số lượng inputs
            byte, bit = divmod(i, 8)  # Tách thành byte và bit
            addr = f"I{byte}.{bit}"  # Tạo địa chỉ (ví dụ: I0.0)
            addr_label = QLabel(addr, self)
            addr_label.setFont(QFont("Arial", 8))
            tag_input = QLineEdit(self)
            tag_input.setText(parent.input_tags.get(addr, ""))  # Lấy giá trị tag cũ nếu có
            input_layout.addRow(addr_label, tag_input)
            self.input_tags.append((addr, tag_input))
        input_group.setLayout(input_layout)
        scroll_layout.addWidget(input_group)

        output_group = QGroupBox("Outputs")  # Nhóm cho outputs
        output_layout = QFormLayout()
        self.output_tags = []  # Danh sách lưu các cặp (địa chỉ, ô nhập liệu) cho outputs
        for i in range(parent.connection_info["outputs"]):  # Lặp qua số lượng outputs
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
        scroll.setWidgetResizable(True)  # Cho phép widget bên trong co giãn để cuộn
        layout.addWidget(scroll)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    # Line 64-113: Class TagNameDialog - Hiển thị dialog để cấu hình tên tag cho inputs và outputs

    def get_tags(self):
        input_tags = {addr: tag.text() for addr, tag in self.input_tags if tag.text().strip()}  # Lấy tag inputs hợp lệ
        output_tags = {addr: tag.text() for addr, tag in self.output_tags if tag.text().strip()}  # Lấy tag outputs hợp lệ
        if not input_tags and not output_tags:
            self.parent.log_message("Warning: No tags have been entered!")  # Cảnh báo nếu không có tag
        return input_tags, output_tags
    # Line 115-123: Phương thức get_tags - Trả về dictionary chứa các tag inputs và outputs

class PLC_HMI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PLC HMI - Visualization")  # Tiêu đề cửa sổ chính
        self.setGeometry(100, 100, 750, 750)  # Vị trí và kích thước ban đầu (x, y, width, height)

        # Thiết lập biểu tượng cho cửa sổ
        self.setWindowIcon(QIcon("shortcut/images/icon3.ico"))  # Đường dẫn đến icon, cần chỉnh sửa nếu khác
        # Note: Đảm bảo file icon3.ico tồn tại trong shortcut/images/, nếu không thay thế bằng đường dẫn đúng

        self.connection_info = {"name": "S7-1214C", "ip": "192.168.0.1", "rack": 0, "slot": 1, "inputs": 10, "outputs": 10}
        self.input_tags = {}  # Dictionary lưu tag cho inputs
        self.output_tags = {}  # Dictionary lưu tag cho outputs
        self.init_ui()  # Khởi tạo giao diện

        self.plc = snap7.client.Client()  # Khởi tạo client snap7 để kết nối PLC

        self.timer = QTimer(self)  # Timer để cập nhật trạng thái định kỳ
        self.timer.timeout.connect(self.update_status)  # Kết nối timer với hàm update_status
        self.timer.start(500)  # Chạy timer mỗi 500ms
        # Note: Có thể điều chỉnh 500ms thành giá trị khác nếu cần tối ưu hiệu suất

        self.create_log_file()  # Tạo file log

    # Line 125-149: Phương thức __init__ - Khởi tạo cửa sổ chính và các thành phần cơ bản

    def create_log_file(self):
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # Lấy thời gian hiện tại
        log_folder = "log\\"  # Thư mục lưu log
        if not os.path.exists(log_folder):  # Kiểm tra và tạo thư mục nếu chưa tồn tại
            os.makedirs(log_folder)
        self.log_filename = log_folder + f"log_{current_time}.txt"  # Tên file log với timestamp
        with open(self.log_filename, 'a') as f:  # Mở file log ở chế độ append
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Application started.\n")
    # Line 151-160: Phương thức create_log_file - Tạo và khởi tạo file log

    def connect_plc(self, max_attempts=3, delay=2):
        self.log_message("Button 'Connect' clicked. Attempting to connect...")
        if not self.connection_info or "ip" not in self.connection_info:
            self.log_message("No connection information available. Press 'Add Device' to configure.")
            return

        if self.plc.get_connected():  # Kiểm tra nếu đã kết nối
            self.plc.disconnect()  # Ngắt kết nối hiện tại
            self.log_message("Disconnecting current connection to retry...")

        for attempt in range(max_attempts):  # Thử kết nối tối đa max_attempts lần
            try:
                self.log_message(f"Attempting to connect to {self.connection_info['ip']} (Attempt {attempt + 1}/{max_attempts})...")
                self.plc.connect(self.connection_info["ip"], self.connection_info["rack"], self.connection_info["slot"])
                if self.plc.get_connected():
                    self.log_message(f"Connection to {self.connection_info['name']} successful!")
                    self.update_plc_info()
                    return
                else:
                    self.log_message(f"Connection attempt {attempt + 1} failed...")
            except Exception as e:  # Bắt mọi lỗi để log
                self.log_message(f"Connection error (attempt {attempt + 1}): {str(e)}")
            time.sleep(delay)  # Đợi delay giây trước khi thử lại
        self.log_message("Connection failed after multiple attempts!")
        self.update_plc_info()
    # Line 162-188: Phương thức connect_plc - Thử kết nối với PLC với retry logic
    # Note: Nếu thất bại, kiểm tra IP, snap7.dll, và cấu hình PLC/PLCSIM

    def init_ui(self):
        self.central_widget = QWidget()  # Widget trung tâm chứa toàn bộ giao diện
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout()  # Layout dọc chính

        header_layout = QHBoxLayout()  # Layout ngang cho header

        # Thêm logo vào giao diện
        logo_label = QLabel(self)
        pixmap = QPixmap("shortcut/images/logo.png")  # Đường dẫn đến logo
        if not pixmap.isNull():  # Kiểm tra logo có tồn tại không
            # Điều chỉnh kích thước logo (100x50 pixel)
            pixmap = pixmap.scaled(100, 50, Qt.KeepAspectRatio)
            logo_label.setPixmap(pixmap)
        else:
            logo_label.setText("Logo not found!")  # Thông báo nếu logo không tìm thấy
        header_layout.addWidget(logo_label)

        self.title = QLabel("PLC HMI Monitoring", self)
        self.title.setFont(QFont("Arial", 14, QFont.Bold))
        header_layout.addWidget(self.title)
        header_layout.addStretch()  # Đẩy các nút sang bên phải

        add_device_btn = QPushButton("Add Device", self)
        add_device_btn.setFont(QFont("Arial", 10))
        add_device_btn.clicked.connect(self.show_connection_dialog)
        header_layout.addWidget(add_device_btn)

        tag_name_btn = QPushButton("Tag Name", self)
        tag_name_btn.setFont(QFont("Arial", 10))
        tag_name_btn.clicked.connect(self.show_tag_name_dialog)
        header_layout.addWidget(tag_name_btn)

        refresh_btn = QPushButton("Refresh", self)
        refresh_btn.setFont(QFont("Arial", 10))
        refresh_btn.clicked.connect(self.refresh_connection)
        header_layout.addWidget(refresh_btn)

        connect_btn = QPushButton("Connect", self)
        connect_btn.setFont(QFont("Arial", 10))
        connect_btn.clicked.connect(self.connect_plc)
        header_layout.addWidget(connect_btn)

        clear_btn = QPushButton("Clear", self)
        clear_btn.setFont(QFont("Arial", 10))
        clear_btn.clicked.connect(self.clear_log)
        header_layout.addWidget(clear_btn)

        self.main_layout.addLayout(header_layout)

        self.status_display = QTextEdit(self)
        self.status_display.setReadOnly(True)  # Chỉ đọc, không cho chỉnh sửa
        self.status_display.setFixedHeight(100)  # Chiều cao cố định cho log
        self.status_display.setFont(QFont("Arial", 10))
        self.main_layout.addWidget(self.status_display)

        self.io_container = QHBoxLayout()  # Layout ngang cho Inputs, Outputs, PLC Info
        self.update_io_layout()  # Cập nhật layout cho các nhóm I/O
        self.main_layout.addLayout(self.io_container)

        self.central_widget.setLayout(self.main_layout)
    # Line 190-243: Phương thức init_ui - Khởi tạo giao diện chính
    # Note: Đảm bảo các file logo và icon tồn tại, nếu không thay đổi đường dẫn

    def refresh_connection(self):
        self.log_message("Button 'Refresh' clicked. Refreshing connection...")
        self.connect_plc()
    # Line 245-250: Phương thức refresh_connection - Gọi lại connect_plc khi nhấn Refresh

    def clear_log(self):
        self.status_display.clear()  # Xóa nội dung log trên giao diện
        self.log_message("Button 'Clear' clicked. Log has been cleared!")
    # Line 252-256: Phương thức clear_log - Xóa log và ghi thông báo

    def get_last_address(self, count):
        if count <= 1:
            return "0.0"
        last_idx = count - 1
        byte = last_idx // 8
        bit = last_idx % 8
        return f"{byte}.{bit}"
    # Line 258-265: Phương thức get_last_address - Tạo địa chỉ cuối cùng dựa trên số lượng
    # Note: Sử dụng để hiển thị phạm vi địa chỉ (0.0 - cuối cùng)

    def update_io_layout(self):
        while self.io_container.count():  # Xóa các widget cũ trong io_container
            item = self.io_container.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        # Input Group
        last_input = self.get_last_address(self.connection_info["inputs"])
        input_group = QGroupBox(f"Inputs (0.0 - {last_input})")
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
            label.setFixedWidth(140)  # Chiều rộng cố định
            label.setFixedHeight(20)  # Chiều cao cố định cho mỗi dòng
            label.setStyleSheet("border: 1px solid gray; padding: 2px;")
            label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)  # Ngăn giãn chiều Y
            self.input_labels.append(label)
            input_layout.addWidget(label, i, 0)

            status_label = QLabel("OFF", self)
            status_label.setFont(QFont("Arial", 8))
            status_label.setFixedWidth(40)  # Chiều rộng cố định
            status_label.setFixedHeight(20)  # Chiều cao cố định
            status_label.setStyleSheet("border: 1px solid gray; padding: 2px; background-color: #F44336; color: white;")
            status_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)  # Ngăn giãn chiều Y
            self.input_status_labels.append(status_label)
            input_layout.addWidget(status_label, i, 1)

        input_layout.setVerticalSpacing(2)  # Khoảng cách giữa các hàng
        input_widget.setLayout(input_layout)
        input_scroll = QScrollArea()
        input_scroll.setWidget(input_widget)
        input_scroll.setWidgetResizable(True)  # Cho phép cuộn nhưng không giãn chiều cao
        input_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        input_scroll.setMinimumHeight(200)  # Chiều cao tối thiểu cố định
        input_scroll.setMaximumHeight(400)  # Chiều cao tối đa để giới hạn giãn
        input_group.setLayout(QVBoxLayout())
        input_group.layout().addWidget(input_scroll)
        self.io_container.addWidget(input_group)
        self.io_container.setStretch(self.io_container.count() - 1, 1)  # Stretch factor 1

        # Output Group
        last_output = self.get_last_address(self.connection_info["outputs"])
        output_group = QGroupBox(f"Outputs (0.0 - {last_output})")
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
            label.setFixedWidth(150)
            label.setFixedHeight(20)  # Chiều cao cố định
            label.setStyleSheet("border: 1px solid gray; padding: 2px;")
            label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)  # Ngăn giãn chiều Y
            self.output_labels.append(label)
            output_layout.addWidget(label, i, 0)

            status_label = QLabel("OFF", self)
            status_label.setFont(QFont("Arial", 8))
            status_label.setFixedWidth(40)
            status_label.setFixedHeight(20)  # Chiều cao cố định
            status_label.setStyleSheet("border: 1px solid gray; padding: 2px; background-color: #F44336; color: white;")
            status_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)  # Ngăn giãn chiều Y
            self.output_status_labels.append(status_label)
            output_layout.addWidget(status_label, i, 1)

            button = QPushButton("T", self)
            button.setFont(QFont("Arial", 7))
            button.setFixedWidth(20)
            button.setFixedHeight(20)  # Chiều cao cố định
            button.setStyleSheet("background-color: #4CAF50; color: white; padding: 2px;")
            button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)  # Ngăn giãn chiều Y
            button.clicked.connect(lambda checked, b=byte, i=bit: self.toggle_output(b, i))
            self.output_buttons.append(button)
            output_layout.addWidget(button, i, 2)

        output_layout.setVerticalSpacing(2)  # Khoảng cách giữa các hàng
        output_widget.setLayout(output_layout)
        output_scroll = QScrollArea()
        output_scroll.setWidget(output_widget)
        output_scroll.setWidgetResizable(True)
        output_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        output_scroll.setMinimumHeight(200)  # Chiều cao tối thiểu cố định
        output_scroll.setMaximumHeight(400)  # Chiều cao tối đa để giới hạn giãn
        output_group.setLayout(QVBoxLayout())
        output_group.layout().addWidget(output_scroll)
        self.io_container.addWidget(output_group)
        self.io_container.setStretch(self.io_container.count() - 1, 1)  # Stretch factor 1

        # PLC Info Group
        self.plc_info_group = QGroupBox("PLC Info")
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

        self.plc_info_layout.addStretch()  # Đẩy các label lên trên, tạo không gian trống phía dưới
        self.plc_info_widget.setLayout(self.plc_info_layout)

        plc_info_scroll = QScrollArea()
        plc_info_scroll.setWidget(self.plc_info_widget)
        plc_info_scroll.setWidgetResizable(True)
        plc_info_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        plc_info_scroll.setMinimumHeight(200)  # Chiều cao tối thiểu cố định
        plc_info_scroll.setMaximumHeight(400)  # Chiều cao tối đa để giới hạn giãn
        self.plc_info_group.setLayout(QVBoxLayout())
        self.plc_info_group.layout().addWidget(plc_info_scroll)
        self.io_container.addWidget(self.plc_info_group)
        self.io_container.setStretch(self.io_container.count() - 1, 1)  # Stretch factor 1
    # Line 267-371: Phương thức update_io_layout - Cập nhật layout cho Inputs, Outputs, và PLC Info
    # Note: Đảm bảo chiều cao tối đa (400px) phù hợp, có thể điều chỉnh nếu cần

    def update_plc_info(self):
        if "name" in self.connection_info:  # Kiểm tra thông tin kết nối có hợp lệ không
            self.title.setText(f"HMI Monitoring {self.connection_info['name']}")
            self.plc_name_label.setText(f"PLC Name: {self.connection_info['name']}")
            self.plc_ip_label.setText(f"IP: {self.connection_info['ip']}")
            self.plc_rack_slot_label.setText(f"Rack/Slot: {self.connection_info['rack']}/{self.connection_info['slot']}")
            self.plc_inputs_label.setText(f"Number of Inputs: {self.connection_info['inputs']}")
            self.plc_outputs_label.setText(f"Number of Outputs: {self.connection_info['outputs']}")
        else:
            self.title.setText("PLC HMI Monitoring")
            self.plc_name_label.setText("PLC Name: N/A")
            self.plc_ip_label.setText("IP: N/A")
            self.plc_rack_slot_label.setText("Rack/Slot: N/A")
            self.plc_inputs_label.setText("Number of Inputs: N/A")
            self.plc_outputs_label.setText("Number of Outputs: N/A")

        if self.plc.get_connected():  # Cập nhật trạng thái kết nối
            self.plc_status_label.setText("Status: Online")
            self.plc_status_label.setStyleSheet("border: 1px solid gray; padding: 2px; background-color: #4CAF50; color: white;")
        else:
            self.plc_status_label.setText("Status: Offline")
            self.plc_status_label.setStyleSheet("border: 1px solid gray; padding: 2px; background-color: #F44336; color: white;")
    # Line 373-397: Phương thức update_plc_info - Cập nhật thông tin PLC trên giao diện

    def show_connection_dialog(self):
        self.log_message("Button 'Add Device' clicked. Opening connection dialog...")
        dialog = ConnectionDialog(self)
        if dialog.exec_() == QDialog.Accepted:  # Xử lý khi nhấn OK
            self.connection_info = dialog.get_connection_info()
            self.input_tags.clear()  # Xóa tag cũ của inputs
            self.output_tags.clear()  # Xóa tag cũ của outputs
            self.log_message("Connection dialog accepted. Updated device info.")
            self.update_io_layout()  # Cập nhật lại layout với thông tin mới
        else:
            self.log_message("Connection dialog cancelled.")
    # Line 399-412: Phương thức show_connection_dialog - Hiển thị và xử lý dialog kết nối

    def show_tag_name_dialog(self):
        self.log_message("Button 'Tag Name' clicked. Opening tag name dialog...")
        dialog = TagNameDialog(self)
        if dialog.exec_() == QDialog.Accepted:  # Xử lý khi nhấn Save
            self.input_tags, self.output_tags = dialog.get_tags()
            self.log_message("Tag name dialog accepted. Updated tags.")
            self.update_io_layout()  # Cập nhật lại layout với tag mới
        else:
            self.log_message("Tag name dialog cancelled.")
    # Line 414-424: Phương thức show_tag_name_dialog - Hiển thị và xử lý dialog tag name

    def log_message(self, message):
        if hasattr(self, 'status_display'):  # Kiểm tra status_display đã khởi tạo
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            full_message = f"[{current_time}] {message}"
            self.status_display.setText(f"{self.status_display.toPlainText()}\n{full_message}")
            self.status_display.verticalScrollBar().setValue(self.status_display.verticalScrollBar().maximum())

            # Ghi vào file log
            with open(self.log_filename, 'a') as f:
                f.write(f"{full_message}\n")
    # Line 426-438: Phương thức log_message - Ghi log lên giao diện và file
    # Note: Đảm bảo thư mục log có quyền ghi

    def update_status(self):
        if self.plc.get_connected() and "ip" in self.connection_info:  # Kiểm tra kết nối
            self.status_display.setStyleSheet("background-color: #4CAF50; color: white;")
            if "Connected" not in self.status_display.toPlainText().split("\n")[-1]:
                self.log_message("Connected")

            num_input_bytes = (self.connection_info["inputs"] + 7) // 8  # Tính số byte cần đọc cho inputs
            try:
                input_data = self.plc.read_area(snap7.types.S7AreaPE, 0, 0, num_input_bytes)  # Đọc khu vực inputs
                if input_data and len(input_data) >= num_input_bytes:
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
                else:
                    self.log_message("Input data is empty or invalid!")
            except Exception as e:
                self.log_message(f"Error reading Input: {e}")

            num_output_bytes = (self.connection_info["outputs"] + 7) // 8  # Tính số byte cần đọc cho outputs
            try:
                output_data = self.plc.read_area(snap7.types.S7AreaPA, 0, 0, num_output_bytes)  # Đọc khu vực outputs
                if output_data and len(output_data) >= num_output_bytes:
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
                    self.log_message("Output data is empty or invalid!")
            except Exception as e:
                self.log_message(f"Error reading Output: {e}")
        else:
            self.status_display.setStyleSheet("background-color: #F44336; color: white;")
            if "Disconnected" not in self.status_display.toPlainText().split("\n")[-1]:
                self.log_message("Disconnected")
        self.update_plc_info()
    # Line 440-495: Phương thức update_status - Cập nhật trạng thái inputs và outputs định kỳ
    # Note: Đảm bảo PLC kết nối và cho phép đọc khu vực PE/PA

    def toggle_output(self, byte, bit):
        addr = f"Q{byte}.{bit}"
        self.log_message(f"Button 'T' clicked for {addr}. Attempting to toggle output...")
        if self.plc.get_connected():  # Kiểm tra kết nối trước khi thay đổi
            num_output_bytes = (self.connection_info["outputs"] + 7) // 8
            try:
                data = self.plc.read_area(snap7.types.S7AreaPA, 0, 0, num_output_bytes)  # Đọc dữ liệu outputs
                if data and len(data) >= num_output_bytes:
                    current_state = get_bool(data, byte, bit)
                    new_data = bytearray(num_output_bytes)
                    for i in range(num_output_bytes):
                        new_data[i] = data[i]
                    set_bool(new_data, byte, bit, not current_state)  # Đảo trạng thái
                    self.plc.write_area(snap7.types.S7AreaPA, 0, 0, new_data)  # Ghi lại dữ liệu
                    tag = self.output_tags.get(addr, addr)
                    self.log_message(f"Changed {tag} to {not current_state}")
                else:
                    self.log_message("Output data is invalid!")
            except Exception as e:
                self.log_message(f"Error changing Output: {e}")
        else:
            self.log_message("Cannot change: PLC is not connected")
    # Line 497-518: Phương thức toggle_output - Xử lý nút "T" để thay đổi trạng thái output
    # Note: Đảm bảo PLC cho phép ghi khu vực PA

    def closeEvent(self, event):
        if self.plc.get_connected():  # Kiểm tra và ngắt kết nối khi đóng cửa sổ
            self.plc.disconnect()
            self.log_message("PLC connection disconnected")
        with open(self.log_filename, 'a') as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Application closed.\n")
        event.accept()
    # Line 520-527: Phương thức closeEvent - Xử lý khi đóng cửa sổ

if __name__ == "__main__":
    app = QApplication(sys.argv)  # Khởi tạo ứng dụng Qt
    window = PLC_HMI()  # Tạo instance của PLC_HMI
    window.show()  # Hiển thị cửa sổ
    sys.exit(app.exec_())  # Chạy vòng lặp sự kiện
# Line 529-534: Khối main - Chạy ứng dụng