
from flask import Flask, jsonify, request
import json
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.exc import IntegrityError
from secure_info import user, password, host, port, socket
from collections import defaultdict
import ast


def nested_dict():
    return defaultdict(nested_dict)


def choose(game_id):
    return game_id % 2


def get_cols(session, table):
    return [col['name'] for col in session.query(table).column_descriptions]


def get_json(tuple, cols, exc):
    res_dict = {}
    for i in range(len(cols)):
        if cols[i] not in exc:
            res_dict[cols[i]] = tuple[i]
    return res_dict


def get_row(id, table, session):
    return session.query(table).filter(table.c.id == id).one()


def create(testing=False, debug=False):
    app = Flask(__name__)
    app.config['DEBUG'] = debug

    data = nested_dict()

    for i in range(2):
        for r in ['m', 's']:
            data[i][r]['engine'] = create_engine('mysql://'+user+':'+password+'@'+host[i][r]+':'+port[i][r] +
                                                 '/db'+str(i+1)+'?unix_socket='+socket[i][r])
            data[i][r]['metadata'] = MetaData(data[i][r]['engine'])
            data[i][r]['session'] = sessionmaker(bind=data[i][r]['engine'])()
            data[i][r]['games'] = Table('games', data[i][r]['metadata'], autoload=True)
            data[i][r]['games_exc'] = ['img_path']
            data[i][r]['teams'] = Table('teams', data[i][r]['metadata'], autoload=True)
            data[i][r]['teams_exc'] = ['img_path']

            data[i][r]['base'] = automap_base()
            data[i][r]['base'].prepare(data[i][r]['engine'], reflect=True)

    @app.route('/')
    def root():
        return 'Welcome to cyber.pro portal!'

    @app.route('/games', methods=['GET'])
    def get_games():
        cur = data[0]['s' if not testing else 'm']
        res_data = cur['session'].query(cur['games']).all()
        res_dict = [get_json(game, get_cols(cur['session'],cur['games']),cur['games_exc']) for game in res_data]
        return jsonify(games=res_dict), 200

    @app.route('/games/<int:game_id>', methods=['GET'])
    def get_game(game_id):
        cur = data[0]['s' if not testing else 'm']
        try:
            res_data = cur['session'].query(cur['games']).filter(cur['games'].c.id == game_id).one()
        except NoResultFound:
            return '', 204
        return jsonify(get_json(res_data, get_cols(cur['session'], cur['games']), cur['games_exc'])), 200

    @app.route('/games/<int:game_id>/teams', methods=['GET'])
    def get_teams(game_id):
        cur = data[choose(game_id)]['s' if not testing else 'm']
        res_data = cur['session'].query(cur['teams']).filter(cur['teams'].c.game_id == game_id).all()
        res_dict = [get_json(game, get_cols(cur['session'], cur['teams']), cur['teams_exc']) for game in res_data]
        return jsonify(teams=res_dict), 200

    @app.route('/games/<int:game_id>/teams', methods=['POST'])
    def post_teams(game_id):
        cur = data[choose(game_id)]['m']

        name = ast.literal_eval(request.data).get('name')
        country = ast.literal_eval(request.data).get('country')

        if not name or not country:
            return 'Missed name, country data', 400

        base = cur['base']
        cur['session'].add(base.classes.teams(name=name, country=country, game_id=game_id))

        # catch failed unique cons

        try:
            if testing:
                cur['session'].flush()
            else:
                cur['session'].commit()
        except IntegrityError as e:
            if e.orig[0] == 1062:
                return 'Name unique constraint failed', 400

        res_data = cur['session'].query(cur['teams']).filter(cur['teams'].c.name == name).one()

        return jsonify(get_json(res_data, get_cols(cur['session'],cur['teams']), cur['teams_exc'])), 201

    @app.route('/games/<int:game_id>/teams/<int:team_id>', methods=['GET'])
    def get_team(game_id, team_id):
        cur = data[choose(game_id)]['s' if not testing else 'm']

        try:
            res_data = cur['session'].query(cur['teams']).filter(cur['teams'].c.id == team_id).one()
        except NoResultFound:
            return '', 204

        return jsonify(get_json(res_data, get_cols(cur['session'], cur['teams']), cur['teams_exc'])), 200

    return app
