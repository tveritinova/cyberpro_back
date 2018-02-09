from flask import Flask, jsonify
import json
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from secure_info import user, password, host_m_1, port_m_1, host_m_2, port_m_2, host_s_1, port_s_1, host_s_2, port_s_2,\
    socket_m_1,socket_s_1,socket_m_2,socket_s_2

app = Flask(__name__)
app.config['DEBUG'] = True
#db = SQLAlchemy(app)

engine_m_1 = create_engine('mysql://'+user+':'+password+'@'+host_m_1+':'+port_m_1+'/db1?unix_socket='+socket_m_1)
engine_s_1 = create_engine('mysql://'+user+':'+password+'@'+host_s_1+':'+port_s_1+'/db1?unix_socket='+socket_s_1)
engine_m_2 = create_engine('mysql://'+user+':'+password+'@'+host_m_2+':'+port_m_2+'/db1?unix_socket='+socket_m_2)
engine_s_2 = create_engine('mysql://'+user+':'+password+'@'+host_s_2+':'+port_s_2+'/db1?unix_socket='+socket_s_2)

metadata_m_1 = MetaData(engine_m_1)
metadata_s_1 = MetaData(engine_s_1)
metadata_m_2 = MetaData(engine_m_2)
metadata_s_2 = MetaData(engine_s_2)

session_s_1 = sessionmaker(bind=engine_s_1)()

games_m_1 = Table('games', metadata_m_1, autoload=True)
games_s_1 = Table('games', metadata_s_1, autoload=True)

#sharding_dict = {}


def choose(game_id):
    if game_id % 2 == 0:
        return 'db1'
    else:
        return 'db2'


@app.route('/')
def root():
    return 'Welcome to cyber.pro portal!'


@app.route('/games', methods=['GET'])
def get_games():
    #games_s_1.select().execute()
    print games_m_1
    data = session_s_1.query(games_s_1).all()
    data_all = []
    cols =  [col['name'] for col in session_s_1.query(games_s_1).column_descriptions]
    for game in data:
        res_dict = {}
        for i in len(game):
            res_dict[cols[i]] = game[i]
        data_all.append(res_dict)
    return jsonify(games=data_all), 200
