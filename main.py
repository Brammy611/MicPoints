from machine import ADC, Pin, I2C
from ssd1306 import SSD1306_I2C
import network, socket, time

# ================= WIFI ======================
SSID = "nama wifi yang digunakan"
PASSWORD = " "
SERVER_IP = "isi sesuai ip laptop masing masing"
SERVER_PORT = 5000

# ================= KONEKSI WIFI ======================
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)

# OLED akan menampilkan status koneksi
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = SSD1306_I2C(128, 64, i2c)

oled.fill(0)
oled.text("Connecting WiFi", 0, 0)
oled.show()

while not wifi.isconnected():
    time.sleep(0.3)

print("WiFi connected:", wifi.ifconfig())

oled.fill(0)
oled.text("WiFi Connected", 0, 0)
oled.text(wifi.ifconfig()[0], 0, 10)
oled.show()
time.sleep(1)

# ================= PIN TOMBOL ======================
button = Pin(14, Pin.IN, Pin.PULL_UP)
recording = False

# ================= MIC ANALOG ======================
mic = ADC(Pin(34))
mic.atten(ADC.ATTN_11DB)
mic.width(ADC.WIDTH_12BIT)

# ================= READY STATUS OLED ======================
oled.fill(0)
oled.text("Ready", 0, 0)
oled.text("Press Button", 0, 12)
oled.show()

print("🟢 Tekan tombol untuk mulai / stop rekaman")

# ================= LOOP UTAMA ======================
while True:
    if not button.value():  # tombol ditekan
        time.sleep(0.2)

        if not recording:
            print("🎙 Mulai rekaman...")
            recording = True

            # UPDATE OLED
            oled.fill(0)
            oled.text("Recording...", 0, 0)
            oled.show()

            # Buka koneksi socket
            addr = socket.getaddrinfo(SERVER_IP, SERVER_PORT)[0][-1]
            s = socket.socket()
            s.connect(addr)

            while recording:
                val = mic.read()
                s.send(val.to_bytes(2, 'little'))

                # cek tombol lagi untuk stop
                if not button.value():
                    time.sleep(0.2)
                    print("🛑 Rekaman dihentikan.")
                    recording = False
                    s.close()

                    # OLED update stop
                    oled.fill(0)
                    oled.text("Stopped", 0, 0)
                    oled.text("Press button", 0, 15)
                    oled.show()
                    break

        else:
            print("⚠️ Sudah berhenti. Tekan lagi untuk mulai.")
            time.sleep(0.3)
