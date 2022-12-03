from app import *


# Define route for viewing flights
@app.route('/viewflights')
def view_flights():

    cursor = conn.cursor()
    display = """
        SELECT DISTINCT *   
        FROM flight
        WHERE departure_date_time > NOW()  
        ORDER BY `flight`.`departure_date_time` ASC
    """
    cursor.execute(display)
    flightdata = cursor.fetchall()
    cursor.close()
    return render_template('viewflights.html', flights=flightdata)

    
# Search flights
@app.route('/flightSearch', methods=['GET', 'POST'])
def flight_search():

    cursor = conn.cursor()
    departPort = request.form['departureairport']
    arrivPort = request.form["arrivalairport"]
    departdate = request.form["departdate"]
    returndate = request.form["returndate"]

    filter = """
        SELECT DISTINCT *   
        FROM flight
        WHERE departure_date_time > NOW()
    """
    variables = []
    if departPort:
        filter += ' AND departure_airport_name=%s'
        variables.append(departPort)
    if arrivPort:
        filter += ' AND arrival_airport_name=%s'
        variables.append(arrivPort)
    if departdate:
        filter += ' AND departure_date_time >= %s'
        variables.append(departdate)
    if returndate:
        filter += ' AND arrival_date_time <= %s'
        variables.append(returndate)
    filter += ' ORDER BY departure_date_time ASC;'
    
    if len(variables):
        cursor.execute(filter, tuple(variables))
    else:
        cursor.execute(filter)
    display = cursor.fetchall()


    cursor.close()
    return render_template('viewflights.html', flights=display)


