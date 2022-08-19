import json
import dateutil.parser
import babel
from flask import Flask, render_template,abort,request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_migrate import Migrate
from flask_wtf import Form
from forms import *
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate=Migrate(app,db)
moment = Moment(app)
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id',ondelete='CASCADE'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id',ondelete='CASCADE'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    
    def __repr__(self):
        return f"<Show id={self.id}, artist_id={self.artist_id},venue_id={self.venue_id}, start_time={self.start_time}>"

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genres=db.Column(db.String(120))#Added
    facebook_link = db.Column(db.String(150))
    website_link=db.Column(db.String(150))#Added
    seeking_talent=db.Column(db.Boolean, nullable=False, default=False)#Added
    seeking_description=db.Column(db.String(150))#Added
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)#Added
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    shows= db.relationship("Show", backref="venues", lazy=False, cascade="all, delete-orphan")#Added
    # schedules= db.relationship("Schedule", backref="venues", lazy=False, cascade="all, delete-orphan")#Added
    #Added
    def __repr__(self):
        return f"<Venue id={self.id}, name={self.name}, city={self.city}, state={self.state}, address={self.address}, phone={self.phone},image_link={self.image_link}, genres={self.genres},facebook_link={self.facebook_link},website_link={self.website_link}, seeking_talent={self.seeking_talent}, seeking_description={self.seeking_description}>"

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genres = db.Column(db.String(150))
    facebook_link = db.Column(db.String(150))
    website_link=db.Column(db.String(150))#Added
    seeking_venue=db.Column(db.Boolean, nullable=False, default=False)#Added
    seeking_description=db.Column(db.String(150))#Added
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)#Added
    shows= db.relationship("Show", backref="artists", lazy=False, cascade="all, delete-orphan")#Added
    # albums= db.relationship("Album", backref="artists", lazy=False, cascade="all, delete-orphan")#Added
    # reserves= db.relationship("Reserve", backref="artists", lazy=False, cascade="all, delete-orphan")#Added
    def __repr__(self):
        return f"<Artist id={self.id}, name={self.name},city={self.city}, state={self.state}, phone={self.phone},image_link={self.image_link},genres={self.genres},facebook_link={self.facebook_link},website_link={self.website_link},seeking_venue={self.seeking_venue},seeking_description={self.seeking_description}>"
# TODO: implement any missing fields, as a database migration using Flask-Migrate

# Suggestions to make your project remarkable! I didn't have time, here is my proposal so that there is the schedule and the album and force the artist to book
# class Reserve(db.Model):
#     __tablename__ = 'reserves'
#     id=db.Column(db.Integer, primary_key=True)
#     artist_id = db.Column(db.Integer, db.ForeignKey('artists.id',ondelete='CASCADE'), nullable=False)
#     schedule_id = db.Column(db.Integer, db.ForeignKey('schedules.id',ondelete='CASCADE'), nullable=False)
#     reserve = db.Column(db.String(120))
#     def __repr__(self):
#         return f"<Reserve id={self.id}, artist_id={self.artist_id},schedule_id={self.schedule_id},reserve={self.reserve}>"

# class Schedule(db.Model):
#     __tablename__ = 'schedules'
#     id=db.Column(db.Integer, primary_key=True)
#     start_time = db.Column(db.DateTime, nullable=False)
#     venue_id = db.Column(db.Integer, db.ForeignKey('venues.id',ondelete='CASCADE'), nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)#Added
#     reserves= db.relationship("Reserve", backref="schedules", lazy=False, cascade="all, delete-orphan")#Added
#     def __repr__(self):
#         return f"<Schedule id={self.id}, start_time={self.start_time},venue_id={self.venue_id}>"

# class Album(db.Model):
#     __tablename__ = 'albums'
#     id=db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(120))
#     song_number = db.Column(db.Integer)
#     song = db.Column(db.String(150))
#     release_date = db.Column(db.DateTime, nullable=False)
#     artist_id = db.Column(db.Integer, db.ForeignKey('artists.id',ondelete='CASCADE'), nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)#Added
#     def __repr__(self):
#         return f"<Album id={self.id}, title={self.title},song_number={self.song_number}, song={self.song},release_date={self.release_date},artist_id={self.artist_id}>"