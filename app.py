from flask import Flask
from flask import render_template
from flask import request
import requests
import sys
from flask_sqlalchemy import SQLAlchemy
from flask import abort, redirect, url_for
from flask import flash
import config
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.secret_key = "super secret key"
db = SQLAlchemy(app)


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)


db.create_all()
db.session.query(City).delete()
db.session.commit()


@app.route('/')
def index():
    cities = City.query.all()
    citiesdata = {}
    if cities:
        for city in cities:
            link = "http://api.openweathermap.org/data/2.5/weather?q=%s&APPID=%s&units=metric" % (city.name,config.api_key)
            r = requests.get(link)
            weather = r.json()
            print(weather)
            weatherdata = {"name": weather['name'],
                           "temp": int(weather['main']['temp']),
                           "state": weather['weather'][0]['main']}
            citiesdata[city] = weatherdata

        print(citiesdata)
        return render_template('index.html', weather=citiesdata)
    else:
        return render_template('index.html')


@app.route('/add', methods=['POST'])
def add_city():
    city = request.form['city_name']
    exists = db.session.query(City.id).filter_by(name=city).first() is not None
    print(exists)
    if city:
        if exists:
            flash("The city has already been added to the list!")

        elif requests.get(
                "http://api.openweathermap.org/data/2.5/weather?q=%s&APPID=%s&units=metric" % (city,config.api_key)).status_code != 200:
            flash("The city doesn't exist!")

        else:
            dbcity = City(name=city)
            db.session.add(dbcity)
            db.session.commit()

    return redirect('/')


@app.route('/delete/<city_id>', methods=['GET', 'POST'])
def delete(city_id):
    city = City.query.filter_by(id=city_id).first()
    db.session.delete(city)
    db.session.commit()
    print("delete called")
    return redirect('/')


# don't change the following way to run flask:
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
