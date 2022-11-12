from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, Form, IntegerField
from dotenv import load_dotenv
import requests
import os

load_dotenv()
API_KEY_MOVIE_DB = os.getenv("API_KEY_MOVIE_DB")
URL = f"https://api.themoviedb.org/3/movie/76341?api_key={API_KEY_MOVIE_DB}"

app = Flask(__name__)
# CREATE DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///10-movies.db'
# Optional: But it will silence the deprecation warning in the console.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.secret_key = os.getenv("app.secret_key_db")
Bootstrap(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String, nullable=True)
    img_url = db.Column(db.String)


with app.app_context():
    db.create_all()


class RateMovieForm(FlaskForm):
    rate = IntegerField(label='Current Rate')
    review = StringField(label='Your Review')
    submit = SubmitField(label='Done')


class AddMovie(FlaskForm):
    movie_title = StringField(label='Movie Title')
    submit = SubmitField(label='Add Movie')


@app.route("/decide/<movie_id>")
def decide(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY_MOVIE_DB}&language=en-US"
    response = requests.get(url).json()
    img_link = f'https://image.tmdb.org/t/p/w342{response["poster_path"]}'
    new_movie = Movie(
        title=response["original_title"],
        year=response["release_date"],
        description=response["overview"],
        rating=response["vote_count"],
        ranking=response["vote_average"],
        review="Very Good",
        img_url=img_link
    )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/", methods=["GET", "POST"])
def home():
    all_movies = db.session.query(Movie).order_by(Movie.ranking.desc())
    db.session.commit()
    return render_template("index.html", movies=all_movies)


@app.route("/edit/<int:id_movie>", methods=["GET", "POST"])
def edit(id_movie):
    form = RateMovieForm()
    update_movie = Movie.query.get(id_movie)
    if form.validate_on_submit():
        update_movie.rating = form.rate.data
        update_movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", form=form, b_update=update_movie)


@app.route("/delete/<int:id_movie>", methods=["GET"])
def delete(id_movie):

    delete_movie = Movie.query.get(id_movie)
    db.session.delete(delete_movie)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/add", methods=["GET", "POST"])
def add():
    add_movie = AddMovie()
    if add_movie.validate_on_submit():
        query = add_movie.movie_title.data
        URL1 = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY_MOVIE_DB}&query={query}"
        data = requests.get(URL1).json()["results"]
        return render_template("select.html", options=data)
    return render_template("add.html", form=add_movie)


if __name__ == '__main__':
    app.run(debug=True)
