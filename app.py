from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = 'my secret key'

#connect to db
def get_db_connection():
    conn = sqlite3.connect('reservations.db')
    conn.row_factory = sqlite3.Row
    return conn
#home route
@app.route('/')
def home():
    return render_template('home.html', title="Home")

#admin login route
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Connect to the database
        conn = get_db_connection()
        
        # Check if the username and password exist in the admins table
        user = conn.execute('SELECT * FROM admins WHERE username = ? AND password = ?',
                            (username, password)).fetchone()
        conn.close()

        #if the user exists, store their username in the session
        if user:
            session['username'] = username
            return redirect(url_for('admin_seating'))
        else:
            #render the login page with an error message
            return render_template('admin_login.html', error="Invalid credentials. Please try again.")


    return render_template('admin_login.html')


#reserve seat route
@app.route('/reserve', methods=['GET', 'POST'])
def reserve():
    return render_template('reserve.html')

#admin page route
@app.route('/admin_seating')
def admin_seating():
    return render_template('admin_seating.html')


#pick menu option from home
@app.route('/menu_option', methods =['POST'])
def menu_option():
    selected_option = request.form.get('Menu')
    if selected_option:
        return redirect(selected_option)
    else:
        flash("Invalid menu option")




if __name__ == '__main__':
    app.run(host="0.0.0.0", debug = True)

