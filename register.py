from app import *


# Define route to register customer
@app.route('/customerRegister')
def customerRegister():
    return render_template('customerRegister.html')


# Authenticates register for a new customer
@app.route('/customerRegisterAuth', methods=['GET', 'POST'])
def customerRegisterAuth():
    email = request.form['email']
    name = request.form['name']
    password = request.form['password']
    building_number = request.form['buildingno']
    street = request.form['street']
    city = request.form['city']
    state = request.form['state']
    phone_number = request.form['phonenumber']
    passport_number = request.form['passportno']
    passport_expiration = request.form['passportexp']
    passport_country = request.form['passportcountry']
    date_of_birth = request.form['dateofbirth']
    cursor = conn.cursor()
    query = 'SELECT * FROM customer WHERE email = %s'
    cursor.execute(query, (email))
    data = cursor.fetchone()
    error = None
    if(data):
        #If the previous query returns data, then user exists
        error = "Existing customer; try another email address"
        return render_template('customerRegister.html', error=error)
    else:
        ins = 'INSERT INTO customer VALUES(%s, %s, MD5(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, (email, name, password, building_number, street, city, state, phone_number, passport_number,
                             passport_expiration, passport_country, date_of_birth))
        conn.commit()
        cursor.close()
        session['email'] = email
        return redirect(url_for('customerHome'))


# Define route to register staff
@app.route('/staffRegister')
def staffRegister():
    return render_template('staffRegister.html')


# Authenticates register for a new staff
@app.route('/staffRegisterAuth', methods=['GET', 'POST'])
def staffRegisterAuth():
    username = request.form['username']
    password = request.form['password']
    first_name = request.form['firstname']
    last_name = request.form['lastname']
    email = request.form['email']
    date_of_birth = request.form['dateofbirth']
    airline_name = request.form['airline']

    cursor = conn.cursor()
    query = 'SELECT * FROM airlineStaff WHERE username = %s'
    cursor.execute(query, (username))
    data = cursor.fetchone()
    error = None
    if(data):
        error = "Existing staff; try another username"
        return render_template('staffRegister.html', error=error)
    else:
        ins = 'INSERT INTO airlinestaff VALUES(%s, MD5(%s), %s, %s, %s, %s)'
        cursor.execute(ins, (username, password, first_name, last_name, date_of_birth, airline_name))
        ins = 'INSERT INTO staffEmail VALUES(%s, %s)'
        cursor.execute(ins, (username, email))
        conn.commit()
        cursor.close()
        session['username'] = username
        return redirect(url_for('staffHome'))
