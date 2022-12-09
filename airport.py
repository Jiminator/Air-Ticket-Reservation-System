from app import *


# renders add airport template
@app.route('/addAirport')
def add_airport():
    try:
        username = session['username']
    except Exception:
        message = 'Please Login or Create an Account'
        return render_template('staffLogin.html', error=message)
    return render_template('staffAddAirport.html')


# form for staff to add airport
@app.route('/addAirportForm', methods=['GET', 'POST'])
def add_airport_form():
    try:
        username = session['username']
    except Exception:
        message = 'Please Login or Create an Account'
        return render_template('staffLogin.html', error=message)
    airport = request.form['airport_name']
    city = request.form['city']
    country = request.form['country']
    type = request.form['type']
    cursor = conn.cursor()
    query = 'SELECT * FROM airport WHERE airport_name = %s'
    cursor.execute(query, airport)
    data = cursor.fetchone()

    if data:
        error = 'Airport already exist'
        return render_template('staffAddAirport.html', error=error)
    else:
        ins = 'INSERT INTO airport VALUES(%s, %s, %s, %s)'
        cursor.execute(ins, (airport, city, country, type))
        conn.commit()
        cursor.close()
        return render_template('staffAddAirport.html')
    return render_template('staffAddAirport.html')
