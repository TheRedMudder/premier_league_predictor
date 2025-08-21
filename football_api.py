"FootBall API"

import http.client
import json
import constants


def get_all_games(league_id=39, year=2023):
    """get all games

    Parameters
    ----------
    league_id, optional
        league id, by default 39 (Liverpool)
    year, optional
        year of first game in the season, by default 2023

    Returns
    -------
        all games
    """
    conn = http.client.HTTPSConnection("v3.football.api-sports.io")
    headers = constants.HEADERS
    conn.request("GET", f"/fixtures?league={league_id}&season={year}", headers=headers)
    data = conn.getresponse().read()
    return json.loads(data.decode("utf-8"))["response"]


def filter_games(games, team_name=None, game_id=None):
    """Filter games

    Parameters
    ----------
    team_games
        team games
    team_name, optional
        team name, by default None
    game_id, optional
        game id, by default None
    """
    filtered_games = []
    for game in games:
        insert_game = True
        if team_name is not None:
            insert_game = insert_game and (
                team_name
                in (game["teams"]["home"]["name"], game["teams"]["away"]["name"])
            )
        if game_id is not None:
            insert_game = insert_game and game["fixture"]["id"] == game_id
        if insert_game:
            filtered_games.append(game)
    return filtered_games


def get_game_ids(games):
    """get game ids

    Parameters
    ----------
    games
        games

    Returns
    -------
        list of game IDs in descending order
    """
    # Sort games by descending time
    games = sorted(games, key=lambda x: x["fixture"]["timestamp"])
    # Return list of IDs
    return [game["fixture"]["id"] for game in games]


def parse_scores(scored, conceded):
    """Parse scores

    Parameters
    ----------
    scored
        target team score
    conceded
        opponent team score

    Returns
    -------
        "Win", "Tie", "Lost"
    """
    if scored > conceded:
        return "Win"
    if scored == conceded:
        return "Draw"
    return "Lost"
