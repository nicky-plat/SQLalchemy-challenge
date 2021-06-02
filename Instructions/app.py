# Import Flask
from flask import Flask, jsonify

# Dependencies and Setup
import numpy as np
import datetime as dt

# Python SQL Toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.pool import StaticPool

##############################################
# Database Setup
##############################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={"check_same_thread": False}, poolclass=StaticPool, echo=True)

# Reflect Existing Database Into a New Model
Base = automap_base()
# Reflect the Tables
Base.prepare(engine, reflect=True)

# Save References to Each Table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create Session from Python to the DB
session = Session(engine)

##############################################
# Flask Setup
##############################################

app = Flask(__name__)

##############################################
# Flask Routes
##############################################

# # Home Route
# @app.route("/")
# def welcome():
#     return """<html>

# Precipitation Route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Convert the query results to a dictionary using 'date' as the Key and 'prcp' as the Value
    # Calculate the date 1 year ago from the last datapoint in the Database
    year_prior = dt.date(2017,8,23) - dt.timedelta(days=365)
    # Design a Query to retrieve the last 12 months of precipitation data selecting only the 'date' and 'prcp' values
    precip_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= year_prior).\
        order_by(Measurement.date).all()
    # Convert list of tuples into a dictionary
    precip_data_list = dict(precip_data)
    # Return JSON representation of the dictionary
    return jsonify(precip_data_list)

# Station Route
@app.route("/api/v1.0/stations")
def stations():
    # Return a JSON list from the dataset
    stations_all = session.query(Station.station, Station.name).all()
    # Convert list of tuples into a normal list
    station_list = list(stations_all)
    # Return JSON list of stations from the dataset
    return jsonify(station_list)

# TOBS Route
@app.route("/api/v1.0/tobs")
def tobs():
    # Query for the dates and temperature observations from a year from the last data point
    year_prior = dt.date(2017,8,23) - dt.timedelta(days=365)
    # Design a Query to retrieve the last 12 months of precipitation data selecting only the 'date' and 'prcp' values
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= year_prior).\
        order_by(Measurement.date).all()
    # Convert list of tuples to a normal list
    tobs_data_list = list(tobs_data)
    # Return JSON list of temperature observations (tobs) for the previous year
    return jsonify(tobs_data_list)

# Start Day Route
@app.route("/api/v1.0/<start>")
def start_day(start):
    start_day = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        group_by(Measurement.date).all()
    # Convert list of tuples into a normal list
    start_day_list = list(start_day)
    # Return JSON list of min temp, avg temp and max temp for a given start range
    return jsonify(start_day_list)

# Start-End Day Route
@app.route("/api/v1.0/<start>/<end>")