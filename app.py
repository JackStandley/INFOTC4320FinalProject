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
    #initialize an empty seating grid
    seat_grid = [['O' for _ in range(4)] for _ in range(12)]
    
    #mark reserved seats with 'X'
    for seat in reserved_seats:
        seat_row = seat['seatRow']
        seat_column = seat['seatColumn']
        seat_grid[seat_row][seat_column] = 'X'

    return seat_grid

def generate_e_ticket_number(name):
    infotc = "INFOTC4320"
    result = []
    name_index = 0
    weave_index = 0

    while name_index < len(name) or weave_index < len(infotc):
        if name_index < len(name):
            result.append(name[name_index])
            name_index += 1
        if weave_index < len(infotc):
            result.append(infotc[weave_index])
            weave_index += 1

    return ''.join(result)
                    

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
    conn = get_db_connection()
    try:
        if request.method == 'POST':
            # Get form data
            first_name = request.form.get('first_name')
            row = request.form.get('row')
            seat = request.form.get('seat')

            # All fields must include data
            if not first_name or not row or not seat:
                flash('All fields are required.', 'error')
                reserved_seats = conn.execute('SELECT seatRow, seatColumn FROM reservations;').fetchall()
                seat_grid = render_seating_chart(reserved_seats)
                return render_template('reserve.html', seat_grid=seat_grid)

            # Convert to zero-based index 
            row_index = int(row) - 1
            seat_index = int(seat) - 1

            # Check if seat is already reserved
            seat_exists = conn.execute(
                'SELECT * FROM reservations WHERE seatRow = ? AND seatColumn = ?',
                (row_index, seat_index)
            ).fetchone()

            if seat_exists:
                flash(f"Seat {row}-{seat} is already reserved. Please select a different seat.", 'error')
                reserved_seats = conn.execute('SELECT seatRow, seatColumn FROM reservations;').fetchall()
                seat_grid = render_seating_chart(reserved_seats)
                return render_template('reserve.html', seat_grid=seat_grid)

            # Generate eTicketNumber
            e_ticket_number = generate_e_ticket_number(first_name)

            # Insert reservation into the database
            conn.execute(
                'INSERT INTO reservations (passengerName, seatRow, seatColumn, eTicketNumber) VALUES (?, ?, ?, ?)',
                (first_name, row_index, seat_index, e_ticket_number)
            )
            conn.commit()

            # Flash success message and redirect
            flash(f"Seat {row}-{seat} reserved successfully for {first_name} with eTicket {e_ticket_number}!", 'success')
            return redirect('/reserve')

        # For GET requests, render seating chart
        reserved_seats = conn.execute('SELECT seatRow, seatColumn FROM reservations;').fetchall()
        seat_grid = render_seating_chart(reserved_seats)
        return render_template('reserve.html', seat_grid=seat_grid)

    finally:
        conn.close()








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

