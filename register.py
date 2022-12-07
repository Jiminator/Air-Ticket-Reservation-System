from app import *


# Define route to register customer
@app.route('/customerRegister')
def customer_register():
    return render_template('customerRegister.html')


# Authenticates register for a new customer
@app.route('/customerRegisterAuth', methods=['GET', 'POST'])
def customer_register_auth():
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
    cursor.execute(query, email)
    data = cursor.fetchone()
    if data:
        # If the previous query returns data, then user exists
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
def staff_register():
    return render_template('staffRegister.html')


# Authenticates register for a new staff
@app.route('/staffRegisterAuth', methods=['GET', 'POST'])
def staff_register_auth():
    username = request.form['username']
    password = request.form['password']
    first_name = request.form['firstname']
    last_name = request.form['lastname']
    email = request.form['email']
    phone = request.form['phone']
    date_of_birth = request.form['dateofbirth']
    airline_name = request.form['airline']


    # ensures that the Airline the user entered exists
    cursor = conn.cursor()
    query = 'SELECT * FROM airline WHERE airline_name = %s'
    cursor.execute(query, airline_name)
    data = cursor.fetchone()
    if not data:
        error = "That airline is does not exist in our system."
        return render_template('staffRegister.html', error=error)

    else:
        # ensures that the username the user entered does not already exist
        query = 'SELECT * FROM airlineStaff WHERE username = %s'
        cursor.execute(query, username)
        data = cursor.fetchone()
        if data:
            error = "Existing staff; try another username"
            return render_template('staffRegister.html', error=error)
        else:
            ins = 'INSERT INTO airlinestaff VALUES(%s, MD5(%s), %s, %s, %s, %s)'
            cursor.execute(ins, (username, password, first_name, last_name, date_of_birth, airline_name))
            ins = 'INSERT INTO staffEmail VALUES(%s, %s)'
            cursor.execute(ins, (username, email))
            if phone:
                ins = 'INSERT INTO staffPhone VALUES(%s, %s)'
                cursor.execute(ins, (username, phone))
            conn.commit()
            cursor.close()
            session['username'] = username
            # it has to be staff_home
            return redirect(url_for('staff_home'))
