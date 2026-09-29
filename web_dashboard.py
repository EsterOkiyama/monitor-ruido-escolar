import uasyncio as asyncio
import socket
from config import ARQ_DB, ESCOLA

async def web_server(ip):
    async def handle_client(conn):
        try:
            data = conn.recv(1024)
            try:
                dados = open(ARQ_DB).readlines()
            except:
                dados = []

            ultima = float(dados[-1].split(',')[1]) if dados else 0
            alerta = sum(1 for d in dados[-20:] if float(d.split(',')[1])>=70)

            html = f"""
            <!DOCTYPE html>
            <html><head>
            <title>Ruído {ESCOLA}</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            </head><body>
            <h1>Monitor Ruído {ESCOLA}</h1>
            <canvas id="grafico" width="400" height="200"></canvas>
            <script>
            const ctx = document.getElementById('grafico').getContext('2d');
            const chart = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: [{','.join([str(i) for i in range(len(dados[-50:]))])}],
                    datasets: [{{
                        label: 'dB',
                        data: [{','.join([d.split(',')[1] for d in dados[-50:]])}],
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1
                    }}]
                }},
                options: {{responsive:true,animation:false}}
            }});
            </script>
            <p>Último: {ultima} dB | Alertas: {alerta}/20</p>
            <a href="/csv">Download CSV</a>
            </body></html>"""

            if b'csv' in data:
                csv_data = "timestamp,db,status\n" + ("".join(dados[-200:]))
                conn.send(f"HTTP/1.1 200 OK\r\nContent-Type:text/csv\r\nContent-Disposition:attachment;filename=ruido.csv\r\n\r\n{csv_data}".encode())
            else:
                conn.send(("HTTP/1.1 200 OK\r\nContent-Type:text/html\r\n\r\n" + html).encode())
        except Exception as e:
            print("Erro client:", e)
        finally:
            conn.close()

    async def server_loop():
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', 80))
        s.listen(5)
        s.setblocking(False)
        print(f"Web server rodando: http://{ip}")

        while True:
            try:
                conn, addr = s.accept()
                conn.setblocking(False)
                asyncio.create_task(handle_client(conn))
            except:
                await asyncio.sleep(0.1)

    await server_loop()