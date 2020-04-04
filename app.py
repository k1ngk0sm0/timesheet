from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///payroll.db'
db = SQLAlchemy(app)

# Create table to store timesheets
class Timesheet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_in = db.Column(db.DateTime)
    time_out = db.Column(db.DateTime, default=datetime.now())
    hours = db.Column(db.Float, default=0.0)

@app.route('/')
def index():
    return render_template("index.html")
    
@app.route('/clock_in')
def clock_in():
    """Clock in and add row to Timesheet table"""
    row = Timesheet(time_in=datetime.now())
    db.session.add(row)
    db.session.commit()

    # Return success message to user
    time_in = row.time_in.strftime("%c")
    return render_template('message.html', time=time_in, status="In")

@app.route('/clock_out')
def clock_out():
    """Clock in and update current row of Timesheet table"""
    row = Timesheet.query.filter_by(hours=0.0).first()
    row.time_out = datetime.now()
    row.hours = ((row.time_out - row.time_in).total_seconds()) / 60 / 60
    db.session.commit()

    # Return success message to user
    time_out = row.time_out.strftime("%c")
    return render_template('message.html', time=time_out, status="Out")

# @app.route('/history', methods=["GET", "POST"])
# def history():
#     return 'history'

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)