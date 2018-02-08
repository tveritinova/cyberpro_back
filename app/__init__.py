from flask import Flask, jsonify
from sqlalchemy import *
from secure_info import user, password, host_m_1, port_m_1, host_m_2, port_m_2, host_s_1, port_s_1, host_s_2, port_s_2

app = Flask(__name__)
#db = SQLAlchemy(app)

engine_m_1 = create_engine('mysql://'+user+':'+password+'@'+host_m_1+':'+port_m_1+'/db1.db')
engine_s_1 = create_engine('mysql://'+user+':'+password+'@'+host_s_1+':'+port_s_1+'/db1.db')
engine_m_2 = create_engine('mysql://'+user+':'+password+'@'+host_m_2+':'+port_m_2+'/db1.db')
engine_s_2 = create_engine('mysql://'+user+':'+password+'@'+host_s_2+':'+port_s_2+'/db1.db')

metadata_m_1 = MetaData(engine_m_1)
metadata_s_1 = MetaData(engine_s_1)
metadata_m_2 = MetaData(engine_m_2)
metadata_s_2 = MetaData(engine_s_2)


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
    raise Exception(games_s_1.select().execute())
    return {}, 200
