from app import *


@app.route('/viewReports')
def view_feports():
	username = session['username']
	cursor = conn.cursor()
	airline_query = '''
	SELECT airline_name
	FROM airlineStaff 
	WHERE username = %s
	'''
	cursor.execute(airline_query, (username))
	airline = cursor.fetchone()
	year_query = '''
	SELECT YEAR(purchase_date_time) AS year, COUNT(ticket_ID) as ticket_sales 
	FROM purchase NATURAL JOIN ticket
	WHERE YEAR(purchase_date_time) < YEAR(CURRENT_DATE) AND airline_name = %s 
	GROUP BY YEAR(purchase_date_time)
	ORDER BY YEAR(purchase_date_time) ASC;
	'''
	cursor.execute(year_query, (airline['airline_name']))
	yearly = cursor.fetchall()
	month_query = '''
	SELECT MONTHNAME(purchase_date_time) AS month, COUNT(ticket_ID) as ticket_sales 
	FROM ticket natural join purchase
	WHERE YEAR(purchase_date_time) = YEAR(CURRENT_DATE)  
	AND airline_name = %s GROUP BY MONTHNAME(purchase_date_time)
	ORDER BY MONTHNAME(purchase_date_time) ASC;
	'''
	cursor.execute(month_query, (airline['airline_name']))
	monthly = cursor.fetchall()
	for each in monthly:
		print(each['ticket_sales'])
	cursor.close()
	return render_template('viewReports.html', monthly = monthly, yearly = yearly)


@app.route('/viewReportDate', methods=['GET', 'POST'])
def view_report_date():
	username = session['username']
	startdate = request.form['startdate']
	enddate = request.form['enddate']
	cursor = conn.cursor()
	airline_query = '''
	SELECT airline_name
	FROM airlineStaff 
	WHERE username = %s
	'''
	cursor.execute(airline_query, (username))
	airline = cursor.fetchone()
	query = '''
		SELECT DATE(purchase_date_time) as purchase_date, COUNT(ticket_ID) as ticket_sales 
		FROM ticket natural join purchase
		WHERE purchase_date_time >= %s AND purchase_date_time <= %s  AND airline_name = %s
		GROUP BY DATE(purchase_date_time) ORDER BY DATE(purchase_date_time) ASC;
	'''
	cursor.execute(query, (startdate, enddate, airline['airline_name']))
	data = cursor.fetchall()
	for each in data:
		print(each['purchase_date'])
	cursor.close()
	return render_template('dateChart.html', daterange = data)


@app.route('/dateChart')
def date_chart():
	return render_template('dateChart.html')


@app.route('/compareRevenue')
def compare_revenue():
	username = session['username']
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
	AND YEAR(purchase_date_time) < YEAR(CURRENT_DATE);
	'''
	cursor.execute(year, (airline['airline_name']))
	year_data = cursor.fetchone()
	month = '''
	SELECT SUM(sold_price) AS revenue FROM ticket, purchase
	WHERE purchase.ticket_ID = ticket.ticket_ID AND airline_name = %s
	AND YEAR(purchase_date_time) = YEAR(CURRENT_DATE)  
	GROUP BY MONTHNAME(purchase_date_time)
	ORDER BY MONTHNAME(purchase_date_time) ASC;
	'''
	cursor.execute(month, (airline['airline_name']))
	month_data = cursor.fetchone()
	cursor.close()
	return render_template('compareRevenue.html', year = year_data, month = month_data)

