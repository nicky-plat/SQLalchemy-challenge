from flask import Flask, jsonify, render_template
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.orm.session import scoped_session, sessionmaker


##############################################
# Database Setup
##############################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect Existing Database Into a New Model
Base = automap_base()
# Reflect the Tables
Base.prepare(engine, reflect=True)

# Save References to Each Table
Measurement = Base.classes.measurement
Station = Base.classes.station

last_date = dt.date(2017, 8, 23)
year_prior = last_date - dt.timedelta(days=365)

# Create Session from Python to the DB
session_factory = sessionmaker(bind=engine)
session = scoped_session(session_factory)

##############################################
# Flask Setup
##############################################

app = Flask(__name__)

##############################################
# Flask Routes
##############################################

# Home Route
@app.route("/")
def welcome():
    """List of all available API Routes."""
    return (
        f"Available Routes:<br />"
        f"<br />"
        f"/api/v1.0/precipitation<br />"
        f"/api/v1.0/stations<br />"
        f"/api/v1.0/tobs<br />"
        f"/api/v1.0/temp/start/end<br />"
        )

# Precipitation Route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Design a Query to retrieve the last 12 months of precipitation data selecting only the 'date' and 'prcp' values
    precip_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= year_prior).all()
    precip = {}
    for result in precip_data:
        precip_list = {result.date: result.prcp, "prcp": result.prcp}
        precip.update(precip_list)
    # Return JSON representation of the dictionary
    return jsonify(precip)

# Station Route
@app.route("/api/v1.0/stations")
def stations():
    # Return a JSON list from the dataset
    stations_all = session.query(Station.station).all()
    # Convert list of tuples into a normal list
    station_dict = list(np.ravel(stations_all))
    # Return JSON list of stations from the dataset
    return jsonify(station_dict)

# TOBS Route
@app.route("/api/v1.0/tobs")
def tobs():
    # Design a Query to retrieve the last 12 months of precipitation data selecting only the 'date' and 'prcp' values
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= year_prior).all()
    # Convert list of tuples to a normal list
    tobs_dict = list(np.ravel(tobs_data))
    # Return JSON list of temperature observations (tobs) for the previous year
    return jsonify(tobs_dict)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def calc_temps(start, end):
    if end != "":
        temp_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), \
            func.max(Measurement.tobs)).filter(Measurement.date.between(year_prior, last_date)).all()
        t_stats = list(np.ravel(temp_stats))
        return jsonify(temp_stats)

    else:
        temp_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), \
            func.max(Measurement.tobs)).filter(Measurement.date > last_date).all()
        t_stats = list(np.ravel(temp_stats))
        return jsonify(temp_stats)


# Define Main behavior
if __name__ == '__main__':
    app.run(debug=True)
