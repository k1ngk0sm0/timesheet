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
    
@app.route('/clock_in', methods=["GET", "POST"])
def clock_in():
    row = Timesheet(time_in=datetime.now())
    db.session.add(row)
    db.session.commit()
    return 'Succesfully clocked in'

@app.route('/clock_out', methods=["GET", "POST"])
def clock_out():
    row = Timesheet.query.filter_by(hours=0.0).first()
    row.time_out = datetime.now()
    row.hours = ((row.time_out - row.time_in).total_seconds()) / 60 / 60
    db.session.commit()
    return 'Successfully clocked out'

@app.route('/history', methods=["GET", "POST"])

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)