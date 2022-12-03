from app import *


@app.route('/flightRatings')
def flight_ratings():
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
    cursor.execute(airline_query, (username))
    airline = cursor.fetchone()
    query = '''
    SELECT airline_name, flight_number, departure_date_time, CAST(AVG(rating) AS DECIMAL(1,0)) AS avgRating 
    FROM interact WHERE airline_name = %s
    GROUP BY airline_name, flight_number, departure_date_time
    '''
    cursor.execute(query, (airline['airline_name']))
    data = cursor.fetchall()
    cursor.close()
    return render_template('flightRatings.html', rating = data)


@app.route('/allFlightRatings<airlinename>/<flightnum>/<depdatetime>/')
def all_flight_ratings(airlinename, flightnum, depdatetime):
    try:
        username = session['username']
    except Exception:
        message = 'Please Login or Create an Account'
        return render_template('staffLogin.html', error=message)
    cursor = conn.cursor()
    query = '''
    SELECT email, comment, rating
    FROM interact
    WHERE airline_name = %s AND flight_number = %s AND departure_date_time = %s
    '''
    cursor.execute(query, (airlinename, flightnum, depdatetime))
    data = cursor.fetchall()
    cursor.close()
    return render_template('allFlightRatings.html', ratings = data)
