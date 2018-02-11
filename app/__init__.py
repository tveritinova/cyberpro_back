
from flask import Flask, jsonify, request
import json
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from secure_info import user, password, host, port, socket
from collections import defaultdict
import ast


def nested_dict():
    return defaultdict(nested_dict)


def choose(game_id):
    return game_id % 2


def get_json(instance):
    res_dict = {}
    cols = instance.__class__.__table__.c.keys()
    for i in range(len(cols)):
        if getattr(instance, cols[i]) is not None:
            res_dict[cols[i]] = getattr(instance, cols[i])
            if type(res_dict[cols[i]]) is bool:
                res_dict[cols[i]] = int(res_dict[cols[i]])
    return res_dict


def create(testing=False, debug=False):
    app = Flask(__name__)
    app.config['DEBUG'] = debug

    data = nested_dict()

    for i in range(2):
        for r in ['m', 's']:
            data[i][r]['engine'] = create_engine('mysql://'+user+':'+password+'@'+host[i][r]+':'+port[i][r] +
                                                 '/db'+str(i+1)+'?unix_socket='+socket[i][r])
            #data[i][r]['metadata'] = MetaData(data[i][r]['engine'])
            data[i][r]['session'] = sessionmaker(bind=data[i][r]['engine'])()
            #data[i][r]['games'] = Table('games', data[i][r]['metadata'], autoload=True)
            #data[i][r]['games_exc'] = ['img_path']
            #data[i][r]['teams'] = Table('teams', data[i][r]['metadata'], autoload=True)
            #data[i][r]['teams_exc'] = ['img_path']

            data[i][r]['base'] = automap_base()
            data[i][r]['base'].prepare(data[i][r]['engine'], reflect=True)

    @app.route('/')
    def root():
        return 'Welcome to cyber.pro portal!'

    @app.route('/games', methods=['GET'])
    def get_games():
        cur = data[0]['s' if not testing else 'm']
        games = cur['base'].classes.games
        res_data = cur['session'].query(games).all()
        res_dict = [get_json(game) for game in res_data]
        return jsonify(games=res_dict), 200

    @app.route('/games/<int:game_id>', methods=['GET'])
    def get_game(game_id):
        cur = data[0]['s' if not testing else 'm']
        games = cur['base'].classes.games
        try:
            res_data = cur['session'].query(games).filter(games.id == game_id).one()
        except NoResultFound:
            return '', 204
        return jsonify(get_json(res_data)), 200

    @app.route('/games/<int:game_id>/teams', methods=['GET'])
    def get_teams(game_id):
        cur = data[choose(game_id)]['s' if not testing else 'm']
        teams = cur['base'].classes.teams
        res_data = cur['session'].query(teams).filter(teams.game_id == game_id).all()
        res_dict = [get_json(game) for game in res_data]
        return jsonify(teams=res_dict), 200

    @app.route('/games/<int:game_id>/teams', methods=['POST'])
    def post_teams(game_id):
        cur = data[choose(game_id)]['m']
        teams = cur['base'].classes.teams

        name = ast.literal_eval(request.data).get('name')
        country = ast.literal_eval(request.data).get('country')

        if not name or not country:
            return 'Missed data', 400

        cur['session'].add(teams(name=name, country=country, game_id=game_id))

        try:
            if testing:
                cur['session'].flush()
            else:
                cur['session'].commit()
        except IntegrityError as e:
            if e.orig[0] == 1062:
                return 'Name unique constraint failed', 400

        res_data = cur['session'].query(teams).filter(teams.name == name).one()

        return jsonify(get_json(res_data)), 201

    @app.route('/games/<int:game_id>/teams/<int:team_id>', methods=['GET'])
    def get_team(game_id, team_id):
        cur = data[choose(game_id)]['s' if not testing else 'm']
        teams = cur['base'].classes.teams

        try:
            res_data = cur['session'].query(teams).filter(teams.id == team_id).one()
        except NoResultFound:
            return '', 204
        except InvalidRequestError:
            return '', 204

        return jsonify(get_json(res_data)), 200

    @app.route('/games/<int:game_id>/teams/<int:team_id>/players', methods=['GET'])
    def get_players(game_id, team_id):
        cur = data[choose(game_id)]['s' if not testing else 'm']
        players = cur['base'].classes.players

        res_data = cur['session'].query(players).filter(players.team_id == team_id)
        res_dict = [get_json(player) for player in res_data]
        return jsonify(players=res_dict), 200

    @app.route('/games/<int:game_id>/teams/<int:team_id>/players', methods=['POST'])
    def post_players(game_id, team_id):
        cur = data[choose(game_id)]['s' if not testing else 'm']
        players = cur['base'].classes.players

        name = ast.literal_eval(request.data).get('name')
        nickname = ast.literal_eval(request.data).get('nickname')
        country = ast.literal_eval(request.data).get('country')
        is_cap = ast.literal_eval(request.data).get('is_cap')

        if not name or not nickname or not country or is_cap is None:
            return 'Missed data', 400

        cur['session'].add(players(name=name, nickname=nickname, country=country, is_cap=is_cap, team_id=team_id))

        try:
            if testing:
                cur['session'].flush()
            else:
                cur['session'].commit()
        except IntegrityError as e:
            if e.orig[0] == 1062:
                return 'Unique constraint failed', 400

        res_data = cur['session'].query(players).filter(players.name == name, players.nickname == nickname,
                                                        players.country == country).one()

        return jsonify(get_json(res_data)), 201

    @app.route('/games/<int:game_id>/teams/<int:team_id>/players/<int:player_id>', methods=['GET'])
    def get_player(game_id, team_id, player_id):
        cur = data[choose(game_id)]['s' if not testing else 'm']
        players = cur['base'].classes.players

        res_data = cur['session'].query(players).filter(players.id == player_id).one()
        return jsonify(get_json(res_data)), 200

    @app.route('/tournaments', methods=['GET'])
    def get_tournaments():
        cur = data[0]['s' if not testing else 'm']
        tournaments = cur['base'].classes.tournaments
        res_data = cur['session'].query(tournaments).all()
        res_dict = [get_json(tournament) for tournament in res_data]
        return jsonify(games=res_dict), 200

    return app
