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

        self.headers_to_post = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    def test_api_can_get_games(self):
        """Test API can get games. (GET request)"""
        res = self.client().get('/games')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(list(ast.literal_eval(res.data).keys()), ['games'])
        self.assertEqual(ast.literal_eval(res.data)['games'], self.games)

    def test_api_can_get_game(self):
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
        team = {'name': 'team1', 'country': 'russia'}
        result = self.client().post('/games/1/teams', data=json.dumps(team), headers=self.headers_to_post)
        self.assertEqual(result.status_code, 201)
        team_id = ast.literal_eval(result.data)['id']
        result = self.client().get('/games/1/teams/'+ str(team_id))
        self.assertEqual(result.status_code, 200)
        self.assertEqual(ast.literal_eval(result.data)['name'], team['name'])
        self.assertEqual(ast.literal_eval(result.data)['country'], team['country'])

    def test_api_can_get_teams(self):
        """Test API can get all teams. (GET request)"""
        result = self.client().get('/games/1/teams')
        self.assertEqual(result.status_code, 200)
        self.assertEqual(list(ast.literal_eval(result.data).keys()), ['teams'])

    def test_api_can_post_team(self):
        """Test API can add a team. (POST request)"""
        team = {'name': 'team2', 'country': 'russia'}
        result = self.client().post('/games/1/teams', data=json.dumps(team), headers=self.headers_to_post)
        self.assertEqual(result.status_code, 201)
        team_id = ast.literal_eval(result.data)['id']

        result = self.client().get('/games/1/teams/'+str(team_id))
        self.assertEqual(result.status_code, 200)
        data = ast.literal_eval(result.data)
        self.assertEqual(data['id'], team_id)
        self.assertEqual(data['name'], team['name'])
        self.assertEqual(data['country'], team['country'])

        rv = self.client().post('/games/1/teams', data=json.dumps(team), headers=self.headers_to_post)
        self.assertEqual(rv.status_code, 400)

        result = self.client().get('/games/1/teams/'+str(team_id+1))
        self.assertEqual(result.status_code, 204)

    def test_api_can_post_and_get_player(self):
        """Test API can post player by team. (GET request)"""
        team = {'name': 'team3', 'country': 'russia'}
        result = self.client().post('/games/1/teams', data=json.dumps(team), headers=self.headers_to_post)
        self.assertEqual(result.status_code, 201)
        team_id = ast.literal_eval(result.data)['id']

        player = {'name': 'Test Player', 'nickname': 'test_player1',
                  'country': 'China', 'is_cap': 0, 'team_id': team_id}
        result = self.client().post('/games/1/teams/'+str(team_id)+'/players', data=json.dumps(player),
                                    headers=self.headers_to_post)
        self.assertEqual(result.status_code, 201)
        data = ast.literal_eval(result.data)
        player_id = ast.literal_eval(result.data)['id']
        self.assertEqual(data['name'], player['name'])
        self.assertEqual(data['nickname'], player['nickname'])
        self.assertEqual(data['is_cap'], player['is_cap'])
        self.assertEqual(data['team_id'], player['team_id'])
        self.assertEqual(data['country'], player['country'])
        self.assertEqual(data['id'], player_id)

        rv = self.client().post('/games/1/teams/'+str(team_id)+'/players', data=json.dumps(player),
                                headers=self.headers_to_post)
        self.assertEqual(rv.status_code, 400)

        result = self.client().get('/games/1/teams/'+str(team_id+1))
        self.assertEqual(result.status_code, 204)

    def test_api_can_get_players(self):
        team = {'name': 'team10', 'country': 'russia'}
        result = self.client().post('/games/1/teams', data=json.dumps(team), headers=self.headers_to_post)
        self.assertEqual(result.status_code, 201)

        team_id = ast.literal_eval(result.data)['id']
        result = self.client().get('/games/1/teams/'+str(team_id)+'/players')
        self.assertEqual(result.status_code, 200)
        self.assertEqual(list(ast.literal_eval(result.data).keys()), ['players'])

    def test_api_can_get_player(self):
        """Test API can get a player by team. (GET request)"""
        team = {'name': 'team4', 'country': 'russia'}
        result = self.client().post('/games/1/teams', data=json.dumps(team), headers=self.headers_to_post)
        self.assertEqual(result.status_code, 201)
        team_id = ast.literal_eval(result.data)['id']

        player = {'name': 'Test Player', 'nickname': 'test_player2',
                  'country': 'China', 'is_cap': 0, 'team_id': team_id}
        result = self.client().post('/games/1/teams/'+str(team_id)+'/players', data=json.dumps(player),
                                    headers=self.headers_to_post)
        self.assertEqual(result.status_code, 201)
        player_id = ast.literal_eval(result.data)['id']

        result = self.client().get('/games/1/teams/'+str(team_id)+'/players/'+str(player_id))
        self.assertEqual(result.status_code, 200)
        data = ast.literal_eval(result.data)
        self.assertEqual(data['name'], player['name'])
        self.assertEqual(data['nickname'], player['nickname'])
        self.assertEqual(data['country'], player['country'])
        self.assertEqual(data['team_id'], player['team_id'])
        self.assertEqual(data['is_cap'], player['is_cap'])

    def test_api_can_post_and_get_tournament(self):
        """Test API can get all tournaments and one by id. (GET request)"""
        tournament = {'name': 'test tournament', 'start_date': str(datetime.date(2018, 2, 11)),
                      'end_date': str(datetime.date(2018, 2, 12))}
        result = self.client().post('/games/1/tournaments', data=json.dumps(tournament), headers=self.headers_to_post)
        self.assertEqual(result.status_code, 201)
        tournament_id = ast.literal_eval(result.data)['id']

        result = self.client().get('/games/1/tournaments/'+str(tournament_id))
        self.assertEqual(result.status_code, 200)
        data = ast.literal_eval(result.data)
        self.assertEqual(data['name'], tournament['name'])
        self.assertEqual(data['start_date'], str(tournament['start_date']))
        self.assertEqual(data['end_date'], str(tournament['end_date']))

    def test_api_can_get_tournaments(self):
        result = self.client().get('/games/1/tournaments')
        self.assertEqual(result.status_code, 200)
        self.assertEqual(list(ast.literal_eval(result.data).keys()), ['tournaments'])

    def test_matches(self):
        first_team = {'name': 'team5', 'country': 'russia'}
        result = self.client().post('/games/1/teams', data=json.dumps(first_team), headers=self.headers_to_post)
        self.assertEqual(result.status_code, 201)
        first_team_id = ast.literal_eval(result.data)['id']
        second_team = {'name': 'team6', 'country': 'russia'}
        result = self.client().post('/games/1/teams', data=json.dumps(second_team), headers=self.headers_to_post)
        self.assertEqual(result.status_code, 201)
        second_team_id = ast.literal_eval(result.data)['id']
        tournament = {'name': 'test tournament first', 'start_date': str(datetime.date(2018, 2, 11)),
                      'end_date': str(datetime.date(2018, 2, 12))}
        result = self.client().post('/games/1/tournaments', data=json.dumps(tournament), headers=self.headers_to_post)
        self.assertEqual(result.status_code, 201)
        tournament_id = ast.literal_eval(result.data)['id']
        match = {'num_in_stage': 1, 'date': str(datetime.datetime(2018, 2, 11, 11)), 'tournament_id': tournament_id,
                 'first_team_id': first_team_id, 'second_team_id': second_team_id}

        result = self.client().post('/games/1/matches', data=json.dumps(match), headers=self.headers_to_post)
        self.assertEqual(result.status_code, 201)
        self.match_id = ast.literal_eval(result.data)['id']

        result = self.client().get('/games/1/matches')
        self.assertEqual(result.status_code, 200)
        self.assertEqual(list(ast.literal_eval(result.data).keys()), ['matches'])

        result = self.client().get('/games/1/matches/' + str(self.match_id))
        self.assertEqual(result.status_code, 200)
        data = ast.literal_eval(result.data)
        self.assertEqual(data['id'], self.match_id)
        self.assertEqual(data['tournament_id'], match['tournament_id'])
        self.assertEqual(data['first_team_id'], match['first_team_id'])
        self.assertEqual(data['second_team_id'], match['second_team_id'])
        self.assertEqual(data['num_in_stage'], match['num_in_stage'])
        self.assertEqual(data['date'], str(match['date']))

        result = self.client().get('/games/1/tournaments/'+str(tournament_id)+'/matches')
        self.assertEqual(result.status_code, 200)

    def test_players_transactions(self):
        first_team = {'name': 'team7', 'country': 'russia'}
        result = self.client().post('/games/1/teams', data=json.dumps(first_team), headers=self.headers_to_post)
        self.assertEqual(result.status_code, 201)
        from_team_id = ast.literal_eval(result.data)['id']

        second_team = {'name': 'team8', 'country': 'russia'}
        result = self.client().post('/games/1/teams', data=json.dumps(second_team), headers=self.headers_to_post)
        self.assertEqual(result.status_code, 201)
        to_team_id = ast.literal_eval(result.data)['id']

        player = {'name': 'Test Player', 'nickname': 'test_player3',
                  'country': 'China', 'is_cap': 0}
        result = self.client().post('/games/1/teams/'+str(from_team_id)+'/players',
                                    data=json.dumps(player), headers=self.headers_to_post)
        self.assertEqual(result.status_code, 201)
        player_id = ast.literal_eval(result.data)['id']

        transaction = {'date': str(datetime.date(2018, 2, 12)), 'player_id': player_id,
                       'from_team_id': from_team_id, 'to_team_id': to_team_id}

        result = self.client().post('games/1/transactions', data=json.dumps(transaction), headers=self.headers_to_post)
        self.assertEqual(result.status_code, 201)
        transaction_id = ast.literal_eval(result.data)['id']

        # check player's team changed
        result = self.client().get('/games/1/teams/'+str(to_team_id)+'/players/'+str(player_id))
        self.assertEqual(result.status_code, 200)

        result = self.client().get('games/1/transactions/'+str(transaction_id))
        self.assertEqual(result.status_code, 200)
        data = ast.literal_eval(result.data)
        self.assertEqual(data['player_id'], transaction['player_id'])
        self.assertEqual(data['from_team_id'], transaction['from_team_id'])
        self.assertEqual(data['to_team_id'], transaction['to_team_id'])
        self.assertEqual(data['date'], transaction['date'])

    def test_api_can_get_transactions(self):
        result = self.client().get('games/1/transactions')
        self.assertEqual(result.status_code, 200)

    def test_team_in_tournament(self):
        tournament = {'name': 'test tournament second', 'start_date': str(datetime.date(2018, 2, 11)),
                      'end_date': str(datetime.date(2018, 2, 12))}
        result = self.client().post('/games/1/tournaments', data=json.dumps(tournament), headers=self.headers_to_post)
        self.assertEqual(result.status_code, 201)
        tournament_id = ast.literal_eval(result.data)['id']

        team = {'name': 'team9', 'country': 'russia'}
        result = self.client().post('/games/1/teams', data=json.dumps(team), headers=self.headers_to_post)
        self.assertEqual(result.status_code, 201)
        team_id = ast.literal_eval(result.data)['id']

        result = self.client().post('/games/1/tournaments/'+str(tournament_id)+'/teams',
                                    data=json.dumps({'team_id': team_id}))
        self.assertEqual(result.status_code, 201)

        result = self.client().get('/games/1/tournaments/'+str(tournament_id)+'/teams')
        self.assertEqual(result.status_code, 200)
        data = ast.literal_eval(result.data)
        self.assertIn(data['team_id'], team_id)

        result = self.client().get('/games/1/teams/'+str(team_id)+'/tournaments')
        self.assertEqual(result.status_code, 200)
        data = ast.literal_eval(result.data)
        self.assertIn(data['tournaments_id'], tournament_id)


    def tearDown(self):
        """teardown all initialized variables."""

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()