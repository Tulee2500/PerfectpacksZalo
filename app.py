import sys
import os

# ===== FIX PATH CHO PYINSTALLER - PHẢI Ở ĐẦU FILE =====
if getattr(sys, 'frozen', False):
    # Đang chạy từ file .exe
    base_path = sys._MEIPASS
else:
    # Đang chạy code Python bình thường
    base_path = os.path.abspath(".")

from flask import Flask, render_template, request, jsonify, send_file
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import threading
import pandas as pd
from werkzeug.utils import secure_filename

# Khởi tạo Flask với đường dẫn templates và static cố định
app = Flask(__name__,
            template_folder=os.path.join(base_path, 'templates'),
            static_folder=os.path.join(base_path, 'static'))

# Cấu hình upload folder (tạo trong thư mục tạm khi chạy .exe)
if getattr(sys, 'frozen', False):
    upload_folder = os.path.join(os.path.dirname(sys.executable), 'uploads')
else:
    upload_folder = os.path.join(base_path, 'uploads')

app.config['UPLOAD_FOLDER'] = upload_folder
app.config['ALLOWED_EXTENSIONS'] = {'xlsx', 'xls'}

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


class ZaloAutoSender:
    def __init__(self):
        self.driver = None
        self.wait = None

    def khoi_tao_driver(self):
        """Khởi tạo Chrome driver với webdriver-manager"""
        try:
            print("\n" + "=" * 60)
            print("ĐANG KHỞI TẠO TRÌNH DUYỆT...")
            print("=" * 60)

            options = webdriver.ChromeOptions()

            # Tìm Chrome đã cài sẵn trên máy
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            ]

            chrome_found = False
            for chrome_path in chrome_paths:
                if os.path.exists(chrome_path):
                    options.binary_location = chrome_path
                    chrome_found = True
                    print(f"✓ Tìm thấy Chrome tại: {chrome_path}")
                    break

            if not chrome_found:
                print("⚠️ Không tìm thấy Chrome. Sử dụng Chrome mặc định...")

            # Các argument cơ bản
            options.add_argument('--start-maximized')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-blink-features=AutomationControlled')

            # Tắt các cảnh báo
            options.add_argument('--disable-logging')
            options.add_argument('--log-level=3')
            options.add_argument('--silent')

            # Thêm options để tránh bị phát hiện là bot
            options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
            options.add_experimental_option('useAutomationExtension', False)

            # Tắt các thông báo không cần thiết
            prefs = {
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0,
            }
            options.add_experimental_option("prefs", prefs)

            print("\n📥 Đang tải ChromeDriver...")
            print("⏳ Lần đầu tiên có thể mất 30-60 giây để tải driver...")

            # Sử dụng webdriver-manager để tự động tải ChromeDriver
            service = Service(ChromeDriverManager().install())
            print("✓ Đã tải ChromeDriver thành công!")

            print("\n🚀 Đang khởi động Google Chrome...")
            self.driver = webdriver.Chrome(service=service, options=options)
            self.wait = WebDriverWait(self.driver, 20)

            print("✓ Đã khởi động Chrome thành công!")
            print("=" * 60 + "\n")

        except Exception as e:
            print("\n" + "=" * 60)
            print("❌ LỖI KHI KHỞI TẠO CHROME")
            print("=" * 60)
            print(f"Chi tiết lỗi: {str(e)}")
            print("\n⚠️ CÁCH KHẮC PHỤC:")
            print("1. Đảm bảo đã cài Google Chrome trên máy")
            print("2. Kiểm tra kết nối Internet")
            print("3. Tắt Antivirus/Windows Defender tạm thời")
            print("4. Chạy file .exe với quyền Administrator")
            print("5. Nếu vẫn lỗi, chạy bằng Python thay vì .exe:")
            print("   python app.py")
            print("=" * 60 + "\n")
            raise

    def dang_nhap_zalo(self):
        """Mở Zalo Web và chờ đăng nhập"""
        print("Đang mở Zalo Web...")
        self.driver.get("https://chat.zalo.me/")
        print("Chờ đăng nhập...")
        self.wait.until(EC.presence_of_element_located((By.ID, "contact-search-input")))
        print("✓ Đăng nhập thành công!")
        time.sleep(2)

    def gui_tin_nhan(self, so_dien_thoai, noi_dung):
        """Gửi tin nhắn cho một số điện thoại"""
        try:
            print(f"\n--- Đang gửi tin cho số: {so_dien_thoai} ---")

            # Tìm kiếm số điện thoại
            search_input = self.wait.until(
                EC.element_to_be_clickable((By.ID, "contact-search-input"))
            )
            search_input.click()
            time.sleep(1)

            search_input.clear()
            search_input.send_keys(so_dien_thoai)
            print(f"Đã nhập số điện thoại: {so_dien_thoai}")
            time.sleep(3)

            # Click vào kết quả đầu tiên
            first_result = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div[id^='friend-item-']"))
            )
            first_result.click()
            print("Đã chọn người nhận")
            time.sleep(2)

            # Tìm ô nhập tin nhắn
            print("Tìm ô nhập tin nhắn...")
            message_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "richInput"))
            )

            # Set contenteditable = true và focus vào ô nhập
            self.driver.execute_script("""
                var input = arguments[0];
                input.setAttribute('contenteditable', 'true');
                input.focus();
            """, message_input)
            time.sleep(0.5)

            # Xóa nội dung cũ nếu có
            self.driver.execute_script("arguments[0].innerHTML = '';", message_input)
            time.sleep(0.5)

            # Nhập tin nhắn bằng JavaScript
            print("Đang nhập nội dung tin nhắn...")
            lines = noi_dung.split('\n')
            html_content = ""
            for i, line in enumerate(lines):
                if line.strip():  # Chỉ thêm dòng không rỗng
                    html_content += f'<div id="input_line_{i}"><span style="white-space: pre-wrap;">{line}</span></div>'

            # Set nội dung và kích hoạt sự kiện input
            self.driver.execute_script("""
                var input = arguments[0];
                input.innerHTML = arguments[1];

                // Kích hoạt các sự kiện cần thiết
                var event = new Event('input', { bubbles: true });
                input.dispatchEvent(event);

                var changeEvent = new Event('change', { bubbles: true });
                input.dispatchEvent(changeEvent);

                // Kích hoạt sự kiện keyup
                var keyupEvent = new KeyboardEvent('keyup', { bubbles: true });
                input.dispatchEvent(keyupEvent);

                // Focus lại vào ô nhập
                input.focus();
            """, message_input, html_content)
            time.sleep(1)

            # Thử gửi tin nhắn bằng nhiều cách
            gui_thanh_cong = False

            # Cách 1: Dùng phím Enter
            print("Thử 1: Gửi bằng phím Enter...")
            try:
                actions = ActionChains(self.driver)
                actions.send_keys(Keys.ENTER).perform()
                time.sleep(1)

                # Kiểm tra xem tin nhắn đã được gửi chưa
                content_after = self.driver.execute_script("return arguments[0].innerText;", message_input)
                if len(content_after.strip()) == 0:
                    print(f"✓ Đã gửi tin nhắn thành công cho {so_dien_thoai} (Enter)")
                    gui_thanh_cong = True
            except Exception as e:
                print(f"Thử 1 thất bại: {str(e)}")

            # Cách 2: Click nút gửi bằng JavaScript
            if not gui_thanh_cong:
                print("Thử 2: Click nút gửi bằng JavaScript...")
                try:
                    self.driver.execute_script("""
                        // Tìm tất cả các nút gửi
                        var sendButtons = Array.from(document.querySelectorAll('div[title*="Gửi"], div[title*="Send"]'));

                        // Lọc ra nút đang hiển thị
                        var visibleButton = sendButtons.find(btn => {
                            return btn.offsetParent !== null && 
                                   window.getComputedStyle(btn).display !== 'none' &&
                                   window.getComputedStyle(btn).visibility !== 'hidden';
                        });

                        // Nếu tìm thấy nút, click vào nó
                        if (visibleButton) {
                            visibleButton.click();
                            return true;
                        }

                        // Nếu không tìm thấy, thử tìm bằng class
                        var buttons = document.querySelectorAll('div.send-msg-btn, button.send-msg-btn');
                        for(var i = 0; i < buttons.length; i++) {
                            var style = window.getComputedStyle(buttons[i]);
                            if(buttons[i].offsetParent !== null && style.display !== 'none' && style.visibility !== 'hidden') {
                                buttons[i].click();
                                return true;
                            }
                        }

                        // Thử tìm bằng XPath nếu vẫn chưa được
                        var xpathResult = document.evaluate('//*[contains(@class, "send-msg-btn")]', document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                        for (var i = 0; i < xpathResult.snapshotLength; i++) {
                            var btn = xpathResult.snapshotItem(i);
                            var style = window.getComputedStyle(btn);
                            if(btn.offsetParent !== null && style.display !== 'none' && style.visibility !== 'hidden') {
                                btn.click();
                                return true;
                            }
                        }

                        return false;
                    """)

                    time.sleep(1)
                    content_after = self.driver.execute_script("return arguments[0].innerText;", message_input)
                    if len(content_after.strip()) == 0:
                        print(f"✓ Đã gửi tin nhắn thành công cho {so_dien_thoai} (JS Click)")
                        gui_thanh_cong = True
                except Exception as e:
                    print(f"Thử 2 thất bại: {str(e)}")

            # Cách 3: Gửi form bằng JavaScript
            if not gui_thanh_cong:
                print("Thử 3: Gửi form bằng JavaScript...")
                try:
                    self.driver.execute_script("""
                        // Tìm form chứa ô nhập tin nhắn
                        var form = document.querySelector('form');
                        if (!form) {
                            // Nếu không tìm thấy form, thử tìm form gần ô nhập
                            var input = document.getElementById('richInput');
                            while (input && input.tagName !== 'FORM' && input.parentElement) {
                                input = input.parentElement;
                            }
                            if (input && input.tagName === 'FORM') {
                                form = input;
                            }
                        }

                        if (form) {
                            form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
                            return true;
                        }
                        return false;
                    """)
                    time.sleep(1)

                    content_after = self.driver.execute_script("return arguments[0].innerText;", message_input)
                    if len(content_after.strip()) == 0:
                        print(f"✓ Đã gửi tin nhắn thành công cho {so_dien_thoai} (Form Submit)")
                        gui_thanh_cong = True
                except Exception as e:
                    print(f"Thử 3 thất bại: {str(e)}")

            # Nếu vẫn chưa gửi được, thử click vào nút gửi bằng tọa độ
            if not gui_thanh_cong:
                print("Thử 4: Click bằng tọa độ...")
                try:
                    # Tìm nút gửi
                    send_button = self.driver.find_element(By.CSS_SELECTOR,
                                                           "div.send-msg-btn, button.send-msg-btn, [title*='Gửi'], [title*='Send']")

                    # Di chuyển chuột đến nút và click
                    actions = ActionChains(self.driver)
                    actions.move_to_element(send_button).click().perform()
                    time.sleep(1)

                    # Kiểm tra xem tin nhắn đã được gửi chưa
                    content_after = self.driver.execute_script("return arguments[0].innerText;", message_input)
                    if len(content_after.strip()) == 0:
                        print(f"✓ Đã gửi tin nhắn thành công cho {so_dien_thoai} (Tọa độ chuột)")
                        gui_thanh_cong = True
                except Exception as e:
                    print(f"Thử 4 thất bại: {str(e)}")

            # Cách 5: Gửi bằng phím tắt
            if not gui_thanh_cong:
                print("Thử 5: Dùng phím tắt...")
                try:
                    # Thử Ctrl+Enter
                    actions = ActionChains(self.driver)
                    actions.key_down(Keys.CONTROL).send_keys(Keys.ENTER).key_up(Keys.CONTROL).perform()
                    time.sleep(1)

                    # Kiểm tra xem tin nhắn đã được gửi chưa
                    content_after = self.driver.execute_script("return arguments[0].innerText;", message_input)
                    if len(content_after.strip()) == 0:
                        print(f"✓ Đã gửi tin nhắn thành công cho {so_dien_thoai} (Phím tắt)")
                        gui_thanh_cong = True
                except Exception as e:
                    print(f"Thử 5 thất bại: {str(e)}")

            # Nếu vẫn chưa gửi được, thử cách cuối cùng
            if not gui_thanh_cong:
                print("Thử 6: Gửi bằng JavaScript cuối cùng...")
                try:
                    self.driver.execute_script("""
                        // Thử tìm và click nút gửi bằng nhiều cách khác nhau
                        function clickSendButton() {
                            // Cách 1: Tìm bằng class
                            var sendBtn = document.querySelector('.send-msg-btn');
                            if (sendBtn && sendBtn.offsetParent !== null) {
                                sendBtn.click();
                                return true;
                            }

                            // Cách 2: Tìm bằng title
                            sendBtn = document.querySelector('[title*="Gửi"], [title*="Send"]');
                            if (sendBtn && sendBtn.offsetParent !== null) {
                                sendBtn.click();
                                return true;
                            }

                            // Cách 3: Tìm button hoặc div có chứa icon gửi
                            sendBtn = document.querySelector('button[data-icon="send"], div[data-icon="send"]');
                            if (sendBtn && sendBtn.offsetParent !== null) {
                                sendBtn.click();
                                return true;
                            }

                            return false;
                        }

                        return clickSendButton();
                    """)

                    time.sleep(1)
                    content_after = self.driver.execute_script("return arguments[0].innerText;", message_input)
                    if len(content_after.strip()) == 0:
                        print(f"✓ Đã gửi tin nhắn thành công cho {so_dien_thoai} (JS cuối cùng)")
                        gui_thanh_cong = True
                except Exception as e:
                    print(f"Thử 6 thất bại: {str(e)}")

            if not gui_thanh_cong:
                print("⚠️ Không thể tự động gửi. Vui lòng click nút gửi thủ công!")
                print("Chờ 10 giây để bạn gửi thủ công...")
                time.sleep(10)

            time.sleep(2)
            return gui_thanh_cong

        except Exception as e:
            print(f"✗ Lỗi khi gửi tin cho {so_dien_thoai}: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def dong_trinh_duyet(self):
        """Đóng trình duyệt"""
        if self.driver:
            self.driver.quit()
            print("Đã đóng trình duyệt")


# Biến global để lưu instance
zalo_sender = None
browser_open = False


@app.route('/')
def index():
    """Trang chủ"""
    return render_template('index.html')


@app.route('/upload-excel', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Không có file được chọn'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Không có file được chọn'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            # Read Excel file
            df = pd.read_excel(filepath)

            # Find phone number column (case insensitive)
            phone_columns = [col for col in df.columns if
                             'số điện thoại' in str(col).lower() or 'phone' in str(col).lower() or 'sdt' in str(
                                 col).lower()]

            if not phone_columns:
                return jsonify({
                    'success': False,
                    'message': 'Không tìm thấy cột số điện thoại trong file Excel. Vui lòng đảm bảo có cột chứa số điện thoại.'
                }), 400

            phone_numbers = df[phone_columns[0]].dropna().astype(str).str.strip().tolist()

            # Remove any non-digit characters from phone numbers
            phone_numbers = [''.join(filter(str.isdigit, num)) for num in phone_numbers]

            # Remove empty strings
            phone_numbers = [num for num in phone_numbers if num]

            if not phone_numbers:
                return jsonify({
                    'success': False,
                    'message': 'Không tìm thấy số điện thoại hợp lệ trong file Excel.'
                }), 400

            return jsonify({
                'success': True,
                'phone_numbers': phone_numbers,
                'count': len(phone_numbers)
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Lỗi khi đọc file Excel: {str(e)}'
            }), 500

    return jsonify({
        'success': False,
        'message': 'Định dạng file không được hỗ trợ. Vui lòng tải lên file Excel (.xlsx hoặc .xls)'
    }), 400


@app.route('/gui-tin-nhan', methods=['POST'])
def gui_tin_nhan_route():
    global browser_open, zalo_sender
    data = request.json
    print(f"Dữ liệu nhận được từ frontend: {data}")  # Debug log
    danh_sach_so = data.get('danh_sach_so', [])
    noi_dung = data.get('noi_dung')
    print(f"Danh sách số: {danh_sach_so}")
    print(f"Nội dung: '{noi_dung}'")
    print(f"Kiểm tra danh_sách_số: {bool(danh_sach_so)}")
    print(f"Kiểm tra nội_dung: {bool(noi_dung)}")

    if not danh_sach_so or not noi_dung:
        return jsonify({
            'success': False,
            'message': f'Vui lòng nhập đầy đủ danh sách số điện thoại và nội dung tin nhắn. Danh sách: {len(danh_sach_so)} số, Nội dung: {len(noi_dung) if noi_dung else 0} ký tự'
        }), 400

    def xu_ly_gui_tin():
        global browser_open, zalo_sender
        try:
            # Khởi tạo trình duyệt nếu chưa mở
            if not browser_open:
                zalo_sender = ZaloAutoSender()
                zalo_sender.khoi_tao_driver()
                zalo_sender.dang_nhap_zalo()
                browser_open = True

            # Gửi tin nhắn đến từng số điện thoại
            for so_dien_thoai in danh_sach_so:
                try:
                    print(f"\nĐang gửi tin nhắn đến {so_dien_thoai}...")
                    thanh_cong = zalo_sender.gui_tin_nhan(so_dien_thoai, noi_dung)

                    if thanh_cong:
                        print(f"✓ Đã gửi tin nhắn thành công đến {so_dien_thoai}")
                    else:
                        print(f"✗ Không thể gửi tin nhắn đến {so_dien_thoai}")

                    # Đợi 5 phút 3 giây trước khi gửi tin nhắn tiếp theo
                    print("Đợi 5 phút 3 giây trước khi gửi tin nhắn tiếp theo...")
                    time.sleep(303)  # 5 phút * 60 giây + 3 giây = 303 giây

                except Exception as e:
                    print(f"Lỗi khi gửi tin nhắn đến {so_dien_thoai}: {str(e)}")
                    continue

            # Đóng trình duyệt sau khi gửi xong tất cả
            print("\nĐã gửi xong tất cả tin nhắn. Đóng trình duyệt...")
            if zalo_sender:
                zalo_sender.dong_trinh_duyet()
                browser_open = False

        except Exception as e:
            print(f"Lỗi: {str(e)}")
            import traceback
            traceback.print_exc()
            if zalo_sender:
                zalo_sender.dong_trinh_duyet()
                browser_open = False

    # Chạy trong thread riêng để không block
    thread = threading.Thread(target=xu_ly_gui_tin)
    thread.daemon = True
    thread.start()

    return jsonify({
        'success': True,
        'message': f'Đang bắt đầu gửi tin nhắn đến {len(danh_sach_so)} số điện thoại, mỗi phút 1 tin nhắn...'
    })


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 ZALO AUTO SENDER - HỆ THỐNG GỬI TIN TỰ ĐỘNG")
    print("=" * 60)
    print("📍 Server đang chạy tại: http://localhost:5000")
    print("📱 Mở trình duyệt và truy cập link trên để sử dụng")
    print("=" * 60 + "\n")
    app.run(debug=True, port=5000)