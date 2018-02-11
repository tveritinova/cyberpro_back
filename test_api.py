import unittest
from app import create
import ast
import json
import datetime


class BackApiTestCase(unittest.TestCase):
    """This class represents the api test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create(debug=True, testing=True)
        self.client = self.app.test_client
        self.games = [{'name': 'dota2', 'id': 1},
                      {'name': 'cs-go', 'id': 2},
                      {'name': 'lol', 'id': 3},
                      {'name': 'hearthstone', 'id': 4},
                      {'name': 'overwatch', 'id': 5}]

        self.first_team = {'name': 'team1', 'country': 'russia'}
        result = self.client().post('/games/1/teams',
                                    data=json.dumps(self.first_team), headers=self.headers_to_post)
        self.first_team_id = ast.literal_eval(result.data)['id']

        self.second_team = {'name': 'team2', 'country': 'russia'}
        rv = self.client().post('/games/1/teams',
                                data=json.dumps(self.second_team), headers=self.headers_to_post)
        self.second_team_id = ast.literal_eval(rv.data)['id']

        self.player = {'name': 'Test Player', 'nickname': 'test_player',
                       'country': 'China', 'is_cap': False, 'team_id': self.first_team_id}
        result = self.client().post('/games/1/teams/1/players',
                                    data=json.dumps(self.player), headers=self.headers_to_post)
        self.player_id = ast.literal_eval(result.data)['id']

        self.tournament = {'name': 'test tournament', 'start_date': datetime.date(2018, 2, 11),
                           'end_date': datetime.date(2018, 2, 12)}
        result = self.client().post('/tournaments', data=self.tournament, headers=self.headers_to_post)
        self.tournament_id = ast.literal_eval(result.data)['id']

        self.match = {'num_in_stage': 1, 'date': datetime.datetime(2018, 2, 11, 11),
                      'tournament_id': self.tournament_id, 'first_team_id': self.first_team_id,
                      'second_team_id': self.second_team_id}
        result = self.client().post('/matches', data=self.match, headers=self.headers_to_post)
        self.match_id = ast.literal_eval(result.data)['id']

        self.transaction = {'date': datetime.date(2018, 2, 12),
                            'player_id': self.player_id,
                            'from_team_id': self.first_team_id,
                            'to_team_id': self.second_team_id}

        result = self.client().post('/transactions', data=self.transaction, header=self.headers_to_post)
        self.assertEqual(result.status_code, 201)
        self.transaction_id = ast.literal_eval(result.data)['id']

        result = self.client().post('/tournaments', data={'tournament_id': self.tournament_id,
                                                          'team_id': self.first_team_id})
        self.tournament_id = ast.literal_eval(result.data)['id']

        self.headers_to_post = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    def test_api_can_get_all_games(self):
        """Test API can get games. (GET request)"""
        res = self.client().get('/games')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(ast.literal_eval(res.data)['games'], self.games)

    def test_api_can_get_game_by_id(self):
        """Test API can get a single game by using it's id. (GET request)"""
        result = self.client().get('/games/1')
        self.assertEqual(result.status_code, 200)
        self.assertEqual(ast.literal_eval(result.data)['id'], 1)
        self.assertEqual(ast.literal_eval(result.data)['name'], 'dota2')
        result = self.client().get('/games/0')
        self.assertEqual(result.status_code, 204)
        result = self.client().get('/games/6')
        self.assertEqual(result.status_code, 204)

    def test_api_can_get_team(self):
        """Test API can get a team by id. (GET request)"""
        result = self.client().get('/games/1/teams/'+ str(self.first_team_id))
        self.assertEqual(result.status_code, 200)
        self.assertEqual(ast.literal_eval(result.data)['name'], self.first_team['name'])
        self.assertEqual(ast.literal_eval(result.data)['country'], self.first_team['country'])

    def test_api_can_post_team(self):
        """Test API can add a team. (POST request)"""
        results = self.client().get('/games/1/teams/'+str(self.second_team_id))
        self.assertEqual(results.status_code, 200)
        self.assertEqual(ast.literal_eval(results.data)['name'], self.second_team['name'])
        self.assertEqual(ast.literal_eval(results.data)['country'], self.second_team['country'])
        rv = self.client().post('/games/1/teams',
                                data=json.dumps(self.second_team), headers=self.headers_to_post)
        self.assertEqual(rv.status_code, 400)
        result = self.client().get('/games/1/teams/'+str(ast.literal_eval(rv.data)['id']+1))
        self.assertEqual(result.status_code, 404)

    def test_api_can_post_and_get_all_players(self):
        """Test API can get all players by team. (GET request)"""
        result = self.client().get('/games/1/teams/1/players/')
        self.assertEqual(result.status_code, 200)

    def test_api_can_get_player(self):
        """Test API can get a player by team. (GET request)"""
        result = self.client().get('/games/1/teams/1/players'+str(self.player_id))
        self.assertEqual(result.status_code, 200)
        data = ast.literal_eval(result.data)
        self.assertEqual(data['name'], self.player['name'])
        self.assertEqual(data['nickname'], self.player['nickname'])
        self.assertEqual(data['country'], self.player['country'])
        self.assertEqual(data['team_id'], self.player['team_id'])
        self.assertEqual(data['is_cap'], self.player['is_cap'])

    def test_api_can_get_tournaments(self):
        """Test API can get all tournaments and one by id. (GET request)"""
        result = self.client().get('/tournaments')
        self.assertEqual(result.status_code, 200)

    def test_api_can_get_tournament(self):
        result = self.client().get('/tournaments/'+str(self.tournament_id))
        self.assertEqual(result.status_code, 200)
        data = ast.literal_eval(result.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data['name'], self.tournament['name'])
        self.assertEqual(data['start_date'], len(self.tournament['start_date']))
        self.assertEqual(data['end_date'], len(self.tournament['end_date']))

    def test_get_matches(self):
        result = self.client().get('/matches/')
        self.assertEqual(result.status_code, 200)

    def test_get_match(self):
        result = self.client().get('/matches/' + str(self.match_id))
        self.assertEqual(result.status_code, 200)
        data = ast.literal_eval(result.data)
        self.assertEqual(data['id'], self.match_id)
        self.assertEqual(data['tournament_id'], self.match['tournament_id'])
        self.assertEqual(data['first_team_id'], self.match['first_team_id'])
        self.assertEqual(data['second_team_id'], self.match['second_team_id'])
        self.assertEqual(data['num_in_stage'], self.match['num_in_stage'])
        self.assertEqual(data['date'], str(self.match['date']))

    def test_players_transactions(self):
        result = self.client().get('/transactions/'+str(self.transaction_id))
        self.assertEqual(result.status_code, 200)
        data = ast.literal_eval(result.data)
        self.assertEqual(data['player_id'], self.transaction['player_id'])
        self.assertEqual(data['from_team_id'], self.transaction['from_team_id'])
        self.assertEqual(data['to_team_id'], self.transaction['to_team_id'])
        self.assertEqual(data['date'], self.transaction['date'])

    def test_get_transactions(self):
        result = self.client().get('/transactions')
        self.assertEqual(result.status_code, 200)

    def test_team_in_tournament(self):
        result = self.client().get('/tournaments/'+str(self.tournament_id)+'/teams')
        self.assertEqual(result.status_code, 200)
        data = ast.literal_eval(result.data)
        self.assertIn(data['teams_id'], self.first_team_id)

    def test_tournament_for_team(self):
        result = self.client().get('/teams/'+str(self.first_team_id)+'/tournaments')
        self.assertEqual(result.status_code, 200)
        data = ast.literal_eval(result.data)
        self.assertIn(data['tournaments_id'], self.tournament_id)

    def tearDown(self):
        """teardown all initialized variables."""

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()