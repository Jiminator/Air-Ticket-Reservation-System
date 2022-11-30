from app import *


# Home page for customer
@app.route('/customerHome')
def customerHome():
    email = session['email']
    cursor = conn.cursor()
    query = 'SELECT * FROM customer WHERE email = %s'
    cursor.execute(query, (email))
    userdata = cursor.fetchone()
    query = """
            SELECT DISTINCT
                flight.airline_name, flight.flight_number, flight.departure_date_time, flight.arrival_date_time,
                flight.flight_status, flight.base_price, flight.departure_airport_name, flight.arrival_airport_name, flight.airplane_ID
            FROM
                customer, purchase, ticket NATURAL JOIN flight
            WHERE
                customer.email = %s AND customer.email = purchase.email AND purchase.ticket_ID = ticket.ticket_ID AND
                (DATE(flight.departure_date_time) > CURRENT_DATE() OR (DATE(flight.departure_date_time) = CURRENT_DATE()
                 AND TIME(flight.departure_date_time) > CURRENT_TIME()));
        """
    cursor.execute(query, (email))
    flightdata = cursor.fetchall()
    cursor.close()
    return render_template('customerHome.html', customer=userdata, flights=flightdata)


# Logout for customers and agents
@app.route('/customerLogout')
def logoutCustomer():
    session.pop('email')
    return redirect('customerLogin')

@app.route('/customerPurchase', methods=['GET', 'POST'])
def customerPurchase():
    cursor = conn.cursor()
    query = """
    SELECT DISTINCT *   
    FROM flight NATURAL JOIN ticket
    WHERE flight.flight_status != 'cancelled'
    AND departure_date_time > NOW()
    """
    cursor.execute(query)
    flightdata = cursor.fetchall()
    cursor.close()
    return render_template('customerPurchase.html', flights=flightdata)

@app.route('/customerPurchaseUpdate', methods=['GET', 'POST'])
def customerPurchaseUpdate():
    email = session['email']
    flightNo = request.form['ticket_ID']
    ticket = int(request.form['ticket_ID'])
    cardType = request.form["card type"]
    name = request.form['Name of Card']
    cardNumber = int(request.form['cc-number'])
    expDate = request.form["expiration start"]

    cursor = conn.cursor()
    query = 'SELECT base_price FROM flight NATURAL JOIN ticket WHERE flight_number=%s'
    cursor.execute(query, (flightNo))
    cost = cursor.fetchall()
    print("THISSSSS")
    print("IT IS A ", cost, type(cost))
    # NOT COMPLETELY WORKING!!!
    query = 'INSERT INTO purchase VALUES (1111, %s, 0 ,%s, 3728193847283410, %s, %s, NOW());'
    cursor.execute(query, (email, cardType, name, expDate))
    conn.commit()
    cursor.close()

    return redirect(url_for('customerPurchase'))

    # ensures that the Airline the user entered exists
    cursor = conn.cursor()
    query = 'SELECT * FROM airline WHERE airline_name = %s'
    cursor.execute(query, airline_name)
    data = cursor.fetchone()
    ins ='INSERT INTO testing VALUES("SEE THIS WORKEDDDD@gmail.com")'
    cursor.execute(ins)
    conn.commit()
    cursor.close()
    session['username'] = username
    # it has to be staff_home
    return redirect(url_for('staff_home'))


@app.route('/customerviewflights')
def customerviewflights():
    email = session['email']
    cursor = conn.cursor()
    query = """
    SELECT DISTINCT *   
    FROM purchase natural join ticket natural join flight
    WHERE email=%s 
    #AND departure_date_time > NOW();
    """
    cursor.execute(query, (email))
    flightdata = cursor.fetchall()
    cursor.close()
    return render_template('customerviewflights.html', flights=flightdata)













@app.route('/customerRateflight', methods=['GET', 'POST'])
def customerRateflights():
    email = session['email']
    cursor = conn.cursor()
    query = """
    SELECT DISTINCT *   
    FROM purchase
    WHERE email=%s;
    """
    cursor.execute(query, (email))
    flightdata = cursor.fetchall()
    cursor.close()
    return render_template('customerRateflight.html', flights=flightdata)

