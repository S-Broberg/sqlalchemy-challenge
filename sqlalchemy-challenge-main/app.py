import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.sql import exists  
from flask import Flask, jsonify
import re
import datetime as dt
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)


@app.route("/api/v1.0/precipitation") 
def precipitation():
    session = Session(engine)

    results = (session.query(Measurement.date, Measurement.tobs)
                 .order_by(Measurement.date))
        
    precipitation_value = []
    for each_row in results:
        dt_dict = {}
        dt_dict["date"] = each_row.date
        dt_dict["tobs"] = each_row.tobs
        precipitation_value.append(dt_dict)
    return jsonify(precipitation_value)


@app.route("/api/v1.0/stations") 
def stations():
    session = Session(engine)
    results = session.query(Station.name).all()
    station_details = list(np.ravel(results))
    return jsonify(station_details)

@app.route("/api/v1.0/tobs") 
def tobs():
    
    session = Session(engine)

    
    last_date = (session.query(Measurement.date)
                          .order_by(Measurement.date
                          .desc())
                          .first())
    
    last_date_str = str(last_date)
    last_date_str = re.sub("'|,", "",last_date_str)
    last_date_obj = dt.datetime.strptime(last_date_str, '(%Y-%m-%d)')
    query_start_date = dt.date(last_date_obj.year, last_date_obj.month, last_date_obj.day) - dt.timedelta(days=366)
     
    query_station = (session.query(Measurement.station, func.count(Measurement.station))
                             .group_by(Measurement.station)
                             .order_by(func.count(Measurement.station).desc())
                             .all())
    
    station_t = query_station[0][0]
    print(station_t)

    results = (session.query(Measurement.station, Measurement.date, Measurement.tobs)
                      .filter(Measurement.date >= query_start_date)
                      .filter(Measurement.station == station_t)
                      .all())
@app.route("/api/v1.0/<start>") 
def startD(start):

    session = Session(engine)
    max_range = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    max_range_str = str(max_range)
    max_range_str = re.sub("'|,", "",max_range_str)
    print (max_range_str)

    min_range = session.query(Measurement.date).first()
    min_range_str = str(min_range)
    min_range_str = re.sub("'|,", "",min_range_str)
    print (min_range_str)


    
    entry_test = session.query(exists().where(Measurement.date == start)).scalar()
 
    if entry_test:

    	results = (session.query(func.min(Measurement.tobs)
    				 ,func.avg(Measurement.tobs)
    				 ,func.max(Measurement.tobs))
    				 	  .filter(Measurement.date >= start).all())

    	tmin =results[0][0]
    	tavg ='{0:.4}'.format(results[0][1])
    	tmax =results[0][2]
    
    	result_printout =( ['Entered Start Date: ' + start,
    						'The lowest Temperature was: '  + str(tmin) + ' F',
    						'The average Temperature was: ' + str(tavg) + ' F',
    						'The highest Temperature was: ' + str(tmax) + ' F'])
    	return jsonify(result_printout)

    return jsonify({"error": f"Input Date {start} not valid. Date Range is {min_range_str} to {max_range_str}"}), 404

@app.route("/api/v1.0/<start>/<end>") 
def start_end(start, end):

    session = Session(engine)

    max_range = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    max_range_str = str(max_range)
    max_range_str = re.sub("'|,", "",max_range_str)
    print (max_range_str)

    min_range = session.query(Measurement.date).first()
    min_range_str = str(min_range)
    min_range_str = re.sub("'|,", "",min_range_str)
    print (min_range_str)

    entry_test_start = session.query(exists().where(Measurement.date == start)).scalar()
 	
    entry_test_end = session.query(exists().where(Measurement.date == end)).scalar()

    if entry_test_start and entry_test_end:

    	results = (session.query(func.min(Measurement.tobs)
    				 ,func.avg(Measurement.tobs)
    				 ,func.max(Measurement.tobs))
    					  .filter(Measurement.date >= start)
    				  	  .filter(Measurement.date <= end).all())

    	tmin =results[0][0]
    	tavg ='{0:.4}'.format(results[0][1])
    	tmax =results[0][2]
    
    	results2 =(tmin, tavg, tmax)
    	return jsonify(results2)

    if not entry_test_start and not entry_test_end:
    	return jsonify({"{start} and {end} not valid dates. Date Range is {min_range_str} to {max_range_str}"})

    if not entry_test_start:
    	return jsonify({"{start} not a valid date. Date Range is {min_range_str} to {max_range_str}"})

    if not entry_test_end:
    	return jsonify({"{end} not a valid date. Date Range is {min_range_str} to {max_range_str}"})

if __name__ == '__main__':
    app.run(debug=True)