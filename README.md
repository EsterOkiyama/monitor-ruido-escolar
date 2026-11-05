Monitoramento de Ruído em Ambientes Escolares com IoT
Descrição

Sistema desenvolvido para monitorar níveis de ruído em ambientes escolares utilizando a plataforma BitDogLab, com coleta automática de dados, armazenamento em nuvem e geração de estatísticas para análise acústica.

Versão Utilizada na Coleta Oficial

Data da versão: 02/11/2026

Melhorias Implementadas
Seleção de ambiente por joystick
Funcionamento autônomo com bateria
Interface gráfica no display OLED
Indicadores visuais através da matriz de LEDs
Reconexão automática à rede Wi‑Fi
Registro de data e horário das medições
Armazenamento local em arquivo ruido.txt
Exportação automática em formato CSV
Envio automático para Google Sheets
Classificação automática dos níveis de ruído
Classificação de Ruído
Status	Faixa✅ Bom	Menor que 55 dB
⚠️ Atenção	Entre 55 e 64 dB
🚨 Alerta	Maior ou igual a 65 dB
Funcionalidades Validadas
✅ Wi‑Fi
✅ OLED
✅ Matriz de LEDs
✅ Seleção de ambiente
✅ Registro de ruído
✅ Armazenamento local
✅ Exportação CSV
✅ Google Sheets
✅ Funcionamento com bateria
Tecnologias Utilizadas
MicroPython
ESP32
BitDogLab
Google Apps Script
Google Sheets
OLED SSD1306
Estrutura do Projeto
Plain Text
/
├── main.py
├── oled.py
├── joystick.py
├── ruido.txt
├── medicoes.csv
└── README.md
Objetivo

Avaliar os níveis de ruído em diferentes ambientes escolares e fornecer dados para análise, auxiliando na identificação de locais com maior impacto acústico no processo de ensino e aprendizagem.

Status do Projeto

✅ Projeto concluído e validado em campo.

