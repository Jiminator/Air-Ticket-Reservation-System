from app import *


# Define route for customer login
@app.route('/customerLogin')
def customer_login():
    return render_template('customerLogin.html')


# Authenticates the customer login
@app.route('/customerLoginAuth', methods=['GET', 'POST'])
def customer_login_auth():
    email = request.form['email']
    password = request.form['password']
    cursor = conn.cursor()
    query = 'SELECT * FROM customer WHERE email = %s and password = MD5(%s)'
    cursor.execute(query, (email, password))
    data = cursor.fetchone()
    cursor.close()
    if data:
        session['email'] = email
        return redirect(url_for('customerHome'))
    else:
        error = 'Invalid login or email'
        return render_template('customerLogin.html', error=error)


# Define route for staff login
@app.route('/staffLogin')
def staff_login():
    return render_template('staffLogin.html')


# Authenticates the staff login
@app.route('/staffLoginAuth', methods=['GET', 'POST'])
def staff_login_auth():
    username = request.form['username']
    password = request.form['password']

    cursor = conn.cursor()
    query = 'SELECT * FROM airlinestaff WHERE username = %s and password = MD5(%s)'
    cursor.execute(query, (username, password))
    data = cursor.fetchone()
    cursor.close()
    if data:
        session['username'] = username
        print("Login")
        return redirect(url_for('staff_home'))
    else:
        error = 'Invalid Username or Password'
        return render_template('staffLogin.html', error=error)
