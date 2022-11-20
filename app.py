# Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors

# Initialize the app from Flask
app = Flask(__name__)

# Configure MySQL
conn = pymysql.connect(host="127.0.0.1",
                       port=3306,
                       user='root',
                       password='',
                       db='air_ticket_reservation_system',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)


# Define a route to main function
@app.route('/')
def index():
    return render_template('index.html')


# Define route for viewing flights
@app.route('/viewflights')
def viewflights():
    # cursor used to send queries
    cursor = conn.cursor()
    # executes query
    query = "SELECT * FROM flight WHERE departure_date_time > NOW()"
    cursor.execute(query)
    # stores the results in a variable
    data = cursor.fetchall()
    # use fetchall() if you are expecting more than 1 data row
    cursor.close()
    return render_template('viewflights.html', flights=data)


# Search flights
@app.route('/flightSearch',methods=['GET','POST'])
def flightSearch():
    sourceairport = request.form['sourceairport']
    destairport = request.form['destairport']
    departdate = request.form['departdate']
    returndate = request.form['returndate']
    flightsearch = []
    if sourceairport == '':
        depart_q = ''
    else:
        flightsearch.append(sourceairport)
        depart_q = 'departure_airport_name = %s AND '
    if destairport == '':
        arrive_q = ''
    else:
        flightsearch.append(destairport)
        arrive_q = 'arrival_airport_name = %s AND '
    if departdate == '':
        ddate_q = ''
    else:
        flightsearch.append(departdate)
        ddate_q = 'DATE(departure_date_time) = %s AND '
    cursor = conn.cursor()
    query = 'SELECT * FROM flight WHERE ' + depart_q + arrive_q + ddate_q + 'departure_date_time > NOW()'
    cursor.execute(query, tuple(flightsearch))
    print(query)
    print(flightsearch)
    data = cursor.fetchall()
    #round-trip
    if returndate != '' and sourceairport != '' and destairport != '' and departdate != '' and returndate > departdate:
        flightsearch[0] = destairport
        flightsearch[1] = sourceairport
        flightsearch[2] = returndate
        cursor.execute(query, tuple(flightsearch))
        print(query)
        print(flightsearch)
        data += cursor.fetchall()
    cursor.close()
    return render_template('viewflights.html', flights=data)


# Define route to register customer
@app.route('/customerRegister')
def customerRegister():
    return render_template('customerRegister.html')


# Authenticates register for a new customer
@app.route('/customerRegisterAuth', methods=['GET', 'POST'])
def customerRegisterAuth():
    email = request.form['email']
    name = request.form['name']
    password = request.form['password']
    building_number = request.form['buildingno']
    street = request.form['street']
    city = request.form['city']
    state = request.form['state']
    phone_number = request.form['phonenumber']
    passport_number = request.form['passportno']
    passport_expiration = request.form['passportexp']
    passport_country = request.form['passportcountry']
    date_of_birth = request.form['dateofbirth']
    cursor = conn.cursor()
    query = 'SELECT * FROM customer WHERE email = %s'
    cursor.execute(query, (email))
    data = cursor.fetchone()
    error = None
    if(data):
        #If the previous query returns data, then user exists
        error = "Existing customer; try another email address"
        return render_template('customerRegister.html', error=error)
    else:
        ins = 'INSERT INTO customer VALUES(%s, %s, MD5(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, (email, name, password, building_number, street, city, state, phone_number, passport_number,
                             passport_expiration, passport_country, date_of_birth))
        conn.commit()
        cursor.close()
        session['email'] = email
        return redirect(url_for('customerHome'))


# Define route to register staff
@app.route('/staffRegister')
def staffRegister():
    return render_template('staffRegister.html')


# Authenticates register for a new staff
@app.route('/staffRegisterAuth', methods=['GET', 'POST'])
def staffRegisterAuth():
    username = request.form['username']
    password = request.form['password']
    first_name = request.form['firstname']
    last_name = request.form['lastname']
    email = request.form['email']
    date_of_birth = request.form['dateofbirth']
    airline_name = request.form['airline']

    cursor = conn.cursor()
    query = 'SELECT * FROM airlineStaff WHERE username = %s'
    cursor.execute(query, (username))
    data = cursor.fetchone()
    error = None
    if(data):
        error = "Existing staff; try another username"
        return render_template('staffRegister.html', error=error)
    else:
        ins = 'INSERT INTO airlinestaff VALUES(%s, MD5(%s), %s, %s, %s, %s)'
        cursor.execute(ins, (username, password, first_name, last_name, date_of_birth, airline_name))
        ins = 'INSERT INTO staffEmail VALUES(%s, %s)'
        cursor.execute(ins, (username, email))
        conn.commit()
        cursor.close()
        session['username'] = username
        return redirect(url_for('staffHome'))


# Define route for customer login
@app.route('/customerLogin')
def customerLogin():
    return render_template('customerLogin.html')

# Authenticates the customer login
@app.route('/customerLoginAuth', methods=['GET', 'POST'])
def customerLoginAuth():
    email = request.form['email']
    password = request.form['password']
    cursor = conn.cursor()
    query = 'SELECT * FROM customer WHERE email = %s and password = MD5(%s)'
    cursor.execute(query, (email, password))
    data = cursor.fetchone()
    cursor.close()
    error = None
    if(data):
        #creates a session for the the customer, session is a built in
        session['email'] = email
        return redirect(url_for('customerHome'))
    else:
        #returns an error message to the html page
        error = 'Invalid login or email'
        return render_template('customerLogin.html', error=error)


# Define route for staff login
@app.route('/staffLogin')
def staffLogin():
    return render_template('staffLogin.html')


# Authenticates the staff login
@app.route('/staffLoginAuth', methods=['GET', 'POST'])
def staffLoginAuth():
    username = request.form['username']
    password = request.form['password']

    cursor = conn.cursor()
    query = 'SELECT * FROM airlinestaff WHERE username = %s and password = MD5(%s)'
    cursor.execute(query, (username, password))
    data = cursor.fetchone()
    cursor.close()
    error = None
    if(data):
        session['username'] = username
        print("Login")
        return redirect(url_for('staffHome'))
    else:
        error = 'Invalid login or email'
        return render_template('staffLogin.html', error=error)


#Home page for customer
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


# Logout for customers and agents
@app.route('/customerLogout')
def logoutCustomer():
    session.pop('email')
    return redirect('customerLogin')


# Logout for staff
@app.route('/staffLogout')
def logoutStaff():
    session.pop('username')
    return redirect('staffLogin')

app.secret_key = 'some key that you will never guess'

# Run the app on localhost port 5000
# debug = True -> you don't have to restart flask
# for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug=True)
