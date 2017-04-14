from Adafruit_BMP import BMP085  # pour lire le capteur
import sqlite3  # pour enregistrer les donnees du capteur
import time
import datetime
import subprocess
import os
DB_PATH = '/home/pi/meteo/site/meteo.db'
PHOTO_PATH = "/home/pi/meteo/site/photos/"

ALTITUDE = 232.0  # altitude de la station

TIME_DELAY = 10 * 60  # espace entre deux mesures
DELAY_STEP = 0.25

def db():
    bmp = BMP085.BMP085(mode=BMP085.BMP085_ULTRAHIGHRES)

    db = sqlite3.connect(DB_PATH)
    cursor = db.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS meteo(year INT, month INT,
                      day INT, hour INT, minute INT, second INT, temp REAL,
                      pressure REAL)''')

    db.commit()  # enregistrement
    
    debut = time.time()  # date de debut de la mesure

    while True:
        now = datetime.datetime.now()

        subprocess.call(["fswebcam", "-q", PHOTO_PATH + 
                         "{:02d}-{:02d}-{:02d},{:02d}:{:02d}:{:02d}.jpg".format(
                         now.year, now.month, now.day, now.hour, now.minute,
                         now.second), "-F 20", "-S 19", "-r 160x120"],
                         stdout=subprocess.PIPE)

        if not "{:02d}-{:02d}-{:02d},{:02d}:{:02d}:{:02d}.jpg".format(
                         now.year, now.month, now.day, now.hour, now.minute,
                         now.second) in os.listdir('photos'):  # erreur
            print("ERROR: retrying...")
            continue  # on reessaye jusqu'a ce que ca marche
        else:
            print("   Image correctly saved")

        data = (now.year, now.month, now.day, now.hour, now.minute, now.second,
                bmp.read_temperature(),
                bmp.read_sealevel_pressure(altitude_m=ALTITUDE).__round__(0))
        cursor.execute('''INSERT INTO meteo VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                       data)
        db.commit()  # enregistrement

        print("   "  + str(data[-2:]))

        while debut + TIME_DELAY > time.time():  # permet de prendre en compte
                                                 # le temps d'execution
            time.sleep(DELAY_STEP)
        debut = time.time()
        print("{:02d}-{:02d}-{:02d},{:02d}:{:02d}:{:02d}".format(
                 now.year, now.month, now.day, now.hour, now.minute,
                 now.second))

def txt():  # version sans SQL, juste un fichier texte
    bmp = BMP085.BMP085(mode=BMP085.BMP085_ULTRAHIGHRES)

    while True:
        with open('releve.txt', 'a') as fi:
            data = "'{}', {}, {}\n".format(time.strftime('%Y/%m/%d %H:%M:%S',
            time.localtime()) , bmp.read_temperature(),
            bmp.read_sealevel_pressure())

            print(data)
            fi.write(data)

        time.sleep(60)

if __name__ == '__main__':
    db()
