from app import *
from datetime import datetime, date


# Define route for viewing flights
@app.route('/viewFlights')
def view_flights():
    cursor = conn.cursor()
    display = """
        SELECT DISTINCT *
        FROM flight
        WHERE departure_date_time > NOW()
        ORDER BY `flight`.`departure_date_time` ASC
    """
    cursor.execute(display)
    flightdata = cursor.fetchall()
    cursor.close()
    return render_template('viewFlights.html', flights=flightdata)


# Search flights
@app.route('/flightSearch', methods=['GET', 'POST'])
def flight_search():
    cursor = conn.cursor()
    departPort = request.form['departureairport']
    arrivPort = request.form["arrivalairport"]
    departdate = request.form["departdate"]
    returndate = request.form["returndate"]

    filter = """
        SELECT DISTINCT *
        FROM flight
        WHERE departure_date_time > NOW()
    """
    variables = []
    if departPort:
        filter += ' AND departure_airport_name=%s'
        variables.append(departPort)
    if arrivPort:
        filter += ' AND arrival_airport_name=%s'
        variables.append(arrivPort)
    if departdate:
        filter += ' AND departure_date_time >= %s'
        variables.append(departdate)
    filter += ' ORDER BY departure_date_time ASC;'
    if len(variables):
        cursor.execute(filter, tuple(variables))
    else:
        cursor.execute(filter)
    data = cursor.fetchall()
    # round-trip
    if returndate != '' and departPort != '' and arrivPort != '' and departdate != '' and returndate >= departdate:
        variables[0] = arrivPort
        variables[1] = departPort
        variables[2] = returndate
        cursor.execute(filter, tuple(variables))
        data += cursor.fetchall()
    cursor.close()
    return render_template('viewFlights.html', flights=data)


# allows staff to add flight to database
@app.route('/addFlight')
def add_flight():
    try:
        username = session['username']
    except Exception:
        message = 'Please Login or Create an Account'
        return render_template('staffLogin.html', error=message)
    cursor = conn.cursor()

    airline_query = '''
    SELECT airline_name
    FROM airlineStaff
    WHERE username = %s
    '''
    cursor.execute(airline_query, username)
    airline = cursor.fetchone()

    query = '''
    SELECT DISTINCT flight.airline_name, flight_number, departure_date_time, arrival_date_time, flight_status, base_price, departure_airport_name, arrival_airport_name, airplane_ID
    FROM airlineStaff, flight
    WHERE flight.airline_name = %s AND DATEDIFF(DATE(departure_date_time),CURRENT_DATE()) <= 30 AND DATEDIFF(DATE(departure_date_time), CURRENT_DATE()) >= 0
    '''
    cursor.execute(query, airline['airline_name'])
    data = cursor.fetchall()
    airp_query = '''
    SELECT airport_name
    FROM airport
    '''
    cursor.execute(airp_query)
    airp_data = cursor.fetchall()
    airpID_query = '''
    SELECT airplane_ID
    FROM airplane
    WHERE airline_name = %s
    '''
    cursor.execute(airpID_query, (airline['airline_name']))
    airpID_data = cursor.fetchall()
    cursor.close()
    return render_template('staffAddFlight.html', flights=data, airport=airp_data, ID=airpID_data)


# form for staff to add flight
@app.route('/addFlightForm', methods=['GET', 'POST'])
def add_flight_form():
    try:
        username = session['username']
    except Exception:
        message = 'Please Login or Create an Account'
        return render_template('staffLogin.html', error=message)
    cursor = conn.cursor()

    airline_query = '''
        SELECT airline_name
        FROM airlineStaff
        WHERE username = %s
        '''
    cursor.execute(airline_query, username)
    airline = cursor.fetchone()

    # executes query
    query = '''
        SELECT DISTINCT flight.airline_name, flight_number, departure_date_time, arrival_date_time, flight_status, base_price, departure_airport_name, arrival_airport_name, airplane_ID
        FROM airlineStaff, flight
        WHERE flight.airline_name = %s AND DATEDIFF(DATE(departure_date_time),CURRENT_DATE()) <= 30 AND DATEDIFF(DATE(departure_date_time), CURRENT_DATE()) >= 0
        '''
    cursor.execute(query, airline['airline_name'])
    data = cursor.fetchall()
    airp_query = '''
        SELECT airport_name
        FROM airport
        '''
    cursor.execute(airp_query)
    airp_data = cursor.fetchall()
    airpID_query = '''
        SELECT airplane_ID
        FROM airplane
        WHERE airline_name = %s
        '''
    cursor.execute(airpID_query, (airline['airline_name']))
    airpID_data = cursor.fetchall()

    flightnum = request.form['flight_number']
    depdatetime = request.form['departure_date_time']
    arrdatetime = request.form['arrival_date_time']
    status = request.form['status']
    price = request.form['price']
    depairp = request.form['departure_airport_name']
    arrairp = request.form['arrival_airport_name']
    airplaneID = request.form['airplaneID']
    username = session['username']

    cursor = conn.cursor()
    airline_query = '''
    SELECT airline_name
    FROM airlineStaff
    WHERE username = %s
    '''
    cursor.execute(airline_query, username)
    airline = cursor.fetchone()

    query = 'SELECT DISTINCT * FROM flight WHERE airline_name = %s AND flight_number = %s AND departure_date_time = %s'
    cursor.execute(query, (airline['airline_name'], flightnum, depdatetime))
    final_data = cursor.fetchone()

    if final_data:
        error = 'Flight already exists'
        return render_template('staffAddFlight.html', flights=data, airport=airp_data, ID=airpID_data, error=error)
    else:
        airplaneID_query = '''
        SELECT departure_date_time, arrival_date_time
        FROM flight
        WHERE airplane_ID = %s
        '''
        cursor.execute(airplaneID_query, airplaneID)
        impossible_dates = cursor.fetchall()
        f = '%Y-%m-%d %H:%M:%S'
        stripped = depdatetime.strip()
        departure_date_time = datetime.strptime(stripped, f)
        for date in impossible_dates:
            if date['departure_date_time'] <= departure_date_time <= date['arrival_date_time']:
                error = 'Plane is in the air at that time.'
                return render_template('staffAddFlight.html', flights=data, airport=airp_data, ID=airpID_data, error=error)
        ins = 'INSERT INTO flight VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(ins,
            (airline['airline_name'], flightnum, depdatetime, arrdatetime, price, status, depairp, arrairp, airplaneID))
        conn.commit()
        cursor.close()
        return redirect(url_for('add_flight'))
