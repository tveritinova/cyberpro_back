from flask import Flask, jsonify, request
import json
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from secure_info import user, password, host, port, socket
from collections import defaultdict


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


def create():
    app = Flask(__name__)
    app.config['DEBUG'] = True

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

    @app.route('/')
    def root():
        return 'Welcome to cyber.pro portal!'


    @app.route('/games', methods=['GET'])
    def get_games():
        cur = data[0]['s']
        res_data = cur['session'].query(cur['games']).all()
        res_dict = [get_json(game, get_cols(cur['session'],cur['games']),cur['games_exc']) for game in res_data]
        return jsonify(games=res_dict), 200


    @app.route('/games/<int:game_id>', methods=['GET'])
    def get_game(game_id):
        cur = data[0]['s']
        try:
            res_data = cur['session'].query(cur['games']).filter(cur['games'].c.id == game_id).one()
        except NoResultFound:
            return '', 204
        return jsonify(get_json(res_data, get_cols(cur['session'], cur['games']), cur['games_exc'])), 200


    @app.route('/games/<int:game_id>/teams', methods=['GET'])
    def get_teams(game_id):
        cur = data[choose(game_id)]['s']
        res_data = cur['session'].query(cur['teams']).filter(cur['teams'].c.game_id == game_id).all()
        res_dict = [get_json(game, get_cols(cur['session'], cur['teams']), cur['teams_exc']) for game in res_data]
        return jsonify(teams=res_dict), 200


    @app.route('/games/<int:game_id>/teams', methods=['POST'])
    def put_teams(game_id):
        cur = data[choose(game_id)]['m']

        name = request.args.get('name')
        country = request.args.get('country')

        query = "insert into teams (name, country, game_id)" \
                "select "+name+","+country+",id" \
                "from games" \
                "where id = "+game_id+ \
                "limit 1"
        cur['engine'].execute(query)
        return 'success', 201


    @app.route('/games/<int:game_id>/teams/<int:team_id>', methods=['GET'])
    def get_team(game_id, team_id):
        cur = data[choose(game_id)]['s']

        try:
            res_data = cur['session'].query(cur['teams']).filter(cur['teams'].c.id == team_id).one()
        except NoResultFound:
            return '', 204

        return jsonify(get_json(res_data, get_cols(cur['session'], cur['teams']), cur['teams_exc'])), 200

    return app