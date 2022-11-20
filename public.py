from app import *


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
    data = cursor.fetchall()
    #round-trip
    if returndate != '' and sourceairport != '' and destairport != '' and departdate != '' and returndate > departdate:
        flightsearch[0] = destairport
        flightsearch[1] = sourceairport
        flightsearch[2] = returndate
        cursor.execute(query, tuple(flightsearch))
        data += cursor.fetchall()
    cursor.close()
    return render_template('viewflights.html', flights=data)
