import uasyncio as asyncio
import socket

from config import (
    ARQ_DB,
    ESCOLA,
    LIMITE_ALERTA
)


async def web_server(ip):

    async def handle_client(conn):

        try:

            data = conn.recv(1024)

            try:

                with open(ARQ_DB, "r") as f:
                    dados = f.readlines()

            except:

                dados = []

            # ==========================
            # ESTATÍSTICAS
            # ==========================

            valores = []

            try:

                valores = [
                    float(
                        d.split(",")[1]
                    )
                    for d in dados
                ]

            except:

                valores = []

            ultima = (
                round(valores[-1], 1)
                if valores
                else 0
            )

            media_db = (
                round(
                    sum(valores)
                    / len(valores),
                    1
                )
                if valores
                else 0
            )

            max_db = (
                round(max(valores), 1)
                if valores
                else 0
            )

            min_db = (
                round(min(valores), 1)
                if valores
                else 0
            )

            alerta = sum(
                1
                for d in dados[-20:]
                if float(
                    d.split(",")[1]
                ) >= LIMITE_ALERTA
            )

            # ==========================
            # DADOS DO GRÁFICO
            # ==========================

            labels = ",".join(
                [
                    str(i)
                    for i in range(
                        len(dados[-50:])
                    )
                ]
            )

            pontos = ",".join(
                [
                    d.split(",")[1]
                    for d in dados[-50:]
                ]
            )

            # ==========================
            # HTML
            # ==========================

            html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Monitor de Ruído - {ESCOLA}</title>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>

body {{
    font-family: Arial, sans-serif;
    margin: 20px;
}}

.card {{
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 10px;
    margin: 5px;
    display: inline-block;
    min-width: 150px;
}}

</style>

</head>

<body>

<h1>Monitor de Ruído</h1>

<h3>{ESCOLA}</h3>

<div class="card">
<b>Último Valor</b><br>
{ultima} dB
</div>

<div class="card">
<b>Média</b><br>
{media_db} dB
</div>

<div class="card">
<b>Máximo</b><br>
{max_db} dB
</div>

<div class="card">
<b>Mínimo</b><br>
{min_db} dB
</div>

<div class="card">
<b>Alertas</b><br>
{alerta}/20
</div>

<br><br>

<canvas
id="grafico"
width="400"
height="200">
</canvas>

<script>

const ctx =
document.getElementById(
'grafico'
).getContext('2d');

new Chart(ctx, {{

    type: 'line',

    data: {{

        labels: [{labels}],

        datasets: [{{
            label: 'Ruído (dB)',
            data: [{pontos}],
            borderColor: 'rgb(75,192,192)',
            tension: 0.2
        }}]

    }},

    options: {{
        responsive: true,
        animation: false
    }}

}});

</script>

<p>
IP do dispositivo:
<b>{ip}</b>
</p>

<a href="/csv">
Download CSV
</a>

</body>
</html>
"""

            # ==========================
            # CSV
            # ==========================

            if b"csv" in data:

                csv_data = (
                    "timestamp,db,status\n"
                    + "".join(
                        dados[-200:]
                    )
                )

                conn.send(
                    (
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type:text/csv\r\n"
                        "Content-Disposition:attachment;"
                        "filename=ruido.csv\r\n\r\n"
                        + csv_data
                    ).encode()
                )

            else:

                conn.send(
                    (
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type:text/html\r\n\r\n"
                        + html
                    ).encode()
                )

        except Exception as e:

            print(
                "Erro client:",
                e
            )

        finally:

            conn.close()
    async def server_loop():

        s = socket.socket()

        s.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        s.bind(("0.0.0.0", 8080))

        s.listen(5)

        s.setblocking(False)

        print(
            f"Dashboard: http://{ip}:8080"
        )

        while True:

            try:

                conn, addr = s.accept()

                conn.setblocking(False)

                asyncio.create_task(
                    handle_client(conn)
                )

            except:

                await asyncio.sleep(0.1)

    await server_loop()
