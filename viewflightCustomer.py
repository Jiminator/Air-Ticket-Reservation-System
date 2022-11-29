from app import *


# Define route for viewing flights
@app.route('/viewflightCustomers')
def view_flights():
    cursor = conn.cursor()
    query = """
    SELECT airline_name, flight_number, departure_date_time, arrival_date_time,	base_price, flight_status, 
    departure_airport_name, arrival_airport_name, airplane_ID	

    FROM ticket NATURAL JOIN purchase NATURAL JOIN flight

    WHERE email = %s;
    """
    
    
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return render_template('viewflights.html', flights=data)


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
    return render_template('viewflights.html', flights=data)