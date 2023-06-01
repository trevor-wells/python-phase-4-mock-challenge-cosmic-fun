from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Scientist, Planet, Mission

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

class Index(Resource):

    def get(self):
        return make_response("<h1>Home Page</h1>", 200)

class Scientists(Resource):

    def get(self):
        scientists = [{"id": scientist.id, "name": scientist.name, "field_of_study": scientist.field_of_study, "avatar": scientist.avatar} for scientist in Scientist.query.all()]
        return scientists, 200

    def post(self):
        try:
            data = request.get_json()
            new_scientist = Scientist(
                name = data["name"],
                field_of_study = data["field_of_study"],
                avatar = data["avatar"]
            )
            db.session.add(new_scientist)
            db.session.commit()
            return new_scientist.to_dict(), 201
        except ValueError:
            return {"errors": ["validation errors"]}, 403

class ScientistById(Resource):

    def get(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).first()
        if scientist:
            scientist_dict = scientist.to_dict(rules=('planets',))
            return scientist_dict, 200
        return {"error": "Scientist not found"}, 400

    def patch(self, id):
        data = request.get_json()
        try:
            scientist = Scientist.query.filter(Scientist.id == id).first()
            if not scientist:
                return {"error": "Scientist not found"}, 404
            if data['name']:
                scientist.name = data['name']
            if data['field_of_study']:
                scientist.field_of_study = data['field_of_study']
            if data['avatar']:
                scientist.avatar = data['avatar']
            db.session.add(scientist)
            db.session.commit()
            return scientist.to_dict(), 202
        except ValueError:
            return {"errors": ["validation errors"]}, 403

    def delete(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).first()
        if not scientist:
            return {"error": "Scientist not found"}, 404
        db.session.delete(scientist)
        db.session.commit()
        return {}, 204


class Planets(Resource):

    def get(self):
        planets = [{"id": planet.id, "name": planet.name, "distance_from_earth": planet.distance_from_earth, "nearest_star": planet.nearest_star, "image": planet.image} for planet in Planet.query.all()]
        return planets, 200

class Missions(Resource):

    def post(self):
        try:
            data = request.get_json()
            new_mission = Mission(
                name = data["name"],
                scientist_id = data["scientist_id"],
                planet_id = data["planet_id"]
            )
            db.session.add(new_mission)
            db.session.commit()
            return new_mission.planet.to_dict(), 201
        except ValueError:
            return {"errors": ["validation errors"]}, 403

api.add_resource(Index, '/')
api.add_resource(Scientists, '/scientists')
api.add_resource(ScientistById, '/scientists/<int:id>')
api.add_resource(Planets, '/planets')
api.add_resource(Missions, '/missions')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
