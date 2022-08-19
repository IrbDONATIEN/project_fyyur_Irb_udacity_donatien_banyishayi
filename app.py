#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from models import *
from forms import *
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  # num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  #For this function, here I was inspired by this author: https://github.com/steffaru/udacity-fyyur-project
  data=[]
  show_venue=Venue.query.order_by(Venue.city, Venue.state, Venue.name).all()
  for venue in show_venue:
    venue_item = {}
    venue_pos = -1
    if len(data) == 0:
      venue_pos = 0
      venue_item = {"city": venue.city,"state": venue.state,"venues": []}
      data.append(venue_item)
    else:
      for i, zon_venue in enumerate(data):
        if zon_venue['city'] == venue.city and zon_venue['state'] == venue.state:
          venue_pos = i
          break
      if venue_pos < 0:
        venue_item = { "city": venue.city,"state": venue.state,"venues": []}
        data.append(venue_item)
        venue_pos = len(data) - 1
      else:
        venue_item = data[venue_pos]
    view = {"id": venue.id,"name": venue.name,"num_upcoming_shows": 9}
    venue_item['venues'].append(view)
    data[venue_pos] = venue_item

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={}
  search_term = request.form.get("search_term", "")
  data_venue = list(Venue.query.filter(Venue.name.ilike(f"%{search_term}%") | Venue.state.ilike(f"%{search_term}%") | Venue.city.ilike(f"%{search_term}%")).all())
  response["count"] = len(data_venue)
  response["data"] = data_venue

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = Venue.query.get(venue_id)
  setattr(data, "genres", data.genres.split(","))
  # get past shows
  dup_shows = db.session.query(Show, Venue, Artist).join(Artist).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time >= datetime.now()).all()
  dup={}
  dup_shows = []
  for show in dup_shows:
      dup["artist_name"] = show.Artist.name
      dup["artist_id"] = show.Artist.id
      dup["artist_image_link"] = show.Artist.image_link
      dup["start_time"] = show.Show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
      dup_shows.append(dup)
  setattr(data, "past_shows", dup_shows)
  setattr(data,"past_shows_count", len(dup_shows))
  # future get  shows
  upcoming_shows = db.session.query(Show, Venue, Artist).join(Artist).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time >= datetime.now()).all()
  for show in upcoming_shows:
    dup["artist_name"] = show.Artist.name
    dup["artist_id"] = show.Artist.id
    dup["artist_image_link"] = show.Artist.image_link
    dup["start_time"] = show.Show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    dup_shows.append(dup)
    setattr(data, "upcoming_shows", dup_shows)    
    setattr(data,"upcoming_shows_count", len(upcoming_shows))

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
  form=VenueForm(request.form)
  venue={}
  error = False
  if form.validate():
    try:
        venue = Venue(
          name=form.name.data,
          city=form.city.data,
          state=form.state.data,
          address=form.address.data,
          phone=form.phone.data,
          image_link=form.image_link.data,
          genres=",".join(form.genres.data),
          facebook_link=form.facebook_link.data,
          website_link=form.website_link.data,
          seeking_talent=form.seeking_talent.data,
          seeking_description=form.seeking_description.data
        )
        db.session.add(venue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue :' + venue.name + ' was successfully listed!')
    except Exception as e:
        error = True
        db.session.rollback()
        flash('This phone number : '+request.form['phone']+' already exists! Please select another phone number')
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
          # TODO: on unsuccessful db insert, flash an error instead.
          flash('An error occurred. Venue'+ venue.name +'could not be listed.')
          abort(400)
  else:
    flash('Venue ' + form.name.data + ' failed due to validation error(s)!')
    flash(form.errors) 
  return render_template('pages/home.html')
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  

@app.route('/venues/<venue_id>/delete', methods=["GET"])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error=False
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash("Venue selected ID :" + str(venue_id)+" was deleted successfully !")
  except Exception as e:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
      flash("Venue selected was not deleted successfully!")
      abort(400)
    else:
      return render_template('pages/home.html')
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  #return None

#just for to joy
@app.route('/artists/<artist_id>/delete', methods=["GET"])
def delete_artist(artist_id):
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error=False
  try:
    Artist.query.filter_by(id=artist_id).delete()
    db.session.commit()
    flash("Artist selected ID: "+artist_id+" was deleted successfully !")
  except Exception as e:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
      flash("Artist selected was not deleted successfully!")
      abort(400)
    else:
      return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=[]
  artists=Artist.query.order_by(Artist.name.desc()).all()
  for artist in artists:
    data.append({
      "id": artist.id,
      "name":artist.name
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={}
  search_term= request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike(f"%{search_term}%") | Artist.city.ilike(f"%{search_term}%") | Artist.state.ilike(f"%{search_term}%")).all()
  response["count"] =len(artists)
  response["data"] = artists

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  data=[]
  data = Artist.query.get(artist_id)
  setattr(data, "genres", data.genres.split(","))
  # get past shows
  dup_shows = db.session.query(Show, Venue, Artist).join(Artist).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time >= datetime.now()).all()
  dup={}
  dup_shows = []
  for show in dup_shows:
      dup["venue_name"] = show.Venue.name
      dup["venue_id"] = show.Venue.id
      dup["venue_image_link"] = show.Venue.image_link
      dup["start_time"] = show.Show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
      dup_shows.append(dup)
  setattr(data, "past_shows", dup_shows)
  setattr(data,"past_shows_count", len(dup_shows))
  # future get  shows
  upcoming_shows = db.session.query(Show, Venue, Artist).join(Artist).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time >= datetime.now()).all()
  for show in upcoming_shows:
    dup["venue_name"] = show.Venue.name
    dup["venue_id"] = show.Venue.id
    dup["venue_image_link"] = show.Venue.image_link
    dup["start_time"] = show.Show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    dup_shows.append(dup)
    setattr(data, "upcoming_shows", dup_shows)    
    setattr(data,"upcoming_shows_count", len(upcoming_shows))

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # TODO: populate form with fields from artist with ID <artist_id>
  artist= Artist.query.get(artist_id)
  form.name.data=artist.name
  form.city.data=artist.city
  form.state.data=artist.state
  form.phone.data=artist.phone
  form.image_link.data=artist.image_link
  form.genres.data = artist.genres.split(",")
  form.facebook_link.data=artist.facebook_link
  form.website_link.data=artist.website_link
  form.seeking_venue.data=artist.seeking_venue
  form.seeking_description.data=artist.seeking_description
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist=Artist.query.get(artist_id)
  form=ArtistForm(request.form)
  if form.validate():
    error=False
    try:
        # TODO: modify data to be the data object returned from db insertion
        artist.name=form.name.data
        artist.city=form.city.data
        artist.state=form.state.data
        artist.phone=form.phone.data
        artist.image_link=form.image_link.data
        artist.genres=",".join(form.genres.data)
        artist.facebook_link=form.facebook_link.data
        artist.website_link=form.website_link.data
        artist.seeking_venue=form.seeking_venue.data
        artist.seeking_description=form.seeking_description.data
        db.session.add(artist)
        db.session.commit()
        flash('Artist :' + request.form['name'] + ' edited successfully!')
    except Exception as e:
        error = True
        db.session.rollback()
        flash('This phone number : '+request.form['phone']+' already exists! Please select another phone number')
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
          flash("Selected artist has not been changed!")
          abort(400)
  else:
    flash('Artist ' + form.name.data + ' failed due to validation error(s)!')
    flash(form.errors)

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  # TODO: populate form with values from venue with ID <venue_id>
  form.name.data=venue.name
  form.city.data=venue.city
  form.state.data=venue.state
  form.phone.data=venue.phone
  form.address.data=venue.address
  form.facebook_link.data=venue.facebook_link
  form.image_link.data=venue.image_link
  form.seeking_talent.data=venue.seeking_talent
  form.website_link.data=venue.website_link
  form.seeking_description.data=venue.seeking_description
  form.genres.data = venue.genres.split(",") 

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venues=Venue.query.get(venue_id)
  form=VenueForm(request.form)
  error=False
  if form.validate():
    try:
        # TODO: modify data to be the data object returned from db insertion
        venues.name=form.name.data
        venues.city=form.city.data
        venues.state=form.state.data
        venues.address=form.address.data
        venues.phone=form.phone.data
        venues.image_link=form.image_link.data
        sh_genres=request.form.getlist('genres')
        venues.genres=','.join(sh_genres)
        venues.facebook_link=form.facebook_link.data
        venues.website_link=form.website_link.data
        venues.seeking_talent=form.seeking_talent.data
        venues.seeking_description=form.seeking_description.data
        db.session.add(venues)
        db.session.commit()
        flash('Venue :' + request.form['name'] + ' edited successfully!')
    except Exception as e:
        error = True
        db.session.rollback()
        flash('This phone number : '+request.form['phone']+' already exists! Please select another phone number')
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
          flash("Selected venue has not been changed!")
          abort(400)
  else:
    flash('Venue ' + form.name.data + ' failed due to validation error(s)!')
    flash(form.errors)
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  form=ArtistForm(request.form)
  artist={}
  error = False
  if form.validate():
    try:
        artist = Artist(
          # TODO: modify data to be the data object returned from db insertion
          name=form.name.data,
          city=form.city.data,
          state=form.state.data,
          phone=form.phone.data,
          image_link=form.image_link.data,
          genres=",".join(form.genres.data),
          facebook_link=form.facebook_link.data,
          website_link=form.website_link.data,
          seeking_venue=form.seeking_venue.data,
          seeking_description=form.seeking_description.data
        )
        db.session.add(artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist :' + request.form['name'] + ' was successfully listed!')
    except Exception as e:
        error = True
        db.session.rollback()
        flash('This phone number : '+request.form['phone']+' already exists! Please select another phone number')
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
  # TODO: on unsuccessful db insert, flash an error instead.
          flash("Artist was not successfully listed.")
          abort(400)
  else:
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('Artist ' + form.name.data + ' failed due to validation error(s)!')
    flash(form.errors)
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data=[]
  # #filtering of current shows for the hider in the poster if the date is greater than the current start time
  shows = db.session.query(Show, Venue, Artist).join(Venue).join(Artist).filter(Show.start_time > datetime.now()).order_by('start_time').all()
  for show in shows:
    data.append({
        "venue_id": show.Venue.id,
        "venue_name": show.Venue.name,
        "artist_id": show.Artist.id,
        "artist_name": show.Artist.name,
        "artist_image_link": show.Artist.image_link,
        "start_time": show.Show.start_time.isoformat()
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form=ShowForm(request.form)
  show={}
  error = False
  if form.validate():
    try:
        show=Show(
          artist_id=form.artist_id.data,
          venue_id=form.venue_id.data,
          start_time=form.start_time.data
        )
        db.session.add(show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
    except Exception as e:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
  # TODO: on unsuccessful db insert, flash an error instead.
          flash('An error occurred. Show could not be listed.')
          abort(400)
  else:
    flash('Show ' + form.venue_id.data + 'failed due to validation error(s)!')
    flash(form.errors)
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
