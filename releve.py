from Adafruit_BMP import BMP085
import sqlite3
import time
import datetime
import subprocess

db_path = '/home/pi/meteo/site/meteo.db'
photo_path = "/home/pi/meteo/site/photos/"

def db():
    bmp = BMP085.BMP085(mode=BMP085.BMP085_ULTRAHIGHRES)

    db = sqlite3.connect(db_path)
    cursor = db.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS meteo(year INT, month INT, day INT, hour INT, minute INT, second INT, temp REAL, pressure REAL)''')

    db.commit()

    while True:
        now = datetime.datetime.now()
        data = (now.year, now.month, now.day, now.hour, now.minute, now.second, bmp.read_temperature(), bmp.read_sealevel_pressure(altitude_m=232.0).__round__(0))
        cursor.execute('''INSERT INTO meteo VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', data)
        db.commit()
        subprocess.call(["fswebcam", "-q", photo_path + "{:02d}-{:02d}-{:02d},{:02d}:{:02d}:{:02d}.jpg".format(now.year, now.month, now.day, now.hour, now.minute, now.second), "-F 20", "-S 19", "-r 160x120"])
        print(data)
        time.sleep(60 * 10)

def txt():
    bmp = BMP085.BMP085(mode=BMP085.BMP085_ULTRAHIGHRES)

    while True:
        with open('releve.txt', 'a') as fi:
            data = "'{}', {}, {}\n".format(time.strftime('%Y/%m/%d %H:%M:%S', time.localtime()) , bmp.read_temperature(), bmp.read_sealevel_pressure())

            print(data)
            fi.write(data)

        time.sleep(60)

if __name__ == '__main__':
    db()
