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
        SELECT DISTINCT *   
        FROM purchase natural join ticket natural join flight
        WHERE email=%s 
        AND departure_date_time > NOW();
    """
    cursor.execute(query, (email))
    flightdata = cursor.fetchall()
    cursor.close()
    return render_template('customerHome.html', customer=userdata, flights=flightdata)






@app.route('/customerviewflights', methods=['GET', 'POST'])
def customerviewflights():
    email = session['email']
    cursor = conn.cursor()
    display = """
    SELECT DISTINCT *   
    FROM purchase natural join ticket natural join flight
    WHERE email=%s 
    AND departure_date_time > NOW();
    """
    cursor.execute(display, (email))
    flightdata = cursor.fetchall()
    cursor.close()
    return render_template('customerviewflights.html', flights=flightdata)


@app.route('/customerviewflightsUpdate', methods=['GET', 'POST'])
def customerviewflightsUpdate():
    email = session['email']
    cursor = conn.cursor()

    departPort = request.form['departureairport']
    arrivPort = request.form["arrivalairport"]
    departdate = request.form["departdate"]
    returndate = request.form["returndate"]

    filter = """
    SELECT DISTINCT *   
    FROM purchase natural join ticket natural join flight
    WHERE email=%s AND departure_date_time > NOW()"""
    variables = [email]
    if departPort:
        filter += ' AND departure_airport_name=%s'
        variables.append(departPort)
    if arrivPort:
        filter += ' AND arrival_airport_name=%s'
        variables.append(arrivPort)
    if departdate:
        filter += ' AND departure_date_time > %s'
        variables.append(departdate)
    if returndate:
        filter += ' AND arrival_date_time < %s'
        variables.append(returndate)

    # filtering by date is UNTESTED!!!
    cursor.execute(filter, tuple(variables))
    display = cursor.fetchall()


    cursor.close()
    return render_template('customerviewflights.html', flights=display)











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
    flightNo = request.form['flightNo']
    cardType = request.form["card type"]
    name = request.form['Name of Card']
    cardNumber = request.form['cc-number']
    expDate = request.form["expiration start"]

    cursor = conn.cursor()
    query = 'SELECT base_price, ticket_ID FROM flight NATURAL JOIN ticket WHERE flight_number=%s'
    cursor.execute(query, (flightNo))
    values = cursor.fetchall()

    display = """
        SELECT DISTINCT *   
        FROM flight NATURAL JOIN ticket
        WHERE flight.flight_status != 'cancelled'
        AND departure_date_time > NOW()
    """

    cursor.execute(display)
    flightdata = cursor.fetchall()

    # checks if the ticket ID is exists
    if not values:
        message = "Error: that ticket does not exist in our system. Please enter a valid ticket"
        cursor.close()
        return render_template('customerPurchase.html', error=message, flights=flightdata)
    ticketID = values[0]['ticket_ID']
    # this query may need to change because customers should be able to purchase multiple tickets
    # this query will check if the user bought the ticket. 
    query = 'SELECT * FROM purchase WHERE ticket_ID=%s AND email=%s'
    cursor.execute(query, (ticketID, email))
    data = cursor.fetchone()


    # if the query returns things then the user has already bought the ticket
    if data:
        message = "Error: You have already purchased a ticket for this flight"
    else:
        numTickets = """
        SELECT count(ticket_ID) as seats_taken, ticket_ID, airline_name, airplane_ID, flight_number, number_of_seats, base_price 
        FROM airplane NATURAL JOIN purchase NATURAL JOIN ticket NATURAL JOIN flight    
        WHERE ticket_ID=%s;
        """
        cursor.execute(numTickets, (ticketID))
        data = cursor.fetchone()
        cost = data['base_price']
        seatsTaken = data['seats_taken']
        totalSeats = data['number_of_seats']
        if seatsTaken >= (totalSeats * 0.6):
            cost = float(cost) * 1.25
        query = 'INSERT INTO purchase VALUES (%s, %s, %s ,%s, %s, %s, %s, NOW());'
        cursor.execute(query, (ticketID, email, cost, cardType, cardNumber,name, expDate))
        conn.commit()
        message = "Success: this is confirmation of your purchase"
    cursor.close()
    return render_template('customerPurchase.html', error=message, flights=flightdata)


@app.route('/customerRateflight', methods=['GET', 'POST'])
def customerRateflights():
    email = session['email']
    cursor = conn.cursor()
    query = """
        SELECT DISTINCT * FROM purchase NATURAL JOIN 
        flight NATURAL JOIN ticket
        WHERE email=%s AND arrival_date_time < NOW();
    """
    cursor.execute(query, (email))
    flightdata = cursor.fetchall()
    cursor.close()
    return render_template('customerRateflight.html', flights=flightdata)


@app.route('/customerRateflightUpdate', methods=['GET', 'POST'])
def customerRateflightsUpdate():
    email = session['email']
    cursor = conn.cursor()
    display = """
    SELECT DISTINCT * FROM purchase NATURAL JOIN 
    flight NATURAL JOIN ticket
    WHERE email=%s AND arrival_date_time < NOW();
    """
    cursor.execute(display, (email))
    flightdata = cursor.fetchall()

    flightNo = request.form['flightNo']
    review = request.form["review"]
    rating = request.form['Rating']

    #all the valid flights that the user can rate are stored in valid_flights
    valid_flights = []
    index = 0
    for i, value in enumerate(flightdata):
        curr = value['flight_number']
        valid_flights.append(curr)
        if flightdata[i]['flight_number'] == flightNo:
            index = i
    



    #checks if the inputted flight number is valid
    if flightNo in valid_flights:
        airline_name = flightdata[index]['airline_name']
        departure_date_time = flightdata[index]['departure_date_time']

        #checks if the user has already given a rating for that flight
        prevRatings = "SELECT * FROM interact WHERE email=%s AND flight_number=%s AND airline_name=%s"
        cursor.execute(prevRatings, (email, flightNo, airline_name))
        prevRatings = cursor.fetchall()
        if not prevRatings:
            query = "INSERT INTO interact VALUES (%s, %s, %s ,%s, %s, %s)"
            cursor.execute(query, (email, airline_name, departure_date_time, flightNo, review, rating))
            conn.commit()
            message = "Success: this is confirmation of your review"
        else:
            message = 'You have already given the flight a rating'
    else:
        message = "That is an invalid flight number"
    cursor.close()
    return render_template('customerRateflight.html', error=message, flights=flightdata)


