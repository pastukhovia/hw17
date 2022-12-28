from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app)
movies_ns = api.namespace('movies')
directors_ns = api.namespace('directors')
genres_ns = api.namespace('genres')


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MoviesSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


class DirectorsSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class GenresSchema(Schema):
    id = fields.Int()
    name = fields.Str()


movies_schema = MoviesSchema(many=True)
movie_schema = MoviesSchema()
directors_schema = DirectorsSchema(many=True)
director_schema = DirectorsSchema()
genres_schema = GenresSchema(many=True)
genre_schema = GenresSchema()


@movies_ns.route('/')
class MoviesView(Resource):
    def get(self):
        search_director = request.args.get('director_id')
        search_genre = request.args.get('genre_id')

        if search_director and search_genre:
            result = db.session.query(Movie).filter(Movie.director_id == search_director,
                                                    Movie.genre_id == search_genre)

            return [movie['title'] for movie in movies_schema.dump(result)], 200
        elif search_director:
            result = db.session.query(Movie).filter(Movie.director_id == search_director)

            return [movie['title'] for movie in movies_schema.dump(result)], 200
        elif search_genre:
            result = db.session.query(Movie).filter(Movie.genre_id == search_genre)

            return [movie['title'] for movie in movies_schema.dump(result)], 200
        else:
            return [movie['title'] for movie in movies_schema.dump(Movie.query.all())], 200

    def post(self):
        req_json = request.get_json()
        new_movie = Movie(**req_json)

        with app.app_context():
            with db.session.begin():
                db.session.add(new_movie)
                db.session.commit()

        return '', 201


@movies_ns.route('/<int:uid>')
class MovieView(Resource):
    def get(self, uid):
        try:
            movie = db.session.query(Movie).filter(Movie.id == uid).one()
            return movie_schema.dump(movie), 200
        except Exception as e:
            return str(e), 404

    def put(self, uid):
        with app.app_context():
            with db.session.begin():
                req_json = request.get_json()
                movie = Movie.query.get(uid)

                movie.title = req_json['title']
                movie.description = req_json['description']
                movie.trailer = req_json['trailer']
                movie.year = req_json['year']
                movie.rating = req_json['rating']
                movie.genre_id = req_json['genre_id']
                movie.director_id = req_json['director_id']

                db.session.add(movie)
                db.session.commit()

            return '', 204

    def delete(self, uid):
        with app.app_context():
            with db.session.begin():
                movie = Movie.query.get(uid)
                db.session.delete(movie)
                db.session.commit()

        return '', 204


@directors_ns.route('/')
class DirectorsView(Resource):
    def get(self):
        return [director['name'] for director in directors_schema.dump(Director.query.all())], 200

    def post(self):
        req_json = request.get_json()
        new_director = Director(**req_json)

        with app.app_context():
            with db.session.begin():
                db.session.add(new_director)
                db.session.commit()

        return '', 201


@directors_ns.route('/<int:uid>')
class DirectorView(Resource):
    def get(self, uid):
        try:
            director = db.session.query(Director).filter(Director.id == uid).one()
            return director_schema.dump(director), 200
        except Exception as e:
            return str(e), 404

    def put(self, uid):
        with app.app_context():
            with db.session.begin():
                req_json = request.get_json()
                director = Director.query.get(uid)

                director.name = req_json['name']

                db.session.add(director)
                db.session.commit()

            return '', 204

    def delete(self, uid):
        with app.app_context():
            with db.session.begin():
                director = Director.query.get(uid)
                db.session.delete(director)
                db.session.commit()

        return '', 204


@genres_ns.route('/')
class GenresView(Resource):
    def get(self):
        return [genre['name'] for genre in genres_schema.dump(Genre.query.all())], 200

    def post(self):
        req_json = request.get_json()
        new_genre = Genre(**req_json)

        with app.app_context():
            with db.session.begin():
                db.session.add(new_genre)
                db.session.commit()

        return '', 201


@genres_ns.route('/<int:uid>')
class GenreView(Resource):
    def get(self, uid):
        try:
            genre = db.session.query(Genre).filter(Genre.id == uid).one()
            return genre_schema.dump(genre), 200
        except Exception as e:
            return str(e), 404

    def put(self, uid):
        with app.app_context():
            with db.session.begin():
                req_json = request.get_json()
                genre = Genre.query.get(uid)

                genre.name = req_json['name']

                db.session.add(genre)
                db.session.commit()

            return '', 204

    def delete(self, uid):
        with app.app_context():
            with db.session.begin():
                genre = Genre.query.get(uid)
                db.session.delete(genre)
                db.session.commit()

        return '', 204


if __name__ == '__main__':
    app.run()
