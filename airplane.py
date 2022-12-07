from app import *


@app.route('/addPlane')
def add_plane():
    try:
        username = session['username']
    except Exception:
        message = 'Please Login or Create an Account'
        return render_template('staffLogin.html', error=message)
    return render_template('addPlane.html')


@app.route('/addPlaneForm', methods=['GET', 'POST'])
def add_plane_form():
    try:
        username = session['username']
    except Exception:
        message = 'Please Login or Create an Account'
        return render_template('staffLogin.html', error=message)
    airplaneID = request.form['airplaneID']
    seat = request.form['seat']
    manufacturer = request.form['manufacturer']
    age = request.form['age']
    cursor = conn.cursor()
    airline_query = '''
    SELECT airline_name
    FROM airlineStaff 
    WHERE username = %s
    '''
    cursor.execute(airline_query, (username))
    airline = cursor.fetchone()
    query = 'SELECT * FROM airplane WHERE airline_name = %s AND airplane_ID = %s'
    cursor.execute(query, (airline['airline_name'], airplaneID))
    data = cursor.fetchone()
    error = None
    if (data):
        error = 'Airplane ID already exist'
        return render_template('addPlane.html', error=error)
    else:
        ins = 'INSERT INTO airplane VALUES(%s, %s, %s, %s, %s)'
        cursor.execute(ins, (airline['airline_name'], airplaneID, seat, manufacturer, age))
        conn.commit()
        cursor.close()
        return redirect(url_for('add_plane_confirm', airlinename=airline['airline_name'], airplaneID=airplaneID))
    return render_template('addPlane.html')


@app.route('/addPlaneConfirm/<airlinename>/<airplaneID>/')
def add_plane_confirm(airlinename, airplaneID):
    try:
        username = session['username']
    except Exception:
        message = 'Please Login or Create an Account'
        return render_template('staffLogin.html', error=message)
    cursor = conn.cursor()
    query = '''
    SELECT *
	FROM airplane
	WHERE airline_name = %s
	'''
    cursor.execute(query, (airlinename))
    data = cursor.fetchall()
    cursor.close()
    return render_template('addPlaneConfirm.html', plane=data, airplaneID=airplaneID)
