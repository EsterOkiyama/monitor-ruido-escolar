from machine import Pin, PWM
import neopixel
import time

class BitDogLab:
    def __init__(self, led_pin=7, num_leds=25, buzzer_pin=21, botao_pin=16):
        self.np = neopixel.NeoPixel(Pin(led_pin), num_leds)
        self.buzzer = PWM(Pin(buzzer_pin))
        self.botao = Pin(botao_pin, Pin.IN, Pin.PULL_UP)
        
        self.icone_bom = [[0,1,1,1,0],
                          [1,0,0,0,1],
                          [1,0,0,0,1],
                          [1,0,0,0,1],
                          [0,1,1,1,0]]
        self.icone_atencao = [[0,0,1,0,0],
                              [0,1,1,1,0],
                              [1,1,1,1,1],
                              [0,0,1,0,0],
                              [0,0,1,0,0]]
        self.icone_alerta = [[1,0,0,0,1],
                             [0,1,0,1,0],
                             [0,0,1,0,0],
                             [0,1,0,1,0],
                             [1,0,0,0,1]]
    
    def desenhar_icone(self, matriz, cor):
        for y in range(5):
            for x in range(5):
                self.np[y*5+x] = cor if matriz[y][x] else (0,0,0)
        self.np.write()
    
    def buzzer_alert(self, duracao_ms=200, freq=1800, duty=30000):
        self.buzzer.freq(freq)
        self.buzzer.duty_u16(duty)
        time.sleep_ms(duracao_ms)
        self.buzzer.duty_u16(0)
    
    def botao_pressionado(self):
        return not self.botao.value()