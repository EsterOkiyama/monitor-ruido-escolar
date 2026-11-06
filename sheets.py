import urequests
import ujson
from config import SHEETS_URL, ESCOLA

contador_sheets = 0

def enviar_sheets(db, status, alert_pct, timestamp, ambiente="Sala"):
    global contador_sheets

    if not SHEETS_URL:
        return

    r = None
    try:
        data = f"{timestamp[6:8]}/{timestamp[4:6]}/{timestamp[0:4]}"
        hora = f"{timestamp[9:11]}:{timestamp[11:13]}:{timestamp[13:15]}"
        alert_str = f"{alert_pct:.0f}%"

        def clean_str(val):
            return str(val).replace(' ', '%20').replace('ã', 'a').replace('ç', 'c').replace('ê', 'e')

        # URL com todos os parâmetros explicitamente alinhados
        url = (
            f"{SHEETS_URL}?data={clean_str(data)}&hora={clean_str(hora)}&db={db}"
            f"&status={clean_str(status)}&alert_pct={clean_str(alert_str)}&escola={clean_str(ESCOLA)}&ambiente={clean_str(ambiente)}"
        )

        print("🔹 Enviando dados para o Sheets...")

        r = urequests.get(url)
        print("Status HTTP recebido:", r.status_code)

        if r.status_code == 200:
            contador_sheets += 1
            print(f"☁️ Sheets atualizado #{contador_sheets}")
        else:
            print(f"⚠️ Erro HTTP do Google: {r.status_code}")

    except Exception as e:
        print("❌ Erro ao enviar Sheets:", e)
        
    finally:
        if r is not None:
            try:
                r.close()
            except:
                pass
