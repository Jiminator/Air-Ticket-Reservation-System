from app import *


# Define route for viewing flights
@app.route('/viewFlights')
def view_flights():
    cursor = conn.cursor()
    query = "SELECT * FROM flight WHERE departure_date_time > NOW()"
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return render_template('viewFlights.html', flights=data)


# Search flights
@app.route('/flightSearch', methods=['GET', 'POST'])
def flight_search():
    sourceairport = request.form['sourceairport']
    destairport = request.form['destairport']
    departdate = request.form['departdate']
    returndate = request.form['returndate']
    flightsearch = []

    flightsearch.append(str(sourceairport) + '%')
    flightsearch.append(str(destairport) + '%')
    flightsearch.append(str(departdate) + '%')
    cursor = conn.cursor()


    query1 = """
    SELECT * FROM flight WHERE arrival_airport_name LIKE %s
      AND departure_airport_name LIKE %s AND DATE(departure_date_time) LIKE %s 
      AND departure_date_time > NOW()
    """

    cursor = conn.cursor()

    cursor.execute(query1, tuple(flightsearch))
        
    data = cursor.fetchall()
    # checks for round-trips
    if returndate != '' and sourceairport != '' and destairport != '' and departdate != '' and returndate > departdate:
        flightsearch[0] = destairport
        flightsearch[1] = sourceairport
        flightsearch[2] = returndate
        cursor.execute(query1, tuple(flightsearch))
        data += cursor.fetchall()
    cursor.close()
    return render_template('viewFlights.html', flights=data)

@app.route('/addFlight')
def add_flight():
    #cursor used to send queries
    username = session['username']
    cursor = conn.cursor()

    airline_query = '''
    SELECT airline_name
    FROM airlineStaff 
    WHERE username = %s
    '''
    cursor.execute(airline_query, (username))
    airline = cursor.fetchone()

    #executes query
    query = '''
    SELECT flight.airline_name, flight_number, departure_date_time, arrival_date_time, flight_status, base_price, departure_airport_name, arrival_airport_name, airplane_ID 
    FROM airlineStaff, flight 
    WHERE airlineStaff.airline_name = flight.airline_name AND DATEDIFF(DATE(departure_date_time),CURRENT_DATE()) <= 30 AND DATEDIFF(DATE(departure_date_time), CURRENT_DATE()) >= 0
    '''
    cursor.execute(query)
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
    return render_template('addFlight.html', flights = data, airport = airp_data, ID = airpID_data)


@app.route('/addFlightResult', methods=['GET', 'POST'])
def add_flight_result():
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
    cursor.execute(airline_query, (username))
    airline = cursor.fetchone()

    query = 'SELECT * FROM flight WHERE airline_name = %s AND flight_number = %s AND departure_date_time = %s'
    cursor.execute(query, (airline['airline_name'], flightnum, depdatetime))
    data = cursor.fetchone()

    error = None

    if (data):
        # returns an error message to the html page
        error = 'Flight already exists'
        return render_template('addFlight.html', error=error)
    else:
        ins = 'INSERT INTO flight VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, (
        airline['airline_name'], flightnum, depdatetime, arrdatetime, price, status, depairp, arrairp,
        airplaneID))
        conn.commit()
        cursor.close()
        return redirect(url_for('add_flight'))
