from flask import Flask, jsonify, request
import json
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from secure_info import user, password, host, port, socket
from collections import defaultdict

app = Flask(__name__)
app.config['DEBUG'] = True
#db = SQLAlchemy(app)

'''
engine_m_1 = create_engine('mysql://'+user+':'+password+'@'+host_m_1+':'+port_m_1+'/db1?unix_socket='+socket_m_1)
engine_s_1 = create_engine('mysql://'+user+':'+password+'@'+host_s_1+':'+port_s_1+'/db1?unix_socket='+socket_s_1)
engine_m_2 = create_engine('mysql://'+user+':'+password+'@'+host_m_2+':'+port_m_2+'/db1?unix_socket='+socket_m_2)
engine_s_2 = create_engine('mysql://'+user+':'+password+'@'+host_s_2+':'+port_s_2+'/db1?unix_socket='+socket_s_2)

metadata_m_1 = MetaData(engine_m_1)
metadata_s_1 = MetaData(engine_s_1)
metadata_m_2 = MetaData(engine_m_2)
metadata_s_2 = MetaData(engine_s_2)

session_m_1 = sessionmaker(bind=engine_m_1)()
session_s_1 = sessionmaker(bind=engine_s_1)()

games_m_1 = {}
games_s_1 = {}
games_m_1['table'] = Table('games', metadata_m_1, autoload=True)
games_m_1['cols'] = [col['name'] for col in session_m_1.query(games_m_1['table']).column_descriptions]
games_s_1['table'] = Table('games', metadata_s_1, autoload=True)
games_s_1['cols'] = [col['name'] for col in session_s_1.query(games_s_1['table']).column_descriptions]
'''


def nested_dict():
    return defaultdict(nested_dict)

data = nested_dict()

for i in range(2):
    for r in ['m', 's']:
        data[i][r]['engine'] = create_engine('mysql://'+user+':'+password+'@'+host[i][r]+':'+port[i][r] +
                                             '/db'+str(i+1)+'?unix_socket='+socket[i][r])
        data[i][r]['metadata'] = MetaData(data[i][r]['engine'])
        data[i][r]['session'] = sessionmaker(bind=data[i][r]['engine'])()
        if i == 0: data[i][r]['games'] = Table('games', data[i][r]['metadata'], autoload=True)
        data[i][r]['teams'] = Table('teams', data[i][r]['metadata'], autoload=True)


def choose(game_id):
    return game_id % 2


def get_cols(session, table):
    return [col['name'] for col in session.query(table).column_descriptions]


def get_json(tuple, cols):
    res_dict = {}
    for i in range(len(cols)):
        res_dict[cols[i]] = tuple[i]
    return res_dict


@app.route('/')
def root():
    return 'Welcome to cyber.pro portal!'


@app.route('/games', methods=['GET'])
def get_games():
    cur = data[0]['s']
    res_data = cur['session'].query(cur['games']).all()
    res_dict = [get_json(game, get_cols(cur['session'],cur['games'])) for game in res_data]
    return jsonify(games=res_dict), 200


@app.route('/games/<int:game_id>', methods=['GET'])
def get_game(game_id):
    cur = data[0]['s']
    print cur['session'].query(cur['games']).filter(cur['games'].c.id == game_id)
    res_data = cur['session'].query(cur['games']).filter(cur['games'].c.id == game_id).one()
    return jsonify(get_json(res_data, get_cols(cur['session'], cur['games']))), 200


@app.route('/games/<int:game_id>/teams', methods=['GET'])
def get_teams(game_id):
    cur = data[choose(game_id)]['s']
    res_data = cur['session'].query(cur['teams']).filter(cur['teams'].c.game_id == game_id).all()
    res_dict = [get_json(game, get_cols(cur['session'], cur['teams'])) for game in res_data]
    return jsonify(teams=res_dict), 200


@app.route('/games/<int:game_id>/teams', methods=['POST'])
def put_teams(game_id):
    cur = data[choose(game_id)]['m']

    name = request.get_json()['name']
    country = request.get_json()['country']

    cur['teams'].insert().values(name=name, country=country)

    return 200