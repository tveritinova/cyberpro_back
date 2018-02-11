
from flask import Flask, jsonify, request
import json
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.exc import IntegrityError, InvalidRequestError, OperationalError
from secure_info import user, password, host, port, socket
from collections import defaultdict
import ast
import datetime


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
            if type(res_dict[cols[i]]) is datetime.datetime:
                res_dict[cols[i]] = str(res_dict[cols[i]])
            if type(res_dict[cols[i]]) is datetime.date:
                res_dict[cols[i]] = str(res_dict[cols[i]])
    return res_dict


def create(testing=False, debug=False):
    app = Flask(__name__)
    app.config['DEBUG'] = debug

    crashed_master = None
    data = nested_dict()

    for i in range(2):
        for r in ['m', 's']:
            try:
                data[i][r]['engine'] = create_engine('mysql://'+user+':'+password+'@'+host[i][r]+':'+port[i][r] +
                                                     '/db'+str(i+1)+'?unix_socket='+socket[i][r])
            except OperationalError:
                cur_r = ['m','s'].remove(r)[0]
                data[i][r]['engine'] = create_engine('mysql://'+user+':'+password+'@'+host[i][cur_r]+':'+port[i][cur_r]+
                                                     '/db'+str(i+1)+'?unix_socket='+socket[i][cur_r])
                if r == 'm':
                    crashed_master = i

            data[i][r]['session'] = sessionmaker(bind=data[i][r]['engine'])()
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
        if crashed_master == choose(game_id):
            return 'Database server crashed, switched to readonly mode', 523
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
        cur = data[choose(game_id)]['m']
        if crashed_master == choose(game_id):
            return 'Database server crashed, switched to readonly mode', 523
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

    @app.route('/games/<int:game_id>/tournaments', methods=['GET'])
    def get_tournaments(game_id):
        cur = data[choose(game_id)]['s' if not testing else 'm']
        tournaments = cur['base'].classes.tournaments
        res_data = cur['session'].query(tournaments).all()
        res_dict = [get_json(tournament) for tournament in res_data]
        return jsonify(tournaments=res_dict), 200

    @app.route('/games/<int:game_id>/tournaments', methods=['POST'])
    def post_tournaments(game_id):
        cur = data[choose(game_id)]['m']
        if crashed_master == choose(game_id):
            return 'Database server crashed, switched to readonly mode', 523
        tournaments = cur['base'].classes.tournaments

        name = ast.literal_eval(request.data).get('name')
        start_date = ast.literal_eval(request.data).get('start_date')
        end_date = ast.literal_eval(request.data).get('end_date')

        if name is None or start_date is None or end_date is None:
            return 'Missed data', 400

        cur['session'].add(tournaments(name=name, start_date=start_date, end_date=end_date))

        try:
            if testing:
                cur['session'].flush()
            else:
                cur['session'].commit()
        except IntegrityError as e:
            if e.orig[0] == 1062:
                return 'Unique constraint failed', 400
            else:
                return '', 400

        res_data = cur['session'].query(tournaments).filter(tournaments.name == name).one()

        return jsonify(get_json(res_data)), 201

    @app.route('/games/<int:game_id>/tournaments/<int:tournament_id>', methods=['GET'])
    def get_tournament(game_id, tournament_id):
        cur = data[choose(game_id)]['s' if not testing else 'm']
        tournaments = cur['base'].classes.tournaments
        res_data = cur['session'].query(tournaments).filter(tournaments.id == tournament_id).one()
        return jsonify(get_json(res_data)), 200

    @app.route('/games/<int:game_id>/matches', methods=['GET'])
    def get_matches(game_id):
        cur = data[choose(game_id)]['s' if not testing else 'm']
        matches = cur['base'].classes.matches
        res_data = cur['session'].query(matches).all()
        res_dict = [get_json(match) for match in res_data]
        return jsonify(matches=res_dict), 200

    @app.route('/games/<int:game_id>/matches', methods=['POST'])
    def post_match(game_id):
        cur = data[choose(game_id)]['m']
        if crashed_master == choose(game_id):
            return 'Database server crashed, switched to readonly mode', 523
        matches = cur['base'].classes.matches

        tournament_id = ast.literal_eval(request.data).get('tournament_id')
        first_team_id = ast.literal_eval(request.data).get('first_team_id')
        second_team_id = ast.literal_eval(request.data).get('second_team_id')
        num_in_stage = ast.literal_eval(request.data).get('num_in_stage')
        date = ast.literal_eval(request.data).get('date')

        if tournament_id is None or first_team_id is None or second_team_id is None\
                or num_in_stage is None or date is None:
            return 'Missed data', 400

        cur['session'].add(matches(tournament_id=tournament_id, first_team_id=first_team_id,
                                   second_team_id=second_team_id, num_in_stage=num_in_stage, date=date))

        try:
            if testing:
                cur['session'].flush()
            else:
                cur['session'].commit()
        except IntegrityError as e:
            if e.orig[0] == 1062:
                return 'Unique constraint failed', 400
            else:
                return '', 400

        res_data = cur['session'].query(matches).filter(matches.tournament_id == tournament_id,
                                                        matches.date == date).one()

        return jsonify(get_json(res_data)), 201

    @app.route('/games/<int:game_id>/matches/<int:match_id>', methods=['GET'])
    def get_match(game_id, match_id):
        cur = data[choose(game_id)]['s' if not testing else 'm']
        matches = cur['base'].classes.matches
        res_data = cur['session'].query(matches).filter(matches.id == match_id).one()
        return jsonify(get_json(res_data)), 200

    @app.route('/games/<int:game_id>/tournaments/<int:tournament_id>/matches', methods=['GET'])
    def get_match_for_tournament(game_id, tournament_id):
        cur = data[choose(game_id)]['s' if not testing else 'm']
        matches = cur['base'].classes.matches
        res_data = cur['session'].query(matches).filter(matches.tournament_id == tournament_id).all()
        return jsonify(matches=[get_json(d) for d in res_data]), 200

    @app.route('/games/<int:game_id>/transactions', methods=['GET'])
    def get_transactions(game_id):
        cur = data[choose(game_id)]['s' if not testing else 'm']
        transactions = cur['base'].classes.matches
        res_data = cur['session'].query(transactions).all()
        return jsonify(transactions=[get_json(d) for d in res_data]), 200

    @app.route('/games/<int:game_id>/transactions', methods=['POST'])
    def post_transactions(game_id):
        cur = data[choose(game_id)]['m']
        if crashed_master == choose(game_id):
            return 'Database server crashed, switched to readonly mode', 523
        transactions = cur['base'].classes.players_transactions
        players = cur['base'].classes.players

        player_id = ast.literal_eval(request.data).get('player_id')
        from_team_id = ast.literal_eval(request.data).get('from_team_id')
        to_team_id = ast.literal_eval(request.data).get('to_team_id')
        date = ast.literal_eval(request.data).get('date')

        if player_id is None or from_team_id is None or to_team_id is None or date is None:
            return 'Missed data', 400

        cur['session'].add(transactions(player_id=player_id, from_team_id=from_team_id,
                                        to_team_id=to_team_id, date=date))
        cur['session'].query(players).filter(players.id == player_id).update({'team_id': to_team_id})

        try:
            if testing:
                cur['session'].flush()
            else:
                cur['session'].commit()
        except IntegrityError as e:
            if e.orig[0] == 1062:
                return 'Unique constraint failed', 400
            else:
                return '', 400

        res_data = cur['session'].query(transactions).filter(transactions.player_id == player_id,
                                                             transactions.date == date).one()

        return jsonify(get_json(res_data)), 201

    @app.route('/games/<int:game_id>/transactions/<int:transaction_id>', methods=['GET'])
    def get_transaction(game_id, transaction_id):
        cur = data[choose(game_id)]['m']
        transactions = cur['base'].classes.players_transactions
        res_data = cur['session'].query(transactions).filter(transactions.id == transaction_id).one()
        return jsonify(get_json(res_data)), 200

    @app.route('/games/<int:game_id>/tournaments/<int:tournament_id>/teams', methods=['POST'])
    def post_team_for_tournament(game_id, tournament_id):
        cur = data[choose(game_id)]['m']
        if crashed_master == choose(game_id):
            return 'Database server crashed, switched to readonly mode', 523
        tournament_command = cur['base'].classes.tournament_command

        team_id = ast.literal_eval(request.data).get('team_id')

        if team_id is None:
           return 'Missed data', 400

        cur['session'].add(tournament_command(tournament_id=tournament_id, team_id=team_id))

        try:
            if testing:
                cur['session'].flush()
            else:
                cur['session'].commit()
        except IntegrityError as e:
            if e.orig[0] == 1062:
                return 'Unique constraint failed', 400
            else:
                return '', 400

        return '', 201

    @app.route('/games/<int:game_id>/tournaments/<int:tournament_id>/teams', methods=['GET'])
    def get_teams_for_tournament(game_id, tournament_id):
        cur = data[choose(game_id)]['s' if not testing else 'm']
        tournament_command = cur['base'].classes.tournament_command
        teams = cur['base'].classes.teams

        res_data = cur['session'].query(tournament_command)\
            .filter(tournament_command.tournament_id == tournament_id).all()

        res = [cur['session'].query(teams).filter(teams.id == row.team_id).one() for row in res_data]

        return jsonify(teams=[get_json(ins) for ins in res]), 200

    @app.route('/games/<int:game_id>/teams/<int:team_id>/tournaments', methods=['GET'])
    def get_tournaments_for_team(game_id, team_id):
        cur = data[choose(game_id)]['s' if not testing else 'm']
        tournament_command = cur['base'].classes.tournament_command
        tournaments = cur['base'].classes.tournaments

        res_data = cur['session'].query(tournament_command)\
            .filter(tournament_command.team_id == team_id).all()

        res = [cur['session'].query(tournaments).filter(tournaments.id == row.tournament_id).one()
               for row in res_data]

        return jsonify(tournaments=[get_json(ins) for ins in res]), 200

    return app
