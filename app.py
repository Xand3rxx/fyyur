#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import os
import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from forms import *
from config import DatabaseConfgurations
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.sql import text
import collections
collections.Callable = collections.abc.Callable
from sqlalchemy import desc, or_

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object(DatabaseConfgurations)

# TODO: connect to a local postgresql database
db = SQLAlchemy(app)
migrate = Migrate(app, db)
csrf = CSRFProtect()
csrf.init_app(app)
# To avoid the circular import error model file must be imported after the db instatiation
from models import *

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    # Get the list of recently created artists
    artists = Artist.query.order_by(desc(Artist.id)).limit(10).all()
    new_artists = []
    for artist in artists:
        new_artists.append({
            "id": artist.id,
            "name": artist.name
        })


    # Get the list of recently created venues
    venues = Venue.query.order_by(desc(Venue.id)).limit(10).all()
    new_venues = []
    for venue in venues:
        new_venues.append({
            "id": venue.id,
            "name": venue.name,
            "city": venue.city,
            "state": venue.state,
        })

    return render_template('pages/home.html', artists=new_artists, venues=new_venues)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    # data = [{
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "venues": [{
    #         "id": 1,
    #         "name": "The Musical Hop",
    #         "num_upcoming_shows": 0,
    #     }, {
    #         "id": 3,
    #         "name": "Park Square Live Music & Coffee",
    #         "num_upcoming_shows": 1,
    #     }]
    # }, {
    #     "city": "New York",
    #     "state": "NY",
    #     "venues": [{
    #         "id": 2,
    #         "name": "The Dueling Pianos Bar",
    #         "num_upcoming_shows": 0,
    #     }]
    # }]

    # Set array to hold the data to be passed to the view.
    data = []

    # Get list of venues
    venues = Venue.query.with_entities(Venue.city, Venue.state).distinct(Venue.city, Venue.state).all()

    for venue in venues:
        data.append({
            "city": venue.city,
            "state": venue.state,
            "venues": Venue.query.with_entities(Venue.id, Venue.name).filter(Venue.city == venue.city).all(),
            "num_upcoming_shows": len(Venue.query.join(Venue.shows).filter(Show.start_time > datetime.now()).all())
        })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
@csrf.exempt
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    # response = {
    #     "count": 1,
    #     "data": [{
    #         "id": 2,
    #         "name": "The Dueling Pianos Bar",
    #         "num_upcoming_shows": 0,
    #     }]
    # }

    search_term = request.form['search_term']

    if search_term == "":
        flash('Please specify the name of the venue in your search phrase.', 'error')
        return redirect(url_for('venues'))

    results = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).order_by(desc(Venue.id)).all()

    data = []

    for venue in results:
        data.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": len(Venue.query.join(Venue.shows).filter(Show.start_time > datetime.now()).all()),
        })

    response = {
        "count": len(results),
        "data": data
    }

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/filter', methods=['POST'])
@csrf.exempt
def filter_venues():
    # TODO: Implement Search Venues by City and State. Searching by "San Francisco, CA" should return all venues in San Francisco, CA.

    # Get the search phrase from the search input field
    search_term = request.form['search_term']

    # Remove comma from the search phrase and split into city and state
    filtered_city = search_term.rsplit(',', 1)[0]
    filtered_state = search_term.rsplit(',', 1)[1]

    # Remove quoutes from split
    filtered_city = filtered_city.replace('"', '')
    filtered_state = filtered_state.replace('"', '')

    # Remove leadnig whitespace from the filtered state
    filtered_state = filtered_state.lstrip()

    # Validate search field
    if search_term == "":
        flash('Please specify the city or state of the venue in your search phrase.', 'error')
        return redirect(url_for('venues'))

    # Query venues that match the filtered city and state
    results = Venue.query.filter_by(city=filtered_city).filter_by(state=filtered_state).all()

    # Array to store mapped objects from results
    data = []

    for venue in results:
        data.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": len(Venue.query.join(Venue.shows).filter(Show.start_time > datetime.now()).all()),
        })

    response = {
        "count": len(results),
        "data": data
    }

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    # data1 = {
    #     "id": 1,
    #     "name": "The Musical Hop",
    #     "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    #     "address": "1015 Folsom Street",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "123-123-1234",
    #     "website": "https://www.themusicalhop.com",
    #     "facebook_link": "https://www.facebook.com/TheMusicalHop",
    #     "seeking_talent": True,
    #     "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    #     "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    #     "past_shows": [{
    #         "artist_id": 4,
    #         "artist_name": "Guns N Petals",
    #         "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #         "start_time": "2019-05-21T21:30:00.000Z"
    #     }],
    #     "upcoming_shows": [],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 0,
    # }
    # data2 = {
    #     "id": 2,
    #     "name": "The Dueling Pianos Bar",
    #     "genres": ["Classical", "R&B", "Hip-Hop"],
    #     "address": "335 Delancey Street",
    #     "city": "New York",
    #     "state": "NY",
    #     "phone": "914-003-1132",
    #     "website": "https://www.theduelingpianos.com",
    #     "facebook_link": "https://www.facebook.com/theduelingpianos",
    #     "seeking_talent": False,
    #     "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    #     "past_shows": [],
    #     "upcoming_shows": [],
    #     "past_shows_count": 0,
    #     "upcoming_shows_count": 0,
    # }
    # data3 = {
    #     "id": 3,
    #     "name": "Park Square Live Music & Coffee",
    #     "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    #     "address": "34 Whiskey Moore Ave",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "415-000-1234",
    #     "website": "https://www.parksquarelivemusicandcoffee.com",
    #     "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    #     "seeking_talent": False,
    #     "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #     "past_shows": [{
    #         "artist_id": 5,
    #         "artist_name": "Matt Quevedo",
    #         "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #         "start_time": "2019-06-15T23:00:00.000Z"
    #     }],
    #     "upcoming_shows": [{
    #         "artist_id": 6,
    #         "artist_name": "The Wild Sax Band",
    #         "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #         "start_time": "2035-04-01T20:00:00.000Z"
    #     }, {
    #         "artist_id": 6,
    #         "artist_name": "The Wild Sax Band",
    #         "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #         "start_time": "2035-04-08T20:00:00.000Z"
    #     }, {
    #         "artist_id": 6,
    #         "artist_name": "The Wild Sax Band",
    #         "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #         "start_time": "2035-04-15T20:00:00.000Z"
    #     }],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 1,
    # }
    # data = list(filter(lambda d: d['id'] ==
    #             venue_id, [data1, data2, data3]))[0]

    venue = Venue.query.get(venue_id)
    if venue == None:
        flash('This Venue ID(' + str(venue_id) + ') does not exist.', 'error')
        return redirect(url_for('venues'))

    else:
        past_shows = []
        upcoming_shows = []
        current_date = datetime.now()

        for show in venue.shows:
            data = {
                "artist_id": show.artist_id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": format_datetime(str(show.start_time))
            }
            if show.start_time > current_date:
                upcoming_shows.append(data)
            elif show.start_time < current_date:
                past_shows.append(data)

        data = {
            "id": venue.id,
            "name": venue.name,
            "city": venue.city,
            "state": venue.state,
            "address": venue.address,
            "phone": venue.phone,
            "genres": venue.genres,
            "image_link": venue.image_link,
            "facebook_link": venue.facebook_link,
            "website_link": venue.website_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.seeking_description,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows)
        }

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    form = VenueForm(request.form)
    venue_name = request.form['name']
    phone = request.form['phone']
    image_link = request.form['image_link']
    website_link = request.form['website_link']
    seeking_talent = request.form.get('seeking_talent', False)
    seeking_description = request.form['seeking_description']
    if form.validate():
        error = False
        if phone == "":
            flash('Please provide a phone number with a maximum length of 15 characters.', 'error')
            return render_template('forms/new_venue.html', form=form)
        if image_link == "":
            flash('Please provide a valid URL for the image link.', 'error')
            return render_template('forms/new_venue.html', form=form)
        if website_link == "":
            flash('Please provide a valid URL for the website link.', 'error')
            return render_template('forms/new_venue.html', form=form)
        if seeking_talent == "y":
            seeking_talent = True
            if seeking_description == "":
                flash('Please enter a description for the talent you seek.', 'error')
                return render_template('forms/new_venue.html', form=form)
        else:
            seeking_talent = False

        try:
            db.session.add(Venue(name=venue_name, city=request.form['city'], state=request.form['state'], address=request.form['address'], genres=request.form.getlist('genres'), phone=phone, facebook_link=request.form['facebook_link'], image_link=image_link, website_link=website_link, seeking_talent=seeking_talent, seeking_description=seeking_description))
            db.session.commit()
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
        if not error:
            flash('Venue ' + venue_name + ' was successfully listed!', 'success')
            return render_template('pages/home.html')
        else:
            flash('An error occurred. Venue ' +
                venue_name + ' could not be listed.', 'error')
            return render_template('forms/new_venue.html', form=form)

        # return json.dumps(request.form.getlist('genres'))

        # on successful db insert, flash success
        # flash('Venue ' + venue_name + ' was successfully listed!')
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g.,
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        # return render_template('pages/home.html')
    else:
        flash('Venue ' + venue_name + ' could not be listed due to validation error(s)!', 'error')
        flash(form.errors)
        return render_template('forms/new_venue.html', form=form)


@app.route('/venues/<venue_id>/', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    # return jsonify({
    #     "id": venue_id
    # })
    venue = Venue.query.get(venue_id)
    if venue == None:
        flash('This Venue ID(' + str(venue_id) + ') does not exist.', 'error')
        return redirect(url_for('pages/show_venue', venue_id=venue_id))

    error = False
    try:
        db.session.delete(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if not error:
        flash('Venue ' + venue.name + ' was successfully deleted!', 'success')
        return redirect(url_for('index'))
    else:
        flash('An error occurred. Venue ' +
            venue.name + ' could not be deleted.', 'error')
        return redirect(url_for('show_venue', venue_id=venue_id))

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    # data = [{
    #     "id": 4,
    #     "name": "Guns N Petals",
    # }, {
    #     "id": 5,
    #     "name": "Matt Quevedo",
    # }, {
    #     "id": 6,
    #     "name": "The Wild Sax Band",
    # }]

    artists = Artist.query.all()
    data = []
    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name
        })
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
@csrf.exempt
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    # response = {
    #     "count": 1,
    #     "data": [{
    #         "id": 4,
    #         "name": "Guns N Petals",
    #         "num_upcoming_shows": 0,
    #     }]
    # }

    search_term = request.form['search_term']

    if search_term == "":
        flash('Please specify the name of the artist in your search phrase.', 'error')
        return redirect(url_for('artists'))

    results = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).order_by(desc(Artist.id)).all()

    data = []

    for artist in results:
        data.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": len(Artist.query.join(Artist.shows).filter(Show.start_time > datetime.now()).all()),
        })

    response = {
        "count": len(results),
        "data": data
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/filter', methods=['POST'])
@csrf.exempt
def filter_artists():
    # TODO: Implement Search Artists by City and State. Searching by "San Francisco, CA" should return all venues in San Francisco, CA.

    # Get the search phrase from the search input field
    search_term = request.form['search_term']

    # Remove comma from the search phrase and split into city and state
    filtered_city = search_term.rsplit(',', 1)[0]
    filtered_state = search_term.rsplit(',', 1)[1]

    # Remove quoutes from split
    filtered_city = filtered_city.replace('"', '')
    filtered_state = filtered_state.replace('"', '')

    # Remove leadnig whitespace from the filtered state
    filtered_state = filtered_state.lstrip()

    # Validate search field
    if search_term == "":
        flash('Please specify the city or state of the artist in your search phrase.', 'error')
        return redirect(url_for('artists'))

     # Query artists that match the filtered city and state
    results = Artist.query.filter_by(city=filtered_city).filter_by(state=filtered_state).all()

    # Array to store mapped objects from results
    data = []

    for artist in results:
        data.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": len(Artist.query.join(Artist.shows).filter(Show.start_time > datetime.now()).all()),
        })

    response = {
        "count": len(results),
        "data": data
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    # data1 = {
    #     "id": 4,
    #     "name": "Guns N Petals",
    #     "genres": ["Rock n Roll"],
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "326-123-5000",
    #     "website": "https://www.gunsnpetalsband.com",
    #     "facebook_link": "https://www.facebook.com/GunsNPetals",
    #     "seeking_venue": True,
    #     "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    #     "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #     "past_shows": [{
    #         "venue_id": 1,
    #         "venue_name": "The Musical Hop",
    #         "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    #         "start_time": "2019-05-21T21:30:00.000Z"
    #     }],
    #     "upcoming_shows": [],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 0,
    # }
    # data2 = {
    #     "id": 5,
    #     "name": "Matt Quevedo",
    #     "genres": ["Jazz"],
    #     "city": "New York",
    #     "state": "NY",
    #     "phone": "300-400-5000",
    #     "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    #     "seeking_venue": False,
    #     "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #     "past_shows": [{
    #         "venue_id": 3,
    #         "venue_name": "Park Square Live Music & Coffee",
    #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #         "start_time": "2019-06-15T23:00:00.000Z"
    #     }],
    #     "upcoming_shows": [],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 0,
    # }
    # data3 = {
    #     "id": 6,
    #     "name": "The Wild Sax Band",
    #     "genres": ["Jazz", "Classical"],
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "432-325-5432",
    #     "seeking_venue": False,
    #     "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "past_shows": [],
    #     "upcoming_shows": [{
    #         "venue_id": 3,
    #         "venue_name": "Park Square Live Music & Coffee",
    #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #         "start_time": "2035-04-01T20:00:00.000Z"
    #     }, {
    #         "venue_id": 3,
    #         "venue_name": "Park Square Live Music & Coffee",
    #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #         "start_time": "2035-04-08T20:00:00.000Z"
    #     }, {
    #         "venue_id": 3,
    #         "venue_name": "Park Square Live Music & Coffee",
    #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #         "start_time": "2035-04-15T20:00:00.000Z"
    #     }],
    #     "past_shows_count": 0,
    #     "upcoming_shows_count": 3,
    # }
    # data = list(filter(lambda d: d['id'] ==
    #             artist_id, [data1, data2, data3]))[0]

    # Check if artist ID exists
    artist = Artist.query.get(artist_id)

    # If result returns None, return back with error message
    if artist == None:
        flash('This Artist ID(' + str(artist_id) + ') does not exist.', 'error')
        return redirect(url_for('artists'))

    else:
        past_shows = []
        upcoming_shows = []
        current_date = datetime.now()

        for show in artist.shows:
            data = {
                "venue_id": show.venue_id,
                "venue_name": show.venue.name,
                "venue_image_link": show.venue.image_link,
                "start_time": format_datetime(str(show.start_time))
            }
            if show.start_time > current_date:
                upcoming_shows.append(data)
            elif show.start_time < current_date:
                past_shows.append(data)

        data = {
            "id": artist.id,
            "name": artist.name,
            "city": artist.city,
            "state": artist.state,
            "phone": artist.phone,
            "genres": artist.genres,
            "image_link": artist.image_link,
            "facebook_link": artist.facebook_link,
            "website_link": artist.website_link,
            "seeking_venue": artist.seeking_venue,
            "seeking_description": artist.seeking_description,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows)
        }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    # artist = {
    #     "id": 4,
    #     "name": "Guns N Petals",
    #     "genres": ["Rock n Roll"],
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "326-123-5000",
    #     "website": "https://www.gunsnpetalsband.com",
    #     "facebook_link": "https://www.facebook.com/GunsNPetals",
    #     "seeking_venue": True,
    #     "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    #     "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    # }
    # TODO: populate form with fields from artist with ID <artist_id>

    artist = Artist.query.get(artist_id)
    if artist == None:
        flash('This Aritst ID(' + str(artist_id) + ') does not exist.', 'error')
        return redirect(url_for('venues'))

    form = ArtistForm()
    artist = {
        "id": artist.id,
        "name": artist.name,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "genres": [genre for genre in artist.genres],
        "image_link": artist.image_link,
        "facebook_link": artist.facebook_link,
        "website_link": artist.website_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
    }

    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    artist = Artist.query.get_or_404(artist_id)

    form = ArtistForm(request.form)
    artist_name = request.form['name']
    phone = request.form['phone']
    image_link = request.form['image_link']
    website_link = request.form['website_link']
    seeking_venue = request.form.get('seeking_venue', False)
    seeking_description = request.form['seeking_description']

    if form.validate():
        error = False
        if phone == "":
            flash('Please provide a phone number with a maximum length of 15 characters.', 'error')
            return render_template('forms/new_artist.html', form=form)
        if image_link == "":
            flash('Please provide a valid URL for the image link.', 'error')
            return render_template('forms/new_artist.html', form=form)
        if website_link == "":
            flash('Please provide a valid URL for the website link.', 'error')
            return render_template('forms/new_artist.html', form=form)
        if seeking_venue == "y":
            seeking_venue = True
            if seeking_description == "":
                flash('Please enter a description for the venue you seek.', 'error')
                return render_template('forms/new_artist.html', form=form)
        else:
            seeking_venue = False

    if form.validate():
        error = False
        try:
            artist.name = request.form['name']
            artist.city = request.form['city']
            artist.state = request.form['state']
            artist.phone = phone
            artist.genres = ",".join(map(str, request.form.getlist('genres')))
            artist.image_link = image_link
            artist.facebook_link = request.form['facebook_link']
            artist.website_link = website_link
            artist.seeking_venue = seeking_venue
            artist.seeking_description = seeking_description
            db.session.commit()
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
        if not error:
            flash('Artist ' + artist_name + ' was successfully updated!', 'success')
            return redirect(url_for('show_artist', artist_id=artist_id))
        else:
            flash('An error occurred. Artist ' +
                artist_name + ' could not be updated.', 'error')
            return redirect(url_for('edit_artist', artist_id=artist_id))
    else:
        flash('Artist ' + artist_name + ' could not be updated due to validation error(s)!', 'error')
        flash(form.errors)
        return redirect(url_for('edit_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    # venue = {
    #     "id": 1,
    #     "name": "The Musical Hop",
    #     "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    #     "address": "1015 Folsom Street",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "123-123-1234",
    #     "website": "https://www.themusicalhop.com",
    #     "facebook_link": "https://www.facebook.com/TheMusicalHop",
    #     "seeking_talent": True,
    #     "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    #     "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    # }
    # TODO: populate form with values from venue with ID <venue_id>

    venue = Venue.query.get(venue_id)
    if venue == None:
        flash('This Venue ID(' + str(venue_id) + ') does not exist.', 'error')
        return redirect(url_for('venues'))

    form = VenueForm()
    venue = {
        "id": venue.id,
        "name": venue.name,
        "city": venue.city,
        "state": venue.state,
        "address": venue.address,
        "phone": venue.phone,
        "genres": venue.genres,
        "image_link": venue.image_link,
        "facebook_link": venue.facebook_link,
        "website_link": venue.website_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
    }

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    venue = Venue.query.get_or_404(venue_id)

    form = VenueForm(request.form)
    venue_name = request.form['name']
    phone = request.form['phone']
    image_link = request.form['image_link']
    website_link = request.form['website_link']
    seeking_talent = request.form.get('seeking_talent', False)
    seeking_description = request.form['seeking_description']
    if form.validate():
        error = False
        if phone == "":
            flash('Please provide a phone number with a maximum length of 15 characters.', 'error')
            return redirect(url_for('show_venue', venue_id=venue_id))
        if image_link == "":
            flash('Please provide a valid URL for the image link.', 'error')
            return redirect(url_for('show_venue', venue_id=venue_id))
        if website_link == "":
            flash('Please provide a valid URL for the website link.', 'error')
            return redirect(url_for('show_venue', venue_id=venue_id))
        if seeking_talent == "y":
            seeking_talent = True
            if seeking_description == "":
                flash('Please enter a description for the talent you seek.', 'error')
                return redirect(url_for('show_venue', venue_id=venue_id))
        else:
            seeking_talent = False

    if form.validate():
        error = False
        try:
            venue.name = request.form['name']
            venue.city = request.form['city']
            venue.state = request.form['state']
            venue.address = request.form['address']
            venue.phone = phone
            venue.genres = request.form.getlist('genres')
            venue.image_link = image_link
            venue.facebook_link = request.form['facebook_link']
            venue.website_link = website_link
            venue.seeking_talent = seeking_talent
            venue.seeking_description = seeking_description
            db.session.commit()
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
        if not error:
            flash('Venue ' + venue_name + ' was successfully updated!', 'success')
            return redirect(url_for('show_venue', venue_id=venue_id))
        else:
            flash('An error occurred. Venue ' +
                venue_name + ' could not be updated.', 'error')
            return redirect(url_for('edit_venue', venue_id=venue_id))
    else:
        flash('Venue ' + venue_name + ' could not be updated due to validation error(s)!', 'error')
        flash(form.errors)
        return redirect(url_for('edit_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm(request.form)
    artist_name = request.form['name']
    phone = request.form['phone']
    image_link = request.form['image_link']
    website_link = request.form['website_link']
    seeking_venue = request.form.get('seeking_venue', False)
    seeking_description = request.form['seeking_description']

    if form.validate():
        error = False
        if phone == "":
            flash('Please provide a phone number with a maximum length of 15 characters.', 'error')
            return render_template('forms/new_artist.html', form=form)
        if image_link == "":
            flash('Please provide a valid URL for the image link.', 'error')
            return render_template('forms/new_artist.html', form=form)
        if website_link == "":
            flash('Please provide a valid URL for the website link.', 'error')
            return render_template('forms/new_artist.html', form=form)
        if seeking_venue == "y":
            seeking_venue = True
            if seeking_description == "":
                flash('Please enter a description for the venue you seek.', 'error')
                return render_template('forms/new_artist.html', form=form)
        else:
            seeking_venue = False

    if form.validate():
        error = False
        try:
            db.session.add(Artist(name=artist_name, city=request.form['city'], state=request.form['state'], phone=phone, genres=",".join(map(str, request.form.getlist('genres'))), facebook_link=request.form['facebook_link'], image_link=image_link, website_link=website_link, seeking_venue=seeking_venue, seeking_description=seeking_description))
            db.session.commit()
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
        if not error:
            flash('Artist ' + artist_name + ' was successfully listed!', 'success')
            return render_template('pages/home.html')
        else:
            flash('An error occurred. Artist ' +
                artist_name + ' could not be listed.', 'error')
            return render_template('forms/new_artist.html', form=form)
    else:
        flash('Artist ' + artist_name + ' could not be listed due to validation error(s)!', 'error')
        flash(form.errors)
        return render_template('forms/new_artist.html', form=form)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    # data = [{
    #     "venue_id": 1,
    #     "venue_name": "The Musical Hop",
    #     "artist_id": 4,
    #     "artist_name": "Guns N Petals",
    #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #     "start_time": "2019-05-21T21:30:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 5,
    #     "artist_name": "Matt Quevedo",
    #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #     "start_time": "2019-06-15T23:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-01T20:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-08T20:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-15T20:00:00.000Z"
    # }]

    shows = Show.query.order_by(desc(Show.id)).all()
    data = []

    for show in shows:
        data.append({
            'venue_id': show.venue.id,
            'venue_name': show.venue.name,
            'artist_id': show.artist.id,
            'artist_name': show.artist.name,
            'artist_image_link': show.artist.image_link,
            "start_time": format_datetime(str(show.start_time))
        })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm(request.form)
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']

    if artist_id == '' or venue_id == '':
        flash('Aritst ID or Venue ID cannot be blank.', 'error')
        return render_template('forms/new_show.html', form=form)

    if form.validate():
        error = False
        artist_exists = Artist.query.get(artist_id)
        venue_exists = Venue.query.get(venue_id)
        if artist_exists == None:
            flash('The provided Artist ID does not exists.', 'error')
            return render_template('forms/new_show.html', form=form)
        elif venue_exists == None:
            flash('The provided Venue ID does not exists.', 'error')
            return render_template('forms/new_show.html', form=form)
        try:
            db.session.add(Show(artist_id=artist_exists.id,venue_id=venue_exists.id,start_time=request.form['start_time']))
            db.session.commit()
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
        if not error:
            flash('Show was successfully listed!', 'success')
            return render_template('pages/home.html')
        else:
            flash('An error occurred. Show could not be listed.', 'error')
            return render_template('forms/new_show.html', form=form)
    else:
        flash('Show could not be listed due to validation error(s)!', 'error')
        flash(form.errors)
        return render_template('forms/new_show.html', form=form)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
# if __name__ == '__main__':
#     app.run()

# Or specify port manually:
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3500))
    app.run(host='0.0.0.0', port=port)
