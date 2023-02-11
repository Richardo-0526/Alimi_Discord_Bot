import arrow
import time

now = arrow.now()
print(now.time().hour)
print(now.time().minute)
hour = now.time().hour
minute = now.time().minute
print(now.weekday())



