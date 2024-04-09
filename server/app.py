# !/usr/bin/env python3

from flask import Flask, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.get_json()
    
    strength = data.get('strength')
    power_id = data.get('power_id')
    hero_id = data.get('hero_id')
    
    if not all([strength, power_id, hero_id]):
        return make_response({"errors": ["Missing required fields"]}, 400)
    if strength not in ['Strong', 'Weak', 'Average']:
        return make_response({"errors": ["validation errors"]}, 400)
    
    hero = Hero.query.get(hero_id)
    power = Power.query.get(power_id)
    
    if hero is None or power is None:
        return make_response({"errors": ["Hero or Power not found"]}, 404)
    hero_power = HeroPower(strength=strength, hero=hero, power=power)
    try:
        db.session.add(hero_power)
        db.session.commit()
    except Exception as e:
        return make_response({"errors" : str(e)} , 400)
    
    response_data = {
        "id": hero_power.id,
        "hero_id": hero_power.hero_id,
        "power_id": hero_power.power_id,
        "strength": hero_power.strength,
        "hero": {
            "id": hero.id,
            "name": hero.name,
            "super_name": hero.super_name
        },
        "power": {
            "id": power.id,
            "name": power.name,
            "description": power.description
        }
    }
    response = make_response (
        response_data,
        200
    )
    return response


@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    power = Power.query.get(id)
    
    if power is None:
        return make_response({"error": "Power not found"}, 404)
    
    data = request.get_json()
    
    if 'description' in data:
        new_description = data['description']
        if len(new_description) < 20:
            return make_response({"errors": ["validation errors"]}, 400)
        try:
            power.description = new_description
            db.session.commit()
        except ValueError as e:
            return make_response({"errors" : str(e)}, 400)
        
    updated_power = {
        "id": power.id,
        "name": power.name,
        "description": power.description
    }
    response = make_response (
        updated_power,
        200
    )
    return response


@app.route('/powers/<int:id>')
def get_power(id):
    power = Power.query.get(id)
    
    if power is None:
        return make_response({"error": "Power not found"}, 404)
    
    power_dict = {
        "id": power.id,
        "name": power.name,
        "description": power.description
    }
    
    response = make_response (
        power_dict,
        200
    )
    return response


@app.route('/powers')
def get_powers():
    powers = Power.query.all()
    
    powers_list = []
    
    for power in powers:
        power_dict = {
            "id": power.id,
            "name": power.name,
            "description": power.description
        }
        powers_list.append(power_dict)
        
    response = make_response (
        powers_list,
        200
    )
    return response


@app.route('/heroes/<int:id>')
def get_hero(id):
    hero = Hero.query.get(id)
    
    if hero is None:
        return make_response({"error": "Hero not found"}, 404)
    
    hero_dict = {
        "id": hero.id,
        "name": hero.name,
        "super_name": hero.super_name,
        "hero_powers": []
    }
    
    for hero_power in hero.hero_powers:
        power = {
            "id": hero_power.power.id,
            "name": hero_power.power.name,
            "description": hero_power.power.description
        }
        
        hero_power_dict = {
            "id": hero_power.id,
            "hero_id": hero_power.hero_id,
            "power": power,
            "power_id": hero_power.power_id,
            "strength": hero_power.strength
        }
        
        hero_dict["hero_powers"].append(hero_power_dict)
        
    return make_response(hero_dict, 200)


@app.route('/heroes')
def get_heroes():
    heroes = []
    
    for hero in Hero.query.all():
        hero_dict = {
            "id": hero.id,
            "name": hero.name,
            "super_name": hero.super_name
        }
        heroes.append(hero_dict)
        
    response = make_response(
        heroes,
        200,
    )
    return response


@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

if __name__ == 'main':
    app.run(port=5555, debug=True)