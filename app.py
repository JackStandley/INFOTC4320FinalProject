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

def get_cost_matrix():
    cost_matrix = [[100, 75, 50, 100] for row in range(12)]
    return cost_matrix

#seating chart function

def render_seating_chart(reserved_seats):
    # Initialize an empty seating grid
    seat_grid = [['O' for _ in range(4)] for _ in range(12)]
    
    # Mark reserved seats with 'X'
    for seat in reserved_seats:
        seat_row = seat['seatRow']
        seat_column = seat['seatColumn']
        seat_grid[seat_row][seat_column] = 'X'

    return seat_grid

#calculate total earnings function

def calculate_total_earnings(seat_grid):
    cost_matrix = get_cost_matrix()
    total_earnings = 0

    for row_index in range(12):
        for col_index in range(4):
            if seat_grid[row_index][col_index] == 'X':
                total_earnings += cost_matrix[row_index][col_index]

    return total_earnings


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
    if 'username' not in session:  # Ensure only logged-in admins can access this
        return redirect(url_for('admin'))
    
    conn = get_db_connection()

    # Get reserved seats
    reserved_seats = conn.execute('SELECT seatRow, seatColumn FROM reservations;').fetchall()
    conn.close()

    # Render seating chart and calculate total earnings
    seat_grid = render_seating_chart(reserved_seats)
    total_earnings = calculate_total_earnings(seat_grid)
    
    return render_template('admin_seating.html', seat_grid=seat_grid, total_earnings=total_earnings)


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

