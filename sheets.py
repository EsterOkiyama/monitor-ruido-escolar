import urequests
import ujson

from config import SHEETS_URL, ESCOLA

contador_sheets = 0

def enviar_sheets(
    db,
    status,
    alert_pct,
    timestamp
):

    global contador_sheets

    if not SHEETS_URL:
        return

    try:

        data = (
            f"{timestamp[6:8]}/"
            f"{timestamp[4:6]}/"
            f"{timestamp[0:4]}"
        )

        hora = (
            f"{timestamp[9:11]}:"
            f"{timestamp[11:13]}:"
            f"{timestamp[13:15]}"
        )

        payload = {
            "data": data,
            "hora": hora,
            "db": db,
            "status": status,
            "alert_pct": f"{alert_pct:.0f}%",
            "escola": ESCOLA,
            "ambiente": "Sala de Aula"
        }

        print(
            "🔹 Payload enviado:",
            ujson.dumps(payload)
        )

        print(
            "🔹 Enviando para:",
            SHEETS_URL
        )

        json_data = ujson.dumps(payload)

        r = urequests.post(
            SHEETS_URL,
            data=json_data
        )

        print("Resposta recebida:")
        print(r.text)

        if r.status_code == 200:

            contador_sheets += 1

            print(
                f"☁️ Sheets atualizado #{contador_sheets}"
            )

        else:

            print(
                f"⚠️ Erro HTTP {r.status_code}"
            )

            print(
                "❌ Conteúdo de resposta:",
                r.text
            )

        r.close()

    except Exception as e:

        print(
            "❌ Erro ao enviar Sheets:",
            e
        )
