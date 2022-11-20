from app import *


# Home page for staff
@app.route('/staffHome')
def staffHome():
    username = session['username']
    cursor = conn.cursor()

    query = 'SELECT * FROM airlinestaff WHERE username = %s'
    cursor.execute(query, (username))

    userdata = cursor.fetchone()
    query = """
            SELECT DISTINCT
                arrival_airport_name,
                COUNT(*) AS ticketCount
            FROM
                purchase natural join flight natural join ticket
            WHERE
                DATE(purchase_date_time) >= DATE_ADD(CURRENT_DATE, INTERVAL -3 MONTH)
            GROUP BY
                arrival_airport_name
            ORDER BY
                ticketCount
            DESC
                LIMIT 3
            """
    cursor.execute(query)
    topdestsmonth = cursor.fetchall()
    query = """
            SELECT DISTINCT
                arrival_airport_name,
                COUNT(*) AS ticketCount
            FROM
                purchase natural join flight natural join ticket
            WHERE
                DATE(purchase_date_time) >= DATE_ADD(CURRENT_DATE, INTERVAL -1 YEAR)
            GROUP BY
                arrival_airport_name
            ORDER BY
                ticketCount
            DESC
            LIMIT 3
            """
    cursor.execute(query)
    topdestsyear = cursor.fetchall()

    query = '''
    SELECT * 
    FROM flight 
    WHERE flight.airline_name = %s AND DATEDIFF(DATE(departure_date_time),CURRENT_DATE()) <= 30 
    AND DATEDIFF(DATE(departure_date_time), CURRENT_DATE()) >= 0;
    '''
    # default flight view within 30 days
    cursor.execute(query, (userdata['airline_name']))
    # stores the results in a variable
    flights_data = cursor.fetchall()
    cursor.close()
    return render_template('staffHome.html', airlinestaff=userdata, topdestsmonth=topdestsmonth,
                           topdestsyear=topdestsyear, flights=flights_data)


# Define route for passenger list
@app.route('/passengerList/<airline_name>/<flight_number>/<departure_date_time>/')
def passengerList(airline_name, flight_number, departure_date_time):
    # cursor used to send queries
    cursor = conn.cursor()
    # executes query
    query = '''
    SELECT name, phone_number, passport_number, passport_expiration
    FROM customer, purchase, ticket 
    WHERE customer.email = purchase.email AND purchase.ticket_ID = ticket.ticket_ID
    AND airline_name = %s AND flight_number = %s AND departure_date_time = %s
    '''
    # default flight view within 30 days
    cursor.execute(query, (airline_name, flight_number, departure_date_time))
    # stores the results in a variable
    data = cursor.fetchall()
    # use fetchall() if you are expecting more than 1 data row
    cursor.close()
    return render_template('passengerList.html', passenger = data)


# Logout for staff
@app.route('/staffLogout')
def logoutStaff():
    session.pop('username')
    return redirect('staffLogin')
