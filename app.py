from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from helpers import usd, f_format

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///payroll.db'
db = SQLAlchemy(app)

# Create table to store timesheets
class Timesheet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pay_period = db.Column(db.Text)
    time_in = db.Column(db.DateTime)
    time_out = db.Column(db.DateTime, default=datetime.now())
    hours = db.Column(db.Float, default=0.0)

# Custom filters
app.jinja_env.filters["usd"] = usd
app.jinja_env.filters["f_format"] = f_format

@app.route('/')
def index():
    return render_template("index.html")
    
@app.route('/clock_in')
def clock_in():
    """Clock in and add row to Timesheet table"""
    row = Timesheet(time_in=datetime.now(), pay_period=datetime.now().strftime('%b %y'))
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

@app.route('/history', methods=["GET", "POST"])
def history():
    """Choose and display selected timesheet"""
    if request.method == 'GET':
        pay_periods = ['Apr 20']
        for row in Timesheet.query.all():
            if row.pay_period not in pay_periods:
                pay_periods.append(row.pay_period)
        return render_template('history.html', pay_periods=pay_periods)

    else:
        # Initialize total hours, rate and pay period
        pay_period = Timesheet.query.filter_by(pay_period=request.form.get('pay_period'))
        total_hours = 0.0
        rate = 12.0
        # Format pay period data for display and store in list of dicts
        formatted = []
        for row in pay_period:
            total_hours += row.hours
            d = {}
            d['date'] = row.time_in.strftime('%m/%d/%y')
            d['time_in'] = row.time_in.strftime('%I:%M %p')
            d['time_out'] = row.time_out.strftime('%I:%M %p')
            d['hours'] = row.hours
            formatted.append(d)
        return render_template('pay_period.html', pay_period=formatted, total_hours=total_hours, rate=rate, pay=total_hours * rate)
            

if __name__ == "__main__":
    app.run(debug=False)