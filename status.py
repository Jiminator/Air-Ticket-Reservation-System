from app import *


@app.route('/flightStatus')
def flight_status():
	return render_template('flightStatus.html')


@app.route('/flightStatusResult', methods=['GET', 'POST'])
def flight_status_result():
	username = session['username']
	flightnum = request.form['flight_number']
	depdatetime = request.form['departure_date_time']
	status = request.form['status']
	cursor = conn.cursor()
	airline_query = '''
    SELECT airline_name
    FROM airlineStaff 
    WHERE username = %s
    '''
	cursor.execute(airline_query, (username))
	airline = cursor.fetchone()
	query = 'SELECT * FROM flight WHERE airline_name = %s AND flight_number = %s AND departure_date_time = %s'
	cursor.execute(query, (airline['airline_name'], flightnum, depdatetime))
	data = cursor.fetchone()
	error = None
	if (data):
		upd = """
		UPDATE flight SET flight_status = %s
		WHERE airline_name = %s AND flight_number = %s
		AND departure_date_time = %s
		"""
		cursor.execute(upd, (status, airline['airline_name'], flightnum, depdatetime))
		conn.commit()
		cursor.close()
		return redirect(url_for('flight_status'))
	else:
		# returns an error message to the html page
		error = 'Flight does not exist'
		return render_template('flightStatus.html', error=error)
	return render_template('flightStatus.html')
