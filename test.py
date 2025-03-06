import snap7
from snap7.util import *
import time

def test_plc_connection():
    # Khởi tạo client snap7
    plc = snap7.client.Client()

    # Thông tin kết nối (thay đổi IP, rack, slot nếu cần)
    ip_address = "192.168.0.2"  # IP của PLCSIM hoặc PLC thật
    rack = 0                    # Rack mặc định
    slot = 1                    # Slot mặc định

    print(f"Thử kết nối với PLC tại {ip_address}, Rack {rack}, Slot {slot}...")

    try:
        # Thử kết nối với PLC
        plc.connect(ip_address, rack, slot)
        if plc.get_connected():
            print(f"Kết nối thành công với PLC tại {ip_address}!")
        else:
            print("Kết nối thất bại! PLC không phản hồi.")
            return

        # Đọc trạng thái Input I0.0 (1 byte từ byte 0)
        print("Đang đọc Input I0.0...")
        input_data = plc.read_area(snap7.types.S7AreaPE, 0, 0, 1)
        input_state = get_bool(input_data, 0, 0)  # Bit 0 của byte 0 (I0.0)
        print(f"Input I0.0: {'ON' if input_state else 'OFF'}")

        # Đọc trạng thái Output Q0.0 (1 byte từ byte 0)
        print("Đang đọc Output Q0.0...")
        output_data = plc.read_area(snap7.types.S7AreaPA, 0, 0, 1)
        output_state = get_bool(output_data, 0, 0)  # Bit 0 của byte 0 (Q0.0)
        print(f"Output Q0.0: {'ON' if output_state else 'OFF'}")

        # Toggle Output Q0.0 (Đổi trạng thái)
        print("Đang thay đổi trạng thái Output Q0.0...")
        new_data = bytearray(1)
        new_data[0] = output_data[0]
        set_bool(new_data, 0, 0, not output_state)
        plc.write_area(snap7.types.S7AreaPA, 0, 0, new_data)
        print(f"Đã đổi trạng thái Output Q0.0 thành {'ON' if not output_state else 'OFF'}")

        # Đợi 1 giây để kiểm tra thay đổi
        time.sleep(1)
        output_data = plc.read_area(snap7.types.S7AreaPA, 0, 0, 1)
        output_state = get_bool(output_data, 0, 0)
        print(f"Output Q0.0 sau khi thay đổi: {'ON' if output_state else 'OFF'}")

    except Exception as e:
        print(f"Lỗi: {e}")

    finally:
        # Ngắt kết nối
        if plc.get_connected():
            plc.disconnect()
            print("Đã ngắt kết nối với PLC.")
        else:
            print("Không có kết nối để ngắt.")

if __name__ == "__main__":
    test_plc_connection()