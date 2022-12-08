from app import *


# Home page for staff
@app.route('/staffHome')
def staff_home():
    try:
        username = session['username'] 
    except Exception:
        message = 'Please Login or Create an Account'
        return render_template('staffLogin.html', error=message)
    cursor = conn.cursor()
    query = 'SELECT * FROM airlinestaff WHERE username = %s'
    cursor.execute(query, username)
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
    cursor.execute(query, (userdata['airline_name']))
    flights_data = cursor.fetchall()
    cursor.close()
    return render_template('staffHome.html', airlinestaff=userdata, topdestsmonth=topdestsmonth,
                           topdestsyear=topdestsyear, flights=flights_data)


# Add email to staff
@app.route('/staffAddEmail')
def staff_add_email():
    try:
        username = session['username']
    except Exception:
        message = 'Please Login or Create an Account'
        return render_template('staffLogin.html', error=message)
    return render_template('staffAddEmail.html')


# add email
@app.route('/staffAddEmailForm', methods=['GET', 'POST'])
def staff_add_email_form():
    try:
        username = session['username']
    except Exception:
        message = 'Please Login or Create an Account'
        return render_template('staffLogin.html', error=message)
    email = request.form['email']
    cursor = conn.cursor()
    query = 'SELECT DISTINCT * FROM staffEmail WHERE username = %s AND email = %s'
    cursor.execute(query, (username, email))
    data = cursor.fetchone()
    error = None
    if (data):
        # returns an error message to the html page
        error = 'Email already exists'
        return render_template('staffAddEmail.html', error=error)
    else:
        ins = 'INSERT INTO staffEmail VALUES(%s, %s)'
        cursor.execute(ins, (username, email))
        conn.commit()
        cursor.close()
        return redirect(url_for('staff_add_email'))


# Add phone to staff
@app.route('/staffAddPhone')
def staff_add_phone():
    try:
        username = session['username']
    except Exception:
        message = 'Please Login or Create an Account'
        return render_template('staffLogin.html', error=message)
    return render_template('staffAddPhone.html')


# add phone
@app.route('/staffAddPhoneForm', methods=['GET', 'POST'])
def staff_add_phone_form():
    try:
        username = session['username']
    except Exception:
        message = 'Please Login or Create an Account'
        return render_template('staffLogin.html', error=message)
    phone = request.form['phone']
    cursor = conn.cursor()
    query = 'SELECT DISTINCT * FROM staffPhone WHERE username = %s AND phone_number = %s'
    cursor.execute(query, (username, phone))
    data = cursor.fetchone()
    error = None
    if (data):
        # returns an error message to the html page
        error = 'Phone already exists'
        return render_template('staffAddPhone.html', error=error)
    else:
        ins = 'INSERT INTO staffPhone VALUES(%s, %s)'
        cursor.execute(ins, (username, phone))
        conn.commit()
        cursor.close()
        return redirect(url_for('staff_add_phone'))


# Define route for passenger list
@app.route('/passengerList/<airline_name>/<flight_number>/<departure_date_time>/')
def passenger_list(airline_name, flight_number, departure_date_time):
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
    if airline['airline_name'] != airline_name:
        message = 'You are not logged in to ' + airline_name
        return render_template('staffLogin.html', error=message)
    query = '''
    SELECT name, phone_number, passport_number, passport_expiration
    FROM customer, purchase, ticket 
    WHERE customer.email = purchase.email AND purchase.ticket_ID = ticket.ticket_ID
    AND airline_name = %s AND flight_number = %s AND departure_date_time = %s
    '''
    cursor.execute(query, (airline_name, flight_number, departure_date_time))
    data = cursor.fetchall()
    cursor.close()
    return render_template('passengerList.html', passenger=data)


@app.route('/bothSearch', methods=['GET', 'POST'])
def bothSearch():
    try:
        username = session['username']
    except Exception:
        message = 'Please Login or Create an Account'
        return render_template('staffLogin.html', error=message)
    source_airport = request.form['sourceairport']
    dest_airport = request.form['destairport']
    username = session['username']
    cursor = conn.cursor()
    airline_query = '''
    SELECT airline_name
    FROM airlineStaff 
    WHERE username = %s
    '''
    cursor.execute(airline_query, (username))
    airline = cursor.fetchone()
    print("source_airport: ", source_airport)
    print("dest_airport: ", dest_airport)
    if not source_airport and not dest_airport:
        query = '''
        SELECT DISTINCT flight.airline_name, flight_number, departure_date_time, arrival_date_time, flight_status, base_price, departure_airport_name, arrival_airport_name, airplane_ID 
        FROM airlineStaff, flight 
        WHERE flight.airline_name = %s AND DATEDIFF(DATE(departure_date_time),CURRENT_DATE()) <= 30 AND DATEDIFF(DATE(departure_date_time), CURRENT_DATE()) >= 0;
        '''
        cursor.execute(query, (airline['airline_name']))
    elif not source_airport:
        query = 'SELECT * FROM flight WHERE arrival_airport_name = %s AND airline_name = %s'
        cursor.execute(query, (dest_airport, airline['airline_name']))
    elif not dest_airport:
        query = 'SELECT DISTINCT * FROM flight WHERE departure_airport_name = %s AND airline_name = %s'
        cursor.execute(query, (source_airport, airline['airline_name']))
    else:
        query = 'SELECT * FROM flight WHERE (departure_airport_name = %s AND arrival_airport_name = %s) AND airline_name = %s'
        cursor.execute(query, (source_airport, dest_airport, airline['airline_name']))
    data = cursor.fetchall()
    cursor.close()
    return render_template('staffViewFlights.html', flights=data)



@app.route('/dateSearch', methods=['GET', 'POST'])
def dateSearch():
    try:
        username = session['username']
    except Exception:
        message = 'Please Login or Create an Account'
        return render_template('staffLogin.html', error=message)
    startdate = request.form['startdate']
    enddate = request.form['enddate']

    username = session['username']
    cursor = conn.cursor()

    airline_query = '''
    SELECT airline_name
    FROM airlineStaff 
    WHERE username = %s
    '''
    cursor.execute(airline_query, (username))
    airline = cursor.fetchone()

    query = 'SELECT * FROM flight WHERE DATE(departure_date_time) >= %s AND DATE(departure_date_time) <= %s AND airline_name = %s'
    cursor.execute(query, (startdate, enddate, airline['airline_name']))

    data = cursor.fetchall()
    cursor.close()
    return render_template('staffViewFlights.html', flights=data)


@app.route('/staffViewFlights')
def staffViewFlights():
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
    SELECT DISTINCT flight.airline_name, flight_number, departure_date_time, arrival_date_time, flight_status, base_price, departure_airport_name, arrival_airport_name, airplane_ID 
    FROM airlineStaff, flight 
    WHERE flight.airline_name = %s AND DATEDIFF(DATE(departure_date_time),CURRENT_DATE()) <= 30 AND DATEDIFF(DATE(departure_date_time), CURRENT_DATE()) >= 0;
    '''
    cursor.execute(query, (airline['airline_name']))
    data = cursor.fetchall()
    cursor.close()
    return render_template('staffViewFlights.html', flights=data)


@app.route('/frequentCustomers')
def frequent_customers():
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

    max_ticket_query = '''
    SELECT MAX(ticket_count) AS max_ticket FROM (
    SELECT email, COUNT(ticket.ticket_ID) as ticket_count 
    FROM ticket, purchase WHERE purchase.ticket_ID = ticket.ticket_ID
    AND purchase_date_time > DATE_SUB(NOW(), INTERVAL 1 YEAR)
    AND purchase_date_time < NOW()
    AND ticket.airline_name = %s
    GROUP BY email) as T;
    '''
    cursor.execute(max_ticket_query, (airline['airline_name']))
    max_data = cursor.fetchone()

    query = '''
    SELECT email, COUNT(ticket.ticket_ID) as ticket_count 
    FROM ticket, purchase WHERE purchase.ticket_ID = ticket.ticket_ID 
    AND purchase_date_time > DATE_SUB(NOW(), INTERVAL 1 YEAR)
    AND purchase_date_time < NOW()
    AND ticket.airline_name = %s
    GROUP BY email HAVING ticket_count = %s
    '''
    cursor.execute(query, (airline['airline_name'], max_data['max_ticket']) )
    data = cursor.fetchall()

    cust_query = '''
    SELECT DISTINCT name, purchase.email AS email 
    FROM customer, purchase, ticket 
    WHERE purchase.ticket_ID = ticket.ticket_ID AND purchase.email = customer.email 
    AND ticket.airline_name = %s;
    '''
    cursor.execute(cust_query, (airline['airline_name']))
    cust_data = cursor.fetchall()
    cursor.close()
    return render_template('frequentCustomers.html', customer=data, allCustomer=cust_data)


@app.route('/customerFlights/<email>/')
def customer_flights(email):
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

    key_query = '''
    SELECT DISTINCT airline_name, flight_number, departure_date_time
    FROM purchase, ticket WHERE purchase.ticket_ID = ticket.ticket_ID 
    AND purchase.email = %s AND ticket.airline_name = %s;
    '''
    cursor.execute(key_query, (email, airline['airline_name']))
    key_data = cursor.fetchall()
    query = '''
    SELECT DISTINCT flight.airline_name, flight.flight_number, flight.departure_date_time, 
    flight.arrival_date_time, flight.base_price, flight.flight_status, 
    flight.departure_airport_name, flight.arrival_airport_name, flight.airplane_ID
    FROM purchase, ticket, flight 
    WHERE ticket.airline_name = flight.airline_name AND ticket.flight_number = flight.flight_number 
    AND ticket.departure_date_time = flight.departure_date_time 
    AND purchase.ticket_ID = ticket.ticket_ID AND purchase.email = %s
    AND ticket.airline_name = %s ORDER BY DATE(flight.departure_date_time);
    '''
    cursor.execute(query, (email, airline['airline_name']))
    data = cursor.fetchall()
    cursor.close()
    return render_template('customerFlights.html', flights=data)


# Logout for staff
@app.route('/staffLogout')
def logout_staff():
    session.pop('username')
    return redirect('staffLogin')
