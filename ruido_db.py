from config import (
    ARQ_DB,
    ARQ_CSV,
    LIMITE_BOM,
    LIMITE_ALERTA
)

from sheets import enviar_sheets

historico_db = []


def gerar_timestamp(rtc):

    t = rtc.datetime()

    return (
        f"{t[0]:04d}"
        f"{t[1]:02d}"
        f"{t[2]:02d}_"
        f"{t[4]:02d}"
        f"{t[5]:02d}"
        f"{t[6]:02d}"
    )


def salvar_db(db, rtc, ambiente, enviar=False):

    if db >= LIMITE_ALERTA:
        status = "Alerta"

    elif db >= LIMITE_BOM:
        status = "Atenção"

    else:
        status = "Bom"

    timestamp = gerar_timestamp(rtc)

    try:

        with open(ARQ_DB, "a") as f:

            f.write(
                f"{timestamp},{db},{status},{ambiente}\n"
            )

    except:
        pass

    historico_db.append(db)

    if len(historico_db) > 50:
        historico_db.pop(0)

    if len(historico_db) > 0:

        alert_pct = (
            len(
                [
                    d
                    for d in historico_db
                    if d >= LIMITE_ALERTA
                ]
            )
            /
            len(historico_db)
            * 100
        )

    else:

        alert_pct = 0

    try:

        with open(ARQ_CSV, "w") as f:

            f.write(
                "timestamp,db,status,ambiente\n"
            )

            with open(
                ARQ_DB,
                "r"
            ) as db_file:

                dados = db_file.readlines()[-200:]

            f.write(
                "".join(dados)
            )

    except Exception as e:

        print(
            "Erro CSV:",
            e
        )

    if enviar:

        enviar_sheets(
            db,
            status,
            alert_pct,
            timestamp
        )

    return (
        status,
        alert_pct,
        timestamp
    )

def resetar_db():

    try:

        open(
            ARQ_DB,
            "w"
        ).close()

        historico_db.clear()

        print(
            "DB resetado"
        )

    except:
        pass
