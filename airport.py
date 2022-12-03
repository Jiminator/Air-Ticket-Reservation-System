from app import *


# Define route for adding new airport
@app.route('/addAirport')
def add_airport():
    return render_template('addAirport.html')


# Define route for adding new airport form
@app.route('/addAirportResult', methods=['GET', 'POST'])
def add_airport_result():
    airport = request.form['airport_name']
    city = request.form['city']
    country = request.form['country']
    type = request.form['type']
    cursor = conn.cursor()
    query = 'SELECT * FROM airport WHERE airport_name = %s AND city = %s'
    cursor.execute(query, (airport, city))
    data = cursor.fetchone()

    error = None

    if (data):
        # returns an error message to the html page
        error = 'Airport already exist'
        return render_template('addAirport.html', error=error)
    else:
        ins = 'INSERT INTO airport VALUES(%s, %s, %s, %s)'
        cursor.execute(ins, (airport, city, country, type))
        conn.commit()
        cursor.close()
        return render_template('addAirport.html')
    return render_template('addAirport.html')