from app import *


# Define route for customer login
@app.route('/customerLogin')
def customerLogin():
    return render_template('customerLogin.html')


# Authenticates the customer login
@app.route('/customerLoginAuth', methods=['GET', 'POST'])
def customerLoginAuth():
    email = request.form['email']
    password = request.form['password']
    cursor = conn.cursor()
    query = 'SELECT * FROM customer WHERE email = %s and password = MD5(%s)'
    cursor.execute(query, (email, password))
    data = cursor.fetchone()
    cursor.close()
    error = None
    if(data):
        #creates a session for the the customer, session is a built in
        session['email'] = email
        return redirect(url_for('customerHome'))
    else:
        #returns an error message to the html page
        error = 'Invalid login or email'
        return render_template('customerLogin.html', error=error)


# Define route for staff login
@app.route('/staffLogin')
def staffLogin():
    return render_template('staffLogin.html')


# Authenticates the staff login
@app.route('/staffLoginAuth', methods=['GET', 'POST'])
def staffLoginAuth():
    username = request.form['username']
    password = request.form['password']

    cursor = conn.cursor()
    query = 'SELECT * FROM airlinestaff WHERE username = %s and password = MD5(%s)'
    cursor.execute(query, (username, password))
    data = cursor.fetchone()
    cursor.close()
    error = None
    if(data):
        session['username'] = username
        print("Login")
        return redirect(url_for('staffHome'))
    else:
        error = 'Invalid login or email'
        return render_template('staffLogin.html', error=error)
