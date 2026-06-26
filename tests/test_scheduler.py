import time

from scheduler import start_scheduler

start_scheduler()

print("Scheduler iniciado.")

while True:
    time.sleep(1)