from app import *
from datetime import datetime, date


def validDates(d1, d2):
    if d1 == '' or d2 =='':
        return True
    start = [int(i) for i in d1.split('-')]
    end = [int(i) for i in d2.split('-')]
    print(start)
    print(end)
    d1 = datetime(start[0], start[1], start[2])
    d2 = datetime(end[0], end[1], end[2])
    return d2 > d1


def yearmonthday(date):
    return str(date).split('-')


def getNoMonths(d1, d2):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    noMonths = (d2.year - d1.year) * 12 + d2.month - d1.month + 1
    if noMonths < 1:
        noMonths = 1
    return noMonths


@app.route('/compareRevenue')
def compare_revenue():
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
	year = '''
	SELECT SUM(sold_price) AS revenue FROM ticket, purchase 
	WHERE purchase.ticket_ID = ticket.ticket_ID AND airline_name = %s
	AND purchase_date_time > DATE_SUB(NOW(), INTERVAL 365 DAY) and purchase_date_time < NOW();
	'''
	cursor.execute(year, (airline['airline_name']))
	year_data = cursor.fetchone()
	month = '''
	SELECT SUM(sold_price) AS revenue FROM ticket, purchase 
	WHERE purchase.ticket_ID = ticket.ticket_ID AND airline_name = %s
	AND purchase_date_time > DATE_SUB(NOW(), INTERVAL 30 DAY) and purchase_date_time < NOW();
	'''
	cursor.execute(month, (airline['airline_name']))
	month_data = cursor.fetchone()
	cursor.close()
	return render_template('compareRevenue.html', year = year_data, month = month_data)


@app.route('/staffSpending', methods=['GET', 'POST'])
def staffSpending(filter_begin_date='', filter_end_date=''):
	try:
		username = session['username']
	except Exception:
		message = 'Please Login or Create an Account'
		return render_template('staffLogin.html', error=message)

	if not validDates(filter_begin_date, filter_end_date):
		message = "Cmon... the End date can't be before the start date..."
		return render_template('dateChart.html', error=message)
	cursor = conn.cursor()
	airline_query = '''
	SELECT airline_name
	FROM airlineStaff 
	WHERE username = %s
	'''
	cursor.execute(airline_query, (username))
	airline = cursor.fetchone()

	# the default is to show the cost of 1 year
	defaultYearCost = """
        SELECT SUM(sold_price) as totalCost  
        FROM purchase natural join ticket natural join flight
        WHERE airline_name=%s
        AND purchase_date_time>=date_sub(now(), interval 1 year);
    """
	cursor.execute(defaultYearCost, (airline['airline_name']))
	defaultYearCost = cursor.fetchone()['totalCost']

	variables = [airline['airline_name']]
	rangedTotalCost = """
    SELECT SUM(sold_price) as totalCost  
    FROM purchase natural join ticket natural join flight
    WHERE airline_name=%s
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

	# noMonths will be the number of months difference between begin and end date.
	noMonths = getNoMonths(str(filter_begin_date), str(filter_end_date))

	byear, bmonth, bday = yearmonthday(filter_begin_date)
	eyear, emonth, eday = yearmonthday(filter_end_date)

	# formats the year and month for me
	display_months = []
	tyear, tmonth, tday = int(eyear), int(emonth), int(eday)
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

	# CALCULATING THE PERCENTS

	monthYear = []  # this will hold the X-Axis Values
	percents = []  # this will hold the Bar graph hieghts
	valsOnly = []  # this will hold the Y-Axis Values  
	for i in display_months:
		i = i.split()
		i.append(months.index(i[0]))  # trying to get the numeric value for the month
		monthYear.append(i)

	for i in monthYear:
		percent = """
        select SUM(sold_price) as price from purchase natural join ticket
        where airline_name=%s
        AND YEAR(purchase_date_time)=%s
        AND MONTH(purchase_date_time)=%s
        """
		cursor.execute(percent, (airline['airline_name'], str(i[1]), str(i[2])))
		val = cursor.fetchone()['price']
		if val:
			val = float(val)
			percents.append(["{:.2f}".format(val), "{:.2f}".format((val / float(rangedTotalCost)) * 100)])
			valsOnly.append("{:.2f}".format(val))
		else:
			percents.append([0, 1])
			valsOnly.append("{:.2f}".format(0))

	# percents is formatted so that percents[0] is the $$ and percents[1] is the Hieght

	x_unformatted = '-'.join(display_months)
	y_unformatted = '-'.join(valsOnly)

	today = date.today()
	today = today.strftime("%d/%m/%Y")
	tdyDay, tdyMonth, tdyYear = str(today).split('/')

	lstYear, lstMonth = int(tdyYear) - 1, months[(int(tdyMonth) - 1)]

	return render_template('dateChart.html', x_unformatted=x_unformatted,
						   y_unformatted=y_unformatted, byear=byear, bmonth=months[int(bmonth)], eyear=eyear,
						   emonth=months[int(emonth)], noMonths=noMonths,
						   tdyYear=tdyYear, tdyMonth=months[int(tdyMonth)], lstYear=lstYear, lstMonth=lstMonth,
						   defaultYearCost=defaultYearCost, rangedTotalCost=rangedTotalCost)


@app.route('/staffSpendingUpdate', methods=['GET', 'POST'])
def staffSpendingUpdate():
	# part1 get user inputs
	try:
		filter_begin_date = request.form['Start Date']
		filter_end_date = request.form['End Date']
	except Exception:
		message = 'Please Login or Create an Account'
		return render_template('staffLogin.html', error=message)
	return staffSpending(filter_begin_date, filter_end_date)
