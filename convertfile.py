import json
import traceback
# Tên file đầu vào và đầu ra
json_file_path = 'cookies.json'
netscape_file_path = 'cookies.txt'

try:
    # Mở và đọc file JSON
    with open(json_file_path, 'r') as f:
        cookies_data = json.load(f)

    # Mở file .txt để ghi
    with open(netscape_file_path, 'w') as f:
        # Viết header tiêu chuẩn của định dạng Netscape
        f.write("# Netscape HTTP Cookie File\n")
        f.write("# http://www.netscape.com/newsref/std/cookie_spec.html\n")
        f.write("# This is a generated file! Do not edit.\n\n")

        # Lặp qua từng value (đối tượng cookie) trong file JSON --- ĐÂY LÀ DÒNG ĐÃ SỬA
        for cookie in cookies_data.values():
            # Các trường cần thiết theo định dạng Netscape
            domain = cookie.get('domain', '')
            # Cờ hostOnly: TRUE nếu domain không bắt đầu bằng dấu chấm
            host_only = str(not domain.startswith('.')).upper()
            path = cookie.get('path', '/')
            secure = str(cookie.get('secure', False)).upper()
            # Chuyển đổi thời gian hết hạn (expirationDate), nếu không có thì để 0
            expires = str(int(cookie.get('expirationDate', 0)))
            name = cookie.get('name', '')
            value = cookie.get('value', '')

            # Ghi dòng cookie đã định dạng vào file .txt
            f.write(f"{domain}\t{host_only}\t{path}\t{secure}\t{expires}\t{name}\t{value}\n")

    print(f"Chuyển đổi thành công! Đã tạo file: {netscape_file_path}")

except FileNotFoundError:
    print(f"Lỗi: Không tìm thấy file '{json_file_path}'. Hãy chắc chắn file nằm đúng chỗ.")
except Exception as e:
    traceback.print_exc()
    print(f"Đã xảy ra lỗi: {e}")