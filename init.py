# Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
from app import app, conn
import customer
import login
import flight
import register
import staff
import status


# Index page
@app.route('/')
def index():
    return render_template('index.html')



app.secret_key = 'some key that you will never guess'

# Run the app on localhost port 5000
# debug = True -> you don't have to restart flask
# for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug=True)
