from app import *
from datetime import datetime, date



def yearmonthday(date):
    return str(date).split('-')

def getNoMonths(d1, d2):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d") 
    noMonths = (d2.year - d1.year) * 12 + d2.month - d1.month + 1
    if noMonths < 1:
        noMonths = 1
    return noMonths


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



@app.route('/customerSpending', methods=['GET', 'POST'])
def customerSpending():
    """ 
    Default view will be total amount of money spent in the past year and a bar
    chart/table showing month wise money spent for last 6 months. He/she will also have option to specify
    a range of dates to view total amount of money spent within that range and a bar chart/table showing
    month wise money spent within that range.
    """
    email = session['email']
    cursor = conn.cursor()

    # this query will get the total purchases
    # from current to last year
    totalCost = """
    SELECT SUM(sold_price) as totalCost  
    FROM purchase natural join ticket natural join flight
    WHERE email=%s
    AND purchase_date_time>=date_sub(now(), interval 1 year) 
    """
    cursor.execute(totalCost, (email))
    totalCost = cursor.fetchone()

    # I added a None is the front to make it easier for indexing...so month 1/index 1 = Jan, month5/index5 = May...etc
    months = [None, "January", "February", "March", "April", "May", "June", "July", 
            "August", "September", "October", "November", "December"]
    

    getTime = 'SELECT YEAR(NOW()) as year, MONTH(NOW()) as month, DAY(NOW()) as day;'
    cursor.execute(getTime)
    getTime = cursor.fetchone()

    currYear = getTime['year']
    currMonth = int(getTime['month'])
    currDay = getTime['day']



    if currMonth >= 6:
        display_months = [mnth for mnth in months[currMonth:currMonth-6:-1]]
    else:
        display_months = [mnth for mnth in months[currMonth:0:-1]]
        currMonth = 6 - currMonth + 1
        display_months.extend([mnth for mnth in months[len(months):len(months)-currMonth:-1]])

    index = tuple([months.index(i) for i in display_months])

    #default 6 months
    pastSixMonths = """
    select SUM(sold_price) as sixMonthCost from purchase
    where email=%s
    AND purchase_date_time>=date_sub(now(), interval 6 month)
    """
    cursor.execute(pastSixMonths, (email))
    pastSixMonths = float(cursor.fetchone()['sixMonthCost'])

    percents = []
    for i in index:
        percent = """
        select SUM(sold_price) as price from purchase
        where email=%s
        AND purchase_date_time>=date_sub(now(), interval 6 month)
        AND MONTH(purchase_date_time)=%s;
        """
        cursor.execute(percent, (email, str(i)))
        val = cursor.fetchone()['price']
        if val:
            val = float(val)
            percents.append(["{:.2f}".format(val), "{:.2f}".format((val/pastSixMonths) * 100 + 5)])
        else:
            percents.append([0, 5])

    indexes = [i for i in range(len(display_months))]
    return render_template('customerSpending.html', totalCost=totalCost, display_months=display_months, 
    pastSixMonths=pastSixMonths, percents=percents, year=currYear, day=currDay, indexes=indexes)










@app.route('/customerSpendingUpdate', methods=['GET', 'POST'])
def customerSpendingUpdate():

    # part1 get user inputs
    filter_begin_date = request.form['Start Date']
    filter_end_date = request.form['End Date']
    email = session['email']

    cursor = conn.cursor()

    variables = [email]

    # part2 get the total cost
    totalCost = """
    SELECT SUM(sold_price) as totalCost  
    FROM purchase natural join ticket natural join flight
    WHERE email=%s
    """

    # make query more specific if the user gives us the dates
    if '' in [filter_begin_date, filter_end_date]:
        if filter_begin_date != '':
            totalCost += ' AND purchase_date_time>=%s'
            variables.append(filter_begin_date)
        if filter_end_date != '':
            totalCost += ' AND purchase_date_time<=%s'
            variables.append(filter_end_date)
    else:
        # if doesn't input anything then default to 1 year.
        totalCost += ' AND purchase_date_time>=date_sub(now(), interval 1 year) '

    cursor.execute(totalCost, tuple(variables))
    totalCost = cursor.fetchone()

    # I added a None is the front to make it easier for indexing...so month 1/index 1 = Jan, month5/index5 = May...etc
    months = [None, "January", "February", "March", "April", "May", "June", "July", 
            "August", "September", "October", "November", "December"]
  

                                

    query = 'select DATE(NOW()) as date'
    cursor.execute(query)
    today_date = cursor.fetchone()['date'] 
    # Setting start date to default ===== current date 
    if filter_end_date == '':
        filter_end_date = today_date
    # Setting begin date to default ===== current date - 6 months 
    if filter_begin_date == "": 
        query = 'select DATE(date_sub(now(), interval 6 month)) as date'
        cursor.execute(query)
        filter_begin_date = cursor.fetchone()['date']  

    #noMonths will be the number of months difference between begin and end date.
    noMonths = getNoMonths(str(filter_begin_date), str(filter_end_date))

    byear,bmonth,bday = yearmonthday(filter_begin_date)
    eyear,emonth,eday = yearmonthday(filter_end_date)

    display_months = []
    tyear,tmonth,tday = int(eyear),int(emonth),int(eday)
    for i in range(noMonths):
        if tmonth == 0:
            tmonth = 12
            tyear -= 1
        
        temp = months[tmonth] + ' ' + str(tyear)
        display_months.append(temp)
        tmonth -= 1

    # when the loop is finished it should look like this
    # display_months looks like ['December 2022', 'November 2022', 'October 2022', 'September 2022', 'August 2022', 'July 2022', 'June 2022', 'May 2022', 'April 2022', 'March 2022', 'February 2022', 'January 2022']        
    # this will be the x axis
    
    pastXmonths = """
    select SUM(sold_price) as pastXmonths from purchase
    where email=%s
    AND purchase_date_time>=date_sub(now(), interval %s month)
    """
    cursor.execute(pastXmonths, (email, noMonths))
    #pastXMonths should contain the total number of money spent throught the
    #specified period of time, or by default 6 months
    pastXmonths = float(cursor.fetchone()['pastXmonths'])



    #CALCULATING THE PERCENTS

    monthYear = []
    percents = []
    valsOnly=[]
    for i in display_months:
        i = i.split()
        i.append(months.index(i[0]))
        monthYear.append(i)

    for i in monthYear:
        print(i)
        percent = """
        select SUM(sold_price) as price from purchase
        where email=%s
        AND YEAR(purchase_date_time)=%s
        AND MONTH(purchase_date_time)=%s
        """
        cursor.execute(percent, (email, str(i[1]), str(i[2])))
        val = cursor.fetchone()['price']
        if val:
            val = float(val)
            percents.append(["{:.2f}".format(val), "{:.2f}".format((val/pastXmonths) * 100)])
            valsOnly.append("{:.2f}".format(val))
        else:
            percents.append([0, 1])
            valsOnly.append("{:.2f}".format(0))

        #percents is formatted so that percents[0] is the $$ and percents[1] is the %%


    print(f'''
    
    
    LOOK HERE    {filter_begin_date}
    LOOK HERE 1   {filter_end_date}
    LOOK HERE 2   {noMonths}
    ddd            {display_months}
    what is this   {valsOnly}
    
    
    ''')
    return render_template('customerSpending.html', totalCost=totalCost, display_months=display_months, 
   percents=percents, pastXmonths=pastXmonths,valsOnly=valsOnly)











