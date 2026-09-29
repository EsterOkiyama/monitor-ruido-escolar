from config import ARQ_DB, ARQ_CSV, LIMITE_DB
from sheets import enviar_sheets
import time

historico_db = []

def salvar_db(db, rtc, enviar=False):
    status = "Alerta" if db>=LIMITE_DB else ("Atenção" if db>=60 else "Bom")
    t = rtc.datetime()
    timestamp = int(time.mktime(t))
    
    try:
        with open(ARQ_DB, "a") as f:
            f.write(f"{timestamp},{db},{status}\n")
    except:
        pass

    historico_db.append(db)
    if len(historico_db) > 50:  # manter últimos 50 valores
        historico_db.pop(0)

    alert_pct = len([d for d in historico_db if d>=LIMITE_DB]) / len(historico_db) * 100

    # Atualiza CSV
    try:
        with open(ARQ_CSV, "w") as f:
            f.write("timestamp,db,status\n")
            dados = open(ARQ_DB).readlines()[-200:]
            f.write("".join(dados))
    except:
        pass

    # Envia para Sheets se solicitado
    if enviar:
        enviar_sheets(db, status, alert_pct, timestamp)

    return status, alert_pct, timestamp

def resetar_db():
    try:
        open(ARQ_DB, "w").close()
        historico_db.clear()
        print("DB resetado")
    except:
        pass