import sqlite3

db = sqlite3.connect('meteo.db')
cur = db.cursor()

cur.execute("SELECT count(*) FROM meteo")

bd_mesure = cur.fetchone()[0]

print("Nombre de mesures:       ", bd_mesure)


cur.execute("SELECT day, month, year, hour, minute, second FROM meteo")
pre_date = cur.fetchone()

print("Première mesure:          le {}/{}/{} à {}:{}:{}".format(*pre_date))


cur.execute("SELECT min(temp), avg(temp), max(temp) from meteo")
stat = cur.fetchone()

print()

print("""Température:
-minimale:                {} °C
-moyenne:                 {:0.1f} °C
-maximale:                {} °C""".format(*stat))

print()


cur.execute("SELECT min(pressure), avg(pressure), max(pressure) from meteo")
stat = map(lambda x: x/100,cur.fetchone())

print("""Pression:
-minimale:                {} hPa
-moyenne:                 {:0.1f} hPa
-maximale:                {} hPa""".format(*stat))
