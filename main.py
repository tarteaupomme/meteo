from flask import Flask, render_template, url_for, request, send_file
import pygal
import datetime
import sqlite3
import re
import os

db_path = 'meteo.db'

dot = True
human_readable = True
legend = True
temp_scale = 20


db = sqlite3.connect(db_path)
cur = db.cursor()


#######################------graphs-functions-------------#####################


def gen_from_db(restriction=',', freq=1, platform=None):
    db = sqlite3.connect(db_path)
    cur = db.cursor()
    plot = pygal.DateTimeLine(
            x_label_rotation=35, truncate_label=-1,
            x_value_formatter=lambda dt: dt.strftime('%y/%m/%d %H:%M'),
            human_readable=human_readable,
            show_legend=True,
            explicit_size=True,
            show_x_guides=True,
            legend_at_bottom=True)

    data = []

    cur.execute('SELECT * FROM meteo ' + restriction)

    datafetch = cur.fetchall()

    data = [(datetime.datetime(*i[0:6]), i[6]) for i in datafetch]

    plot.add('température', data[::freq], show_dots=dot, secondary=False)

    plot.max_scale = temp_scale
    plot.secondary_range = [965, 1045]
    plot.range = [-10, 30]
    if platform in ('iphone', 'android'):
        plot.width = 450
        plot.height = 700
    else:
        plot.width = 1150
        plot.height = 800

    plot.x_labels = [i[0] for i in data if i[0].hour == 0 and 
                     i[0].minute < 10]
    plot.x_labels = [datetime.datetime(i.year, i.month, i.day, 0, 0, 0) 
                     for i in plot.x_labels]


    data2 = []

    data2 = [(datetime.datetime(*i[0:6]), i[7] / 100) for i in datafetch]

    plot.add('pression', data2[::freq], show_dots=dot, secondary=True)

    return plot.render_data_uri()


def extrem():
    db = sqlite3.connect(db_path)
    cur = db.cursor()
    cur.execute(
    'SELECT year, month, day, hour, minute, second, max(temp) FROM meteo')
    data_temp_max = cur.fetchone()

    cur.execute(
    'SELECT year, month, day, hour, minute, second, min(temp) FROM meteo')
    data_temp_min = cur.fetchone()

    cur.execute(
    'SELECT year, month, day, hour, minute, second, max(pressure) FROM meteo')
    data_pressure_max = cur.fetchone()

    cur.execute(
    'SELECT year, month, day, hour, minute, second, min(pressure) FROM meteo')
    data_pressure_min = cur.fetchone()

    return (data_temp_max, data_temp_min, data_pressure_max, data_pressure_min)


def annuel_stats():
    """renvoie des graph avec la temperature et de la pression a 8h 
    chaque jour de l'annee"""
    today = datetime.datetime.now()
    db = sqlite3.connect(db_path)
    cur = db.cursor()
    cur.execute(
    """SELECT year, month, day, temp FROM meteo WHERE hour=8 AND minute < 10
    AND (year=? OR (year=? and month>=? and day>=?))""",
    (today.year, today.year - 1, today.month, today.day))

    data_temp_matin = [(datetime.datetime(*i[:3]), i[3])
                        for i in cur.fetchall()]
    cur.execute(
    """SELECT year, month, day, pressure FROM meteo WHERE hour==8
    AND minute < 10 AND (year==? OR (year==? and month>=?
    and day>=?))""", (today.year, today.year - 1, today.month, today.day))

    data_pres_matin = [(datetime.datetime(*i[:3]), i[3] / 100)
                       for i in cur.fetchall()]

    temp = pygal.DateTimeLine(
            x_label_rotation=35, truncate_label=-1,
            x_value_formatter=lambda dt: dt.strftime('%Y/%m/%d %H:%M:%S'),
            human_readable=human_readable, show_legend=legend)

    temp.max_scale = temp_scale
#    temp.title = 'Température anuelles'

    pres = pygal.DateTimeLine(
            x_label_rotation=35, truncate_label=-1,
            x_value_formatter=lambda dt: dt.strftime('%Y/%m/%d %H:%M:%S'),
            human_readable=human_readable, show_legend=legend)

#    pres.title = 'Pression anuelles'

    temp.add('8H', data_temp_matin, show_dots=dot)
    pres.add('8H', data_pres_matin, show_dots=dot)

    cur.execute("""SELECT year, month, day, temp FROM meteo WHERE hour==19 AND
     minute < 10 AND (year==? OR (year==? and month>=?
     and day>=?))""", (today.year, today.year - 1, today.month,
                             today.day))

    data_temp_soir = [(datetime.datetime(*i[:3]), i[3]) for i in cur.fetchall()]
    cur.execute("""SELECT year, month, day, pressure FROM meteo WHERE hour==19
    AND minute < 10 AND (year==? OR (year==? and month>=?
    and day>=?))""", (today.year, today.year - 1, today.month, today.day))

    data_pres_soir = [(datetime.datetime(*i[:3]), i[3] / 100)
                       for i in cur.fetchall()]

    temp.add('19H', data_temp_soir, show_dots=dot)
    pres.add('19H', data_pres_soir, show_dots=dot)

    temp.range = [-10, 35]
    pres.range = [945, 1080]

    return temp.render_data_uri(), pres.render_data_uri()



def month_stats_temp():
    """min, moy et max sur chaque mois"""
#    today = datetime.datetime.now()
    db = sqlite3.connect(db_path)
    cur = db.cursor()

    graph = pygal.Bar(human_readable=human_readable)
    graph.x_labels = [i for i in range(1, 13)]
    graph.range = [-10, 35]

    data = []
    for i in range(1, 13):
        cur.execute("""SELECT MIN(temp), year, month, day, hour FROM
                    meteo WHERE month==?""", (i,))

        fetched = cur.fetchone()
        da = fetched[0]
        if da is not None:
            da = da.__round__(1)
        data.append({'value': da,
                     'xlink': url_for('archives', _external=True,
                                      year=fetched[1],
                                      month=fetched[2], day=fetched[3])})

    graph.add('Minimales', data)

    data = []
    for i in range(1, 13):
        cur.execute("SELECT AVG(temp) FROM meteo WHERE month==?", (i,))

        da = cur.fetchone()[0]
        if da is not None:
            da = da.__round__(1)
        data.append(da)

    graph.add('Moyennes', data)
    data = []
    for i in range(1, 13):
        cur.execute("""SELECT MAX(temp), year, month, day, hour FROM
                    meteo WHERE month==?""", (i,))

        fetched = cur.fetchone()
        da = fetched[0]
        if da is not None:
            da = da.__round__(1)
        data.append({'value': da,
                     'xlink': url_for('archives', _external=True,
                                      year=fetched[1],
                                      month=fetched[2], day=fetched[3])})

    graph.add('Maximales', data)

    return graph.render_data_uri()


def format_query(query, var):
	if query == "*":
		return 1
	elif re.search(r'([0-9]+)-([0-9]+)', query) is not None:
		d = tuple(re.findall(r'([0-9]+)-([0-9]+)', query)[0])
		return var + " BETWEEN {} AND {}".format(*d)
	else:
		return var + " == " + query



#####################-----------views-----------###############################

app = Flask(__name__)


@app.route('/')
def home():
    platform = request.user_agent.platform
    if platform in ('android', 'iphone'):
        today = datetime.datetime.now() - datetime.timedelta(1)
    else:
        today = datetime.datetime.now() - datetime.timedelta(2)
    
    plot = gen_from_db("""WHERE (year * 100000000 + month *1000000 + day * 10000 
                       + hour * 100 + minute) >= {}
                      """
					  .format(today.year * 100000000 + today.month * 1000000 +
					          today.day * 10000 + today.hour * 100 + 
                              today.minute),
                       1, platform)

    extremum = extrem()

    return render_template('home.html', plot=plot,
                           max_temp=extremum[0],
                           min_temp=extremum[1], max_pressure=extremum[2],
                           min_pressure=extremum[3], here="home")


@app.route('/stats')
def stats():
    """"statistique annuels"""
    temp, pres = annuel_stats()
    extremum = extrem()
    month_stats = month_stats_temp()

    return render_template('stats.html', temp=temp, pres=pres,
                           max_temp=extremum[0], min_temp=extremum[1],
                           max_pressure=extremum[2], min_pressure=extremum[3],
                           month_stats=month_stats, here="stats")

@app.route('/simple_data')
def simple_data():
    from Adafruit_BMP import BMP085

    bmp = BMP085.BMP085(mode=BMP085.BMP085_ULTRAHIGHRES)
    data = "{}\n{}\n{}\n".format(
        bmp.read_temperature(),
        bmp.read_pressure().__round__(0) / 100,
        bmp.read_sealevel_pressure(240).__round__(0) / 100)

    return data


@app.route('/about')
def about():
    db = sqlite3.connect('meteo.db')
    cur = db.cursor()

    cur.execute("SELECT count(*) FROM meteo")

    nb_mesure = cur.fetchone()[0]

    return render_template('about.html', nb_mesure=nb_mesure, here="about")




@app.route('/archives/')
@app.route('/archives/<year>/')
@app.route('/archives/<year>/<month>/')
@app.route('/archives/<year>/<month>/<day>/')
@app.route('/archives/<year>/<month>/<day>/<hour>')
def archives(year="*", month="*", day="*", hour="*"):
    """renvoie un graph de la periode voulue"""
    
    dyear = format_query(year, "year")
    dmonth = format_query(month, "month")
    dday = format_query(day, "day")
    dhour = format_query(hour, "hour")
    
    try:
        freq = int(request.args.get('freq', ''))
    except:
        freq = 1
    
    query = "WHERE {} AND {} AND {} AND {}".format(dyear, dmonth,dday,
             dhour)


    plot = gen_from_db(query, freq, request.user_agent.platform)

    return render_template('archives.html', plot=plot, year=year, month=month,
                           day=day, hour=hour, here="archives")

@app.route('/photo')
def photo():
    images = os.listdir('photos')
    images.sort()
    return render_template('photo.html', photos=images)

@app.route('/static_image/<image>')
def static_image(image=None):
    return send_file("photos/" + image, mimetype='image/gif')



if __name__ == '__main__':
    app.run('192.168.1.14', 80, debug=True, threaded=True)

