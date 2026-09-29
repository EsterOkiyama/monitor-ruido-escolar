# sheets.py - Pico W → Google Sheets via Apps Script
import urequests
import ujson
from config import SHEETS_URL, ESCOLA

contador_sheets = 0  # contador de envios

def enviar_sheets(db, status, alert_pct, timestamp):
    """
    Envia os dados de ruído para o Google Sheets via Apps Script.
    db          : valor de decibéis
    status      : "Bom", "Atenção" ou "Alerta"
    alert_pct   : percentual de alertas nos últimos 50 valores
    timestamp   : tempo Unix (int)
    """
    global contador_sheets
    try:
        # Monta payload JSON
        payload = {
            "timestamp": timestamp,
            "db": db,
            "status": status,
            "alert_pct": f"{alert_pct:.0f}%",
            "escola": ESCOLA
        }

        # Debug: imprime payload antes de enviar
        print("🔹 Payload enviado:", ujson.dumps(payload))
        print("🔹 Enviando para:", SHEETS_URL)

        # Envia POST com JSON puro
        r = urequests.post(
            SHEETS_URL,
            json=payload,  # <- importante: garante que Apps Script interprete como JSON
            headers={'Content-Type': 'application/json'}
        )

        # Verifica se deu certo
        if r.status_code == 200:
            contador_sheets += 1
            print(f"☁️ Sheets atualizado #{contador_sheets}")
        else:
            print(f"⚠️ Erro HTTP {r.status_code} ao enviar para Sheets")
            print("❌ Conteúdo de resposta:", r.text)

        r.close()

    except Exception as e:
        print("❌ Erro ao enviar Sheets:", e)