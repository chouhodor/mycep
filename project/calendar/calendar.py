from flask import Blueprint, render_template, request
from flask.helpers import url_for
from flask.wrappers import Request
from werkzeug.utils import redirect 
from flask_login import login_required, current_user
from datetime import date, datetime
from ..models import User, OAuth, Events
from .. import db 

calendar = Blueprint('calendar', __name__, url_prefix='/calendar', template_folder='templates', static_url_path='/project/static' )

@calendar.route('/')
def index_calendar():
    date_times = datetime.now().strftime("%d/%m/%Y")
    calendar = []
    course = Events.query.all()

    try:
      username = current_user.username   
    except:
      username = None

    for c in course:
        calendar.append(
        {
            'id': c.id,
            'name': c.name,
            'location': c.location,
            'startDate': c.startDate.strftime("%Y,%m-1,%d"),
            'endDate': c.endDate.strftime("%Y,%m-1,%d"),
            'startDate_card': c.startDate.strftime("%d/%m/%Y"),
            'endDate_card': c.endDate.strftime("%d/%m/%Y")
        })

    return render_template('calendar.html',
    calendar=calendar,
    username = username,
    date_times = date_times   
    )


@calendar.route('/event/<int:event_id>')
@login_required
def event(event_id):

    users = User.query.filter_by(id=event_id).one()

    event = Events.query.filter_by(id=event_id).one()


    def date_convert(inputdate):
        inputdate = inputdate.split(",")
        inputdate= [inputdate]
        for d in inputdate:
            d[1] = calendar.month_name[int(d[1]) + 1]
        return d[2], d[1], d[0]

    startDate_list = event.startDate
    startDate_list = date_convert(startDate_list)

    endDate_list = event.endDate
    endDate_list = date_convert(endDate_list)

    return render_template('event.html', 
    event=event, 
    date_convert=date_convert,
    startDate_list=startDate_list,
    endDate_list=endDate_list
    )


@calendar.route('/addevent', methods=['POST'])
@login_required
def addevent():

    def dateform(y):
        y = datetime.strptime(y, "%d/%m/%Y")
        y = y.strftime("%Y-%m-%d")
        return y

    id = request.form['event-index']
    name = request.form['event-name']
    location = request.form['event-location']
    startDate = dateform(request.form['event-start-date'])
    endDate = dateform(request.form['event-end-date'])

   

    new_event = Events(name =name, location = location, startDate = startDate, endDate = endDate)
    #edit_event = Events(id =id, name =name, location = location, startDate = startDate, endDate = endDate)
    if request.method == 'POST':
        if id != '':
            update_events = Events.query.get(id)
            update_events.name = name
            update_events.location = location
            update_events.startDate = startDate
            update_events.endDate = endDate
            db.session.commit()
            return redirect(url_for('calendar.index'))
        else:
            db.session.add(new_event)
            db.session.commit()
            return redirect(url_for('calendar.index'))


@calendar.route('/delete', methods = ['POST'])
def delete():

    delete_form = int(request.form['eventdelete-index'])
    delete_id = Events.query.get(delete_form)

    if request.method == 'POST':
        db.session.delete(delete_id)
        db.session.commit()
        return redirect(url_for('calendar.index'))
    
