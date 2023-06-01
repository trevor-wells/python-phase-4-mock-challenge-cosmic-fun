from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy

metadata = MetaData(naming_convention = {"fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",})
db = SQLAlchemy(metadata = metadata)

class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    serialize_rules = ('-missions.scientist', '-planet.scientists',)

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)
    field_of_study = db.Column(db.String)
    avatar = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default = db.func.now())
    updated_at = db.Column(db.DateTime, onupdate = db.func.now())

    missions = db.relationship('Mission', back_populates = 'scientist', cascade='all, delete-orphan')
    planets = association_proxy('missions', 'planet', creator=lambda pl: Mission(planet=pl))

    @validates('name, field_of_study')
    def validate_scientist(self, key, value):
        if key == 'name' and not value:
            raise ValueError("Scientist must have a name.")
        if key == 'name' and value in [scientist.name for scientist in Scientist.query.all()]:
            raise ValueError("Scientist's name must be unique.")
        if key == 'field_of_study' and not value:
            raise ValueError("Scientist must have a field of study.")
        return value
    
    def __repr__(self):
        return f'<Scientist {self.id}>'
        
class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'

    serialize_rules = ('-scientist.missions', '-planet.missions',)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default = db.func.now())
    updated_at = db.Column(db.DateTime, onupdate = db.func.now())

    scientist_id = db.Column(db.Integer, db.ForeignKey('scientists.id'))
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'))

    scientist = db.relationship('Scientist', back_populates='missions')
    planet = db.relationship('Planet', back_populates='missions')

    @validates('name, scientist, planet')
    def validate_mission(self, key, value):
        if not value:
            if key == 'name':
                raise ValueError("Mission must have a name.")
            elif key == 'scientist':
                raise ValueError("Mission must have a scientist.")
            elif key == 'planet':
                raise ValueError("Mission must have a planet.")
        if key == 'scientist' and value in self.scientists:
            raise ValueError("Scientists canot join the same mission twice.")
        return value
    
    def __repr__(self):
        return f'<Mission {self.id}>'

class Planet(db.Model, SerializerMixin):
    __tablename__ = 'planets'

    serialize_rules = ('-missions.planet', '-scientist.planets')

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    distance_from_earth = db.Column(db.String)
    nearest_star = db.Column(db.String)
    image = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default = db.func.now())
    updated_at = db.Column(db.DateTime, onupdate = db.func.now())

    missions = db.relationship('Mission', back_populates = 'planet', cascade='all, delete-orphan')
    scientists = association_proxy('missions', 'scientist', creator=lambda sc: Mission(scientist=sc))

    def __repr__(self):
        return f'<Planet {self.id}>'
