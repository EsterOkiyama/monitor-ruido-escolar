"""
MONITOR RUÍDO v4.0 - AUTÔNOMO COM OLED + WEB + SHEETS
Ester Univesp PI 2026 - BitDogLab + Pico W
"""

import uasyncio as asyncio
import network, math, time
import ntptime
from machine import ADC, RTC, SoftI2C
from bitdoglab import BitDogLab
from ssd1306 import SSD1306_I2C
from ruido_db import salvar_db, resetar_db, historico_db
from web_dashboard import web_server
from sheets import enviar_sheets
from config import (
    WIFI_SSID,
    WIFI_PWD,
    LIMITE_BOM,
    LIMITE_ALERTA
)

# ========= HARDWARE =========
mic = ADC(28)

joy_x = ADC(27)   # VRx
joy_y = ADC(26)   # VRy
# ========= MÉDIA MÓVEL =========

janela_media = []
TAMANHO_MEDIA = 10

def media_movel(valor):

    janela_media.append(valor)

    if len(janela_media) > TAMANHO_MEDIA:
        janela_media.pop(0)

    return sum(janela_media) / len(janela_media)


def ler_joystick():

    x = joy_x.read_u16()
    y = joy_y.read_u16()

    if y > 55000:
        return "CIMA"

    if y < 5000:
        return "BAIXO"

    if x < 5000:
        return "ESQUERDA"

    if x > 55000:
        return "DIREITA"

    return None

    
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

AMBIENTES = [
    "Sala",
    "Corredor",
    "Patio",
    "Biblioteca"
]

indice_ambiente = 0

ambiente_selecionado = AMBIENTES[indice_ambiente]

ambiente_atual = ambiente_selecionado

modo_selecao = False
# ========= WIFI =========
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

print("Conectando em:", WIFI_SSID)

wlan.connect(WIFI_SSID, WIFI_PWD)

timeout = time.ticks_ms() + 20000

while not wlan.isconnected() and time.ticks_ms() < timeout:

    print("Status:", wlan.status())

    time.sleep(1)

print("Status final:", wlan.status())

if wlan.isconnected():

    ip = wlan.ifconfig()[0]

    try:

        ntptime.settime()

        t = time.localtime(
            time.time() - 3 * 3600
        )

        rtc.datetime(
            (
                t[0],  # ano
                t[1],  # mês
                t[2],  # dia
                0,
                t[3],  # hora
                t[4],  # minuto
                t[5],  # segundo
                0
            )
        )

        print("RTC sincronizado")

    except Exception as e:

        print(
            "Erro ao sincronizar RTC:",
            e
        )

else:

    ip = "OFFLINE"

print("IP conectado:", ip)

# ========= SERVIDOR WEB =========
if wlan.isconnected():

   asyncio.create_task(
    web_server(ip)
   )
# ========= FUNÇÃO DE MEDIÇÃO =========
def medir_db():

    soma = sum(
        (
            mic.read_u16()
            - 32768
        ) ** 2
        for _ in range(500)
    )

    rms = math.sqrt(
        soma / 500
    )

    db = (
        20
        * math.log10(
            max(
                rms / 150 + 1,
                0.001
            )
        )
        + 30
    )

    # pequeno ajuste de calibração
    db -= 10

    db = max(
        30,
        min(
            120,
            db
        )
        
    )

    db = media_movel(db)

    return round(db, 1)
    

# ========= DESENHO NO OLED =========

def desenhar_oled(db, status, alert_pct):

    if not oled:
        return

    oled.fill(0)
    
    if modo_selecao:

        oled.text(
            "Selecionar",
            0,
            0
        )

        oled.text(
            ambiente_selecionado[:12],
            0,
            24
        )

        oled.text(
            "DIR=OK",
            0,
            48
        )

        oled.show()

        return

    t = rtc.datetime()

    oled.text(
        f"{t[2]:02d}/{t[1]:02d}",
        0,
        0
    )

    oled.text(
        f"{t[4]:02d}:{t[5]:02d}",
        70,
        0
    )

    oled.text(
        f"{db:.1f}",
        0,
        16
    )

    oled.text(
        "dB",
        80,
        16
    )

    oled.text(
        status,
        0,
        28
    )

    oled.text(
        f"Alert:{alert_pct:.0f}%",
        0,
        40
    )

    oled.text(
        ambiente_atual[:12],
        0,
        52
    )

    for i, val in enumerate(historico_db[-50:]):

        y = 63 - int(
            (val / 120) * 50
        )

        oled.pixel(
            i,
            y,
            1
        )

    oled.show()

# ========= LOOP PRINCIPAL =========
async def loop_principal():
    
    global indice_ambiente
    global ambiente_atual
    global ambiente_selecionado
    global modo_selecao

    while True:
        
        direcao = ler_joystick()

        
        if direcao == "CIMA":
            
            modo_selecao = True

            indice_ambiente -= 1

            if indice_ambiente < 0:
                indice_ambiente = len(AMBIENTES) - 1

            ambiente_selecionado = AMBIENTES[indice_ambiente]

            print("Ambiente:", ambiente_selecionado)

            await asyncio.sleep(0.3)

        elif direcao == "BAIXO":
            
            modo_selecao = True

            indice_ambiente += 1

            if indice_ambiente >= len(AMBIENTES):
                indice_ambiente = 0

            ambiente_selecionado = AMBIENTES[indice_ambiente]

            print("Ambiente:", ambiente_selecionado)

            await asyncio.sleep(0.3)

        elif direcao == "DIREITA":

            ambiente_atual = ambiente_selecionado
            
            bdlab.buzzer_alert(80)
            
            modo_selecao = False

            print("CONFIRMADO:",ambiente_atual
            )

            if oled:

                oled.fill(0)

                oled.text(
                    "AMBIENTE",
                    0,
                    0
                )

                oled.text(
                    "CONFIRMADO",
                    0,
                    16
                )

                oled.text(
                    ambiente_atual[:12],
                    0,
                    32
                )

                oled.show()

            await asyncio.sleep(0.5)
        # RESET via botão
        if bdlab.botao_pressionado():	

            resetar_db()

            if oled:

                oled.fill(0)

                oled.text(
                    "DB RESET",
                    0,
                    0
                )

                oled.show()

            bdlab.buzzer_alert(150)

            await asyncio.sleep(1)

        # Medição e histórico
        db = medir_db()

        status, alert_pct, timestamp = salvar_db(
            db,
            rtc,
            ambiente_atual,
            wlan.isconnected()
        )
        # OLED
        desenhar_oled(db, status, alert_pct)

        # LED/Buzzer
        
        if db < LIMITE_BOM:

            bdlab.desenhar_icone(
                bdlab.icone_bom,
                (0, 50, 0)
            )

        elif db < LIMITE_ALERTA:

            bdlab.desenhar_icone(
                bdlab.icone_atencao,
                (50, 50, 0)
            )

        else:

            bdlab.desenhar_icone(
                bdlab.icone_alerta,
                (50, 0, 0)
            )

        # Log REPL
        print(f"[{time.localtime()[2]:02d}/{time.localtime()[1]:02d}] dB:{db:.1f} | Status:{status} | Alert:{alert_pct:.0f}%")

        await asyncio.sleep(0.2)

# ========= EXECUTA LOOP =========
asyncio.run(loop_principal())
