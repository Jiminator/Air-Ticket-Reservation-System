from app import *
from datetime import datetime, date
from dateutil.relativedelta import relativedelta


def genTicketId(taken):
    infinity = 99999999
    for i in range(infinity):
        if i not in taken:
            return i


def validDates(d1,d2):
    max_endDate = datetime.today() + relativedelta(months=-5)
    max_startDate = datetime.today()
    if d1 == '' and d2 == '':
        return True

    date1 = max_endDate
    date2 = max_startDate
    if d1:
        start = [int(i) for i in d1.split('-')]
        date1 = datetime(start[0], start[1], start[2])


    if d2:
        end = [int(i) for i in d2.split('-')]
        date2 = datetime(end[0], end[1], end[2])

    
    return date2 > date1

def yearmonthday(date):
    return str(date).split('-')

def getNoMonths(d1, d2):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d") 
    noMonths = (d2.year - d1.year) * 12 + d2.month - d1.month + 1
    if noMonths < 1:
        noMonths = 1
    return noMonths

def removeFromDisplay(display, val):
    newdisplay=[]
    for checkflight in display:
        flag = True
        for currFlight in val:
            if str(checkflight['ticket_ID']) == str(currFlight['ticket_ID']):
                # if ticket_ids match then the person owns the ticket already
                flag = False
        if flag:
            newdisplay.append(checkflight)
    return newdisplay


# Home page for customer
@app.route('/customerHome')
def customerHome():
    try:
        email = session['email']
    except Exception:
        message = 'Please Login or Create an Account'
        return render_template('customerLogin.html', error=message)
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
    try:
        email = session['email']
    except Exception:
        message = 'Please Login or Create an Account'
        return render_template('customerLogin.html', error=message)
    cursor = conn.cursor()
    display = """
        SELECT DISTINCT *   
        FROM purchase natural join ticket natural join flight
        WHERE email=%s 
        AND departure_date_time > NOW()
        ORDER BY `ticket`.`departure_date_time` ASC
    """
    cursor.execute(display, (email))
    flightdata = cursor.fetchall()
    cursor.close()
    return render_template('customerviewflights.html', flights=flightdata)

# @app.route('/customerviewflightsUpdate', methods=['GET', 'POST'])
# def customerviewflightsUpdate():
#     try:
#         email = session['email']
#     except Exception:
#         message = 'Please Login or Create an Account'
#         return render_template('customerLogin.html', error=message)
#     cursor = conn.cursor()

#     departPort = request.form['departureairport']
#     arrivPort = request.form["arrivalairport"]
#     departdate = request.form["departdate"]
#     returndate = request.form["returndate"]

#     filter = """
#     SELECT DISTINCT *   
#     FROM purchase natural join ticket natural join flight
#     WHERE email=%s AND departure_date_time > NOW()"""
#     variables = [email]
#     if departPort:
#         filter += ' AND departure_airport_name=%s'
#         variables.append(departPort)
#     if arrivPort:
#         filter += ' AND arrival_airport_name=%s'
#         variables.append(arrivPort)
#     if departdate:
#         filter += ' AND departure_date_time >= %s'
#         variables.append(departdate)
#     if returndate:
#         filter += ' AND arrival_date_time <= %s'
#         variables.append(returndate)
#     filter += ' ORDER BY `ticket`.`departure_date_time` ASC;'
#     cursor.execute(filter, tuple(variables))
#     display = cursor.fetchall()


#     cursor.close()
#     return render_template('customerviewflights.html', flights=display)


@app.route('/customerviewflightsUpdate', methods=['GET', 'POST'])
def customerviewflightsUpdate():
    try:
        email = session['email']
    except Exception:
        message = 'Please Login or Create an Account'
        return render_template('customerLogin.html', error=message)
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
        filter += ' AND departure_date_time >= %s'
        variables.append(departdate)
    filter += ' ORDER BY ticket.departure_date_time ASC;'
    if len(variables):
        cursor.execute(filter, tuple(variables))
    else:
        cursor.execute(filter)
    data = cursor.fetchall()
    # round-trip
    if returndate != '' and departPort != '' and arrivPort != '' and departdate != '' and returndate >= departdate:
        variables[1] = arrivPort
        variables[2] = departPort
        variables[3] = returndate
        cursor.execute(filter, tuple(variables))
        data += cursor.fetchall()
    cursor.close()
    return render_template('customerviewflights.html', flights=data)

# Logout for customers and agents
@app.route('/customerLogout')
def logoutCustomer():
    session.pop('email')
    flag = True
    message = 'You have Successfully Logged Out'
    return render_template('customerLogin.html', error=message, flag=flag)

@app.route('/customerPurchase', methods=['GET', 'POST'])
def customerPurchase(flight_number = '', cardType = '', name = '', cardNumber = '',expDate =''):
    try:
        email = session['email']
    except Exception:
        message = 'Please Login or Create an Account'
        return render_template('customerLogin.html', error=message)
    cursor = conn.cursor()


    # This query will give us all of our purchases
    purchases = """
        SELECT * FROM purchase NATURAL JOIN ticket NATURAL JOIN flight
        WHERE email = %s
        AND departure_date_time >= NOW();
    """
    cursor.execute(purchases, (email))
    purchases = cursor.fetchall()


    # Only will filter the tickets that aren't cancelled and 
    # are in the future. DOESN"T CHECK if the number of seats YET
    filter1 = """
        SELECT DISTINCT *   
        FROM flight NATURAL JOIN ticket NATURAL JOIN airplane 
        WHERE flight.flight_status != 'cancelled'
        AND departure_date_time > NOW()
    """
    cursor.execute(filter1)
    filter1 = cursor.fetchall()

    finalDisplay = []
    validTicketID = []
    # We will now check for the number of seats
    for flight in filter1:
        numTickets = """
            SELECT count(flight_number) as seats_taken, ticket_ID, airline_name, airplane_ID, flight_number, number_of_seats, base_price 
            FROM airplane NATURAL JOIN purchase NATURAL JOIN ticket NATURAL JOIN flight    
            WHERE flight_number=%s;
        """
        cursor.execute(numTickets, (flight['flight_number']))
        numTickets = cursor.fetchone()
        cost = numTickets['base_price']
        seatsTaken = numTickets['seats_taken']
        totalSeats = numTickets['number_of_seats']
        if seatsTaken >= (totalSeats * 0.6):
            cost = float(cost) * 1.25
            flight['base_price'] = float(cost)
        if seatsTaken < totalSeats and flight['flight_number'] not in finalDisplay:
            finalDisplay.append(flight)
            validTicketID.append(flight['flight_number'])
    # finalDisplay will have all the available flights for purchase that
    # are Not full, Not cancelled, and Not previous flight

    finalDisplay = removeFromDisplay(finalDisplay, purchases)

    # finalDisplay will have all the available flights for purchase that
    # are Not full, Not cancelled, Not previous flight, AND NOT owned!!!

    message = None
    flag = False
    if flight_number and flight_number in validTicketID:
        checkForRepurchase = 'SELECT * FROM purchase natural join flight natural join ticket WHERE flight_number=%s AND email=%s'
        cursor.execute(checkForRepurchase, (flight_number, email))
        checkForRepurchase = cursor.fetchone()
        #checks for repurchase error
        if checkForRepurchase:
            message = "Error: You have already purchased this Ticket!"
        else:

            # this query will get us all of the ticket_IDs
            takenTickets = """
            SELECT DISTINCT ticket_ID FROM PURCHASE
            """
            cursor.execute(takenTickets)
            takenTickets = cursor.fetchall()
            takenList = [i["ticket_ID"] for i in takenTickets]

            newTicketID = genTicketId(takenList)

            popval = None
            # find the index
            for i,flight in enumerate(finalDisplay):
                if flight['flight_number'] == flight_number:
                    popval = i

            
            createTheTicket = 'INSERT INTO ticket Values (%s, %s, %s, %s) '
            cursor.execute(createTheTicket, (newTicketID, finalDisplay[popval]['airline_name'], flight_number, finalDisplay[popval]['departure_date_time']))


            purchase = 'INSERT INTO purchase VALUES (%s, %s, %s ,%s, %s, %s, %s, NOW());'
            cursor.execute(purchase, (newTicketID, email, finalDisplay[popval]['base_price'], cardType, cardNumber,name, expDate))
            conn.commit()
            message = "Success: this is confirmation of your purchase"
            flag = True

            #need to now update the table
            if popval is not None:
                finalDisplay.pop(popval)
    
    elif flight_number:
        message = "Ticket for this flight is not unavailable for purchase"
    
    cursor.close()

    today = date.today()
    today = today.strftime("%b-%d-%Y")
    return render_template('customerPurchase.html', flights=finalDisplay, error=message, flag=flag, today=today)

@app.route('/customerPurchaseUpdate', methods=['GET', 'POST'])
def customerPurchaseUpdate():
    try:
        email = session['email']
    except Exception:
        message = 'Please Login or Create an Account'
        return render_template('customerLogin.html', error=message)
    flight_number = request.form['flight_number']
    cardType = request.form["card type"]
    name = request.form['Name of Card']
    cardNumber = request.form['cc-number']
    expDate = request.form["expiration start"]
    return customerPurchase(flight_number, cardType, name , cardNumber,expDate)


@app.route('/customerDelete', methods=['GET', 'POST'])
def customerDelete():
    try:
        email = session['email']
    except Exception:
        message = 'Please Login or Create an Account'
        return render_template('customerLogin.html', error=message)
    cursor = conn.cursor()
    available = """
    SELECT * FROM purchase NATURAL JOIN ticket NATURAL JOIN flight
    WHERE email = %s
    AND departure_date_time >= NOW() - INTERVAL 1 DAY;
    """
    cursor.execute(available, (email))
    flightdata = cursor.fetchall()
    try:
        ticket_ID = request.form['ticket_ID']
    except Exception:
        ticket_ID = None

    isvalid = [str(ticketIDs['ticket_ID']) for ticketIDs in flightdata]
    message= ''
    if ticket_ID:
        if ticket_ID in isvalid:
            deleteQuery = """
                DELETE FROM purchase 
                WHERE ticket_ID=%s
                AND email=%s
            """
            cursor.execute(deleteQuery, (ticket_ID, email))
            conn.commit()
            message = f'TicketID: {ticket_ID} has been cancelled'
            checker = True
        else:
            checker = False
            message = 'This is an invalid ticketID. Please submit an ID that is from the list above. If the list is empty then you cannot cancel any tickets'
    else:
        checker = False
    

    available = """
    SELECT * FROM purchase NATURAL JOIN ticket NATURAL JOIN flight
    WHERE email = %s
    AND departure_date_time >= NOW() - INTERVAL 1 DAY;
    """
    cursor.execute(available, (email))
    flightdata = cursor.fetchall()

    cursor.close()
    return render_template('customerDelete.html', flights=flightdata, checker=checker,error=message, success=message)  





@app.route('/customerRateflight', methods=['GET', 'POST'])
def customerRateflights():
    try:
        email = session['email']
    except Exception:
        message = 'Please Login or Create an Account'
        return render_template('customerLogin.html', error=message)
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
    try:
        email = session['email']
    except Exception:
        message = 'Please Login or Create an Account'
        return render_template('customerLogin.html', error=message)
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
def customerSpending(filter_begin_date='', filter_end_date=''):
    try:
        email = session['email']
    except Exception:
        message = 'Please Login or Create an Account'
        return render_template('customerLogin.html', error=message)

    if not validDates(filter_begin_date, filter_end_date):
        message = "The dates you entered could not be executed. Please enter correct dates."
        return render_template('customerSpending.html', error=message)
    cursor = conn.cursor()


    # the default is to show the cost of 1 year
    defaultYearCost = """
        SELECT SUM(sold_price) as totalCost  
        FROM purchase natural join ticket natural join flight
        WHERE email=%s
        AND purchase_date_time>=date_sub(now(), interval 1 year);
    """
    cursor.execute(defaultYearCost, (email))
    defaultYearCost = cursor.fetchone()['totalCost']


    variables = [email]
    rangedTotalCost = """
    SELECT SUM(sold_price) as totalCost  
    FROM purchase natural join ticket natural join flight
    WHERE email=%s
    """

    # make query more specific if the user gives us the dates
    if filter_begin_date != '' or filter_end_date != '':
        if filter_begin_date != '':
            rangedTotalCost += ' AND purchase_date_time>=%s'
            variables.append(filter_begin_date)
        if filter_end_date != '':
            rangedTotalCost += ' AND purchase_date_time<=%s'
            variables.append(filter_end_date)
    else:
        # I included the current month so I only subtract by 5.
        rangedTotalCost += ' AND purchase_date_time>=date_sub(now(), interval 5 month) '
    cursor.execute(rangedTotalCost, tuple(variables))
    rangedTotalCost = cursor.fetchone()['totalCost']


    print(rangedTotalCost)
    # I added a None is the front to make it easier for indexing...so month 1/index 1 = Jan, month5/index5 = May...etc
    months = [None, "January", "February", "March", "April", "May", "June", "July", 
            "August", "September", "October", "November", "December"]
  

                                

    today = date.today()
    today = today.strftime("%b-%d-%Y")
    # Setting start date to default ===== current date 
    if filter_end_date == '':
        filter_end_date = date.today()
    # Setting begin date to default ===== current date - 6 months 
    if filter_begin_date == "": 
        query = 'select DATE(date_sub(now(), interval 5 month)) as date'
        cursor.execute(query)
        filter_begin_date = cursor.fetchone()['date']  

    #noMonths will be the number of months difference between begin and end date.
    noMonths = getNoMonths(str(filter_begin_date), str(filter_end_date))


    byear,bmonth,bday = yearmonthday(filter_begin_date)
    eyear,emonth,eday = yearmonthday(filter_end_date)

    #formats the year and month for me
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
    # get the total cost of between the range
    if rangedTotalCost:
        rangedTotalCost = float(rangedTotalCost)
    else:
        rangedTotalCost = 0
    rangedTotalCost = "{:.2f}".format(rangedTotalCost)

    #CALCULATING THE PERCENTS

    monthYear = []  # this will hold the X-Axis Values
    percents = []   # this will hold the Bar graph hieghts
    valsOnly=[]     # this will hold the Y-Axis Values  
    for i in display_months:
        i = i.split()
        i.append(months.index(i[0])) # trying to get the numeric value for the month
        monthYear.append(i)


    for i in monthYear:
        percent = """
        select SUM(sold_price) as price from purchase
        where email=%s
        AND YEAR(purchase_date_time)=%s
        AND MONTH(purchase_date_time)=%s
        """
        cursor.execute(percent, (email, str(i[1]), str(i[2])))
        val = cursor.fetchone()['price']
        if float(rangedTotalCost) and val:
            val = float(val)
            percents.append(["{:.2f}".format(val), "{:.2f}".format((val/float(rangedTotalCost)) * 100)])
            valsOnly.append("{:.2f}".format(val))
        elif val: 
            val = float(val)
            percents.append(["{:.2f}".format(val), "{:.2f}".format(100)])
            valsOnly.append("{:.2f}".format(val))
        else:
            percents.append([0, 1])
            valsOnly.append("{:.2f}".format(0))

        #percents is formatted so that percents[0] is the $$ and percents[1] is the Hieght

    x_unformatted = '-'.join(display_months)
    y_unformatted = '-'.join(valsOnly)



    today = date.today()
    today = today.strftime("%d/%m/%Y")
    tdyDay, tdyMonth, tdyYear = str(today).split('/')

    lstYear, lstMonth = int(tdyYear) - 1, months[(int(tdyMonth)-1)]

    return render_template('customerSpending.html', x_unformatted=x_unformatted, 
   y_unformatted=y_unformatted, byear=byear,bmonth=months[int(bmonth)], eyear=eyear, emonth=months[int(emonth)], noMonths=noMonths,
   tdyYear=tdyYear, tdyMonth=months[int(tdyMonth)], lstYear=lstYear, lstMonth=lstMonth, defaultYearCost=defaultYearCost, rangedTotalCost=rangedTotalCost)


# totalCostYear=totalCostYear, display_months=display_months, 
# percents=percents, pastXmonthsDisplay=pastXmonthsDisplay,valsOnly=valsOnly, 
   




@app.route('/customerSpendingUpdate', methods=['GET', 'POST'])
def customerSpendingUpdate():
    # part1 get user inputs
    try:
        filter_begin_date = request.form['Start Date']
        filter_end_date = request.form['End Date']
    except Exception:
        message = 'Please Login or Create an Account'
        return render_template('customerLogin.html', error=message)
    return customerSpending(filter_begin_date, filter_end_date)









