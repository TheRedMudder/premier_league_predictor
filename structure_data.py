"structure Liverpool data"

import pickle

import pandas as pd

from football_api import filter_games, get_all_games, get_game_ids, parse_scores

# Options for generating team report
USE_API = False
SELECTED_TEAM = "Liverpool"


def generate_game_summary(team_games, ids, team_name):
    """Generates game summary"""
    # Loop through games
    game_summary = {}
    for g_id in ids:
        game = filter_games(team_games, game_id=g_id)[0]
        # Home Team, Scores, winner
        is_home = game["teams"]["home"]["name"] == team_name
        scored = game["goals"]["home" if is_home else "away"]
        conceded = game["goals"]["away" if is_home else "home"]
        winner = parse_scores(scored=scored, conceded=conceded)
        # Opponent Team Name
        opponent = game["teams"]["away" if is_home else "home"]["name"]
        # Game Results
        game_summary[str(g_id)] = {
            "is_home": is_home,
            "scored": scored,
            "conceded": conceded,
            "result": winner,
            "opponent_name": opponent,
        }
    return game_summary


def generate_prior_game_summary(game_results, game_index, game_ids):
    """get prior five game summary"""
    # Total Score.
    score = 0
    # Total Loss
    loss = 0
    # Win/Loss/Draw
    outcome = []
    # Get prior 5 games
    for j in range(1, 6):
        game_prior = game_results[str(game_ids[game_index - j])]
        score += game_prior["scored"]
        loss += game_prior["conceded"]
        outcome.append(game_prior["result"][0])
    outcome = "".join(outcome)
    return score, loss, outcome


def generate_team_report(season_games):
    """Generate Team Report

    Parameters
    ----------
    season_games
        All games in season

    Returns
    -------
        Dataframe
    """
    # filter team games
    team_games = filter_games(games=season_games, team_name=SELECTED_TEAM)
    # get game id in descending order
    game_ids = get_game_ids(team_games)
    # Generates game summaries:  Home Team, Scores, Game results, Opponent name
    game_results = generate_game_summary(
        team_games=team_games, ids=game_ids, team_name=SELECTED_TEAM
    )
    # Loop through games. Start at 5.
    for i in range(5, len(game_ids)):
        current_game_id = game_ids[i]
        game = game_results[str(current_game_id)]
        # Get Prior 5 games: Total Score, Total Loss, Win/Loss/Draw
        game["total_score"], game["total_conceded"], game["momentum"] = (
            generate_prior_game_summary(
                game_results=game_results, game_index=i, game_ids=game_ids
            )
        )

        # Loop through opponent games

        # Get Opponent Games in Descending Order
        opponent_name = game["opponent_name"]
        opponent_games = filter_games(games=season_games, team_name=opponent_name)
        # Get Which Index This Game is For Opponent
        opponent_game_ids = get_game_ids(opponent_games)
        opponent_game_index = opponent_game_ids.index(current_game_id)

        # Check if index for opponent is greater than 4 (6th games or higher)
        if opponent_game_index > 4:
            # Generates opponent game summaries:  Home Team, Scores, Game results, Opponent name
            opponent_game_results = generate_game_summary(
                team_games=opponent_games,
                ids=opponent_game_ids,
                team_name=opponent_name,
            )
            # Get Opponent Previous 5 Games Total Win
            total_opponent_score, total_opponent_loss, momentum_opponent = (
                generate_prior_game_summary(
                    game_results=opponent_game_results,
                    game_index=opponent_game_index,
                    game_ids=opponent_game_ids,
                )
            )
            game["total_opponent_score"] = total_opponent_score
            game["total_opponent_conceded"] = total_opponent_loss
            game["momentum_opponent"] = momentum_opponent
    # Create DataFrame
    return pd.DataFrame(
        list(game_results.values())[5:], index=list(game_results.keys())[5:]
    )


if __name__ == "__main__":
    # # get all Premier League games (from API or disk)
    if USE_API:
        games = get_all_games()
        # cache all games
        with open("all_games.pickle", "wb") as handle:
            pickle.dump(games, handle, protocol=pickle.HIGHEST_PROTOCOL)
        # validate cache
        with open("all_games.pickle", "rb") as handle:
            cache_games = pickle.load(handle)
        assert games == cache_games, "Cache failed"
    else:
        # Read cached responses
        with open("all_games.pickle", "rb") as handle:
            games = pickle.load(handle)
    team_report_df = generate_team_report(season_games=games)
    print(team_report_df)
