#!/usr/bin/env python3
import serial
import time
import random
import sys

class AirSimulator:
    def __init__(self, port):
        self.port = port
        self.serial = None
        self.co2 = 400
        self.temp = 22
        self.window_open = False
    
    def run(self):
        self.serial = serial.Serial(self.port, 9600, timeout=1)
        print(f"Воздух: {self.port}")
        
        while True:
            if self.serial.in_waiting:
                cmd = self.serial.readline().decode().strip()
                if cmd == "OPEN":
                    self.window_open = True
                elif cmd == "CLOSE":
                    self.window_open = False
            
            if self.window_open:
                self.co2 -= random.uniform(0, 50)
                self.temp -= random.uniform(0, 1)
            else:
                self.co2 += random.uniform(0, 20)
                self.temp += random.uniform(0, 0.3)
            
            data = f"{self.co2:.1f},{self.temp:.1f}\n"
            self.serial.write(data.encode())
            
            print(f"CO2: {self.co2:.0f}, TEMP: {self.temp:.1f}, WINDOW: {self.window_open}")
            time.sleep(2)

if __name__ == "__main__":
    AirSimulator(sys.argv[1]).run()