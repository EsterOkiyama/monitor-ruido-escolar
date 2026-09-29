"""
MONITOR RUÍDO v4.0 - AUTÔNOMO COM OLED + WEB + SHEETS
Ester Univesp PI 2026 - BitDogLab + Pico W
"""

import uasyncio as asyncio
import network, math, time
from machine import ADC, RTC, SoftI2C
from bitdoglab import BitDogLab
from ssd1306 import SSD1306_I2C
from ruido_db import salvar_db, resetar_db, historico_db
from web_dashboard import web_server
from sheets import enviar_sheets
from config import WIFI_SSID, WIFI_PWD, LIMITE_DB

# ========= HARDWARE =========
mic = ADC(28)
rtc = RTC()
i2c_oled = SoftI2C(scl=15, sda=14)
try:
    oled = SSD1306_I2C(128,64,i2c_oled)
    oled.fill(0)
    oled.text("OLED OK",0,0)
    oled.show()
except Exception as e:
    oled = None
    print("OLED off:", e)

bdlab = BitDogLab()

# ========= WIFI =========
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PWD)
timeout = time.ticks_ms() + 20000
while not wlan.isconnected() and time.ticks_ms() < timeout:
    time.sleep(1)
ip = wlan.ifconfig()[0] if wlan.isconnected() else "OFFLINE"
print(f"IP conectado: {ip}")

# ========= SERVIDOR WEB =========
asyncio.create_task(web_server(ip))

# ========= FUNÇÃO DE MEDIÇÃO =========
def medir_db():
    soma = sum((mic.read_u16()-32768)**2 for _ in range(300))
    rms = math.sqrt(soma/300)
    db = 20*math.log10(max(rms/150+1,0.001))+30
    return round(max(30,min(120,db)),1)

# ========= DESENHO NO OLED =========
def desenhar_oled(db, status, alert_pct):
    if not oled:
        return
    oled.fill(0)
    t = rtc.datetime()
    # Data e hora
    oled.text(f"{t[2]:02d}/{t[1]:02d}/{t[0]}", 0, 0)
    oled.text(f"{t[4]:02d}:{t[5]:02d}", 70, 0)
    # Nível dB atual
    oled.text(f"dB:{db:.1f}", 0, 16)
    oled.text(status, 0, 28)
    oled.text(f"Alert:{alert_pct:.0f}%", 0, 40)
    oled.text(f"IP:{ip[:10]}", 0, 52)

    # HISTÓRICO: pixels individuais
    for i, val in enumerate(historico_db[-50:]):
        y = 63 - int((val / 120) * 50)  # escala 0-120 dB
        oled.pixel(i, y, 1)  # desenha cada pixel do histórico

    oled.show()

# ========= LOOP PRINCIPAL =========
async def loop_principal():
    while True:
        # RESET via botão
        if bdlab.botao_pressionado():
            resetar_db()
            if oled:
                oled.fill(0)
                oled.text("DB RESET",0,0)
                oled.show()
            bdlab.buzzer_alert(150)
            await asyncio.sleep(1)

        # Medição e histórico
        db = medir_db()
        status, alert_pct, timestamp = salvar_db(db, rtc, True)

        # OLED
        desenhar_oled(db, status, alert_pct)

        # LED/Buzzer
        cor = (0,50,0) if db<60 else (50,50,0) if db<LIMITE_DB else (50,0,0)
        icone = bdlab.icone_alerta if db>=LIMITE_DB else bdlab.icone_atencao if db>=60 else bdlab.icone_bom
        bdlab.desenhar_icone(icone, cor)
        if db>=LIMITE_DB:
            bdlab.buzzer_alert(200)

        # Log REPL
        print(f"[{time.localtime()[2]:02d}/{time.localtime()[1]:02d}] dB:{db:.1f} | Status:{status} | Alert:{alert_pct:.0f}%")

        await asyncio.sleep(1.8)

# ========= EXECUTA LOOP =========
asyncio.run(loop_principal())