#!/usr/bin/env python3
import serial
import time
import sys
from flask import Flask, jsonify
import threading

app = Flask(__name__)

class Controller:
    def __init__(self, port):
        self.port = port
        self.serial = None
        self.co2 = 400
        self.temp = 22
        self.window_open = False
    
    def run_sensor(self):
        self.serial = serial.Serial(self.port, 9600, timeout=1)
        print(f"Контроллер: {self.port}")
        
        while True:
            if self.serial.in_waiting:
                line = self.serial.readline().decode().strip()
                co2_str, temp_str = line.split(',')
                self.co2 = float(co2_str)
                self.temp = float(temp_str)
                
                if (self.co2 > 800 or self.temp >28) and not self.window_open:
                    self.serial.write(b"OPEN\n")
                    self.window_open = True
                    print("Открыл окно")
                elif self.co2 < 400 and self.temp <20 and self.window_open:
                    self.serial.write(b"CLOSE\n")
                    self.window_open = False
                    print("Закрыл окно")
                
                print(f"CO2: {self.co2:.0f} | Temp: {self.temp:.0f}")
            
            time.sleep(1)

controller = Controller(sys.argv[1])

@app.route('/')
def index():
    return """
    <html><body>
        <h1>Контроль воздуха</h1>
        <p>CO2: <span id="co2">0</span></p>
        <p>Темп: <span id="temp">0</span></p>
        <p>Окно: <span id="window">закрыто</span></p>
        <button onclick="send('open')">Открыть</button>
        <button onclick="send('close')">Закрыть</button>
        <script>
            function update() {
                fetch('/data').then(r => r.json()).then(d => {
                    document.getElementById('co2').textContent = d.co2;
                    document.getElementById('temp').textContent = d.temp;
                    document.getElementById('window').textContent = 
                        d.window ? 'открыто' : 'закрыто';
                });
            }
            function send(cmd) {
                fetch('/command/' + cmd);
            }
            setInterval(update, 2000);
            update();
        </script>
    </body></html>
    """

@app.route('/data')
def data():
    return jsonify({
        "co2": controller.co2,
        "temp": controller.temp,
        "window": controller.window_open
    })

@app.route('/command/<cmd>')
def command(cmd):
    if cmd == 'open' and controller.serial:
        controller.serial.write(b"OPEN\n")
        controller.window_open = True
    elif cmd == 'close' and controller.serial:
        controller.serial.write(b"CLOSE\n")
        controller.window_open = False
    return "OK"

if __name__ == "__main__":
    sensor_thread = threading.Thread(target=controller.run_sensor, daemon=True)
    sensor_thread.start()
    app.run(host='0.0.0.0', port=5000)