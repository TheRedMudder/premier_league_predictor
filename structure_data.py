"structure soccer data"

import pandas as pd

from football_api import filter_games, get_all_games, get_game_ids, parse_scores

# options for generating team report
USE_API = False
SELECTED_TEAM = "Liverpool"
YEARS = [2021, 2022, 2023]


def generate_game_summary(team_games, ids, team_name):
    """generates game summary

    Parameters
    ----------
    team_games
        all team games
    ids
        game ids
    team_name
        team name

    Returns
    -------
        dataframe: home team, scores, result (win/loss/draw), opponent team
    """
    game_summary = {}
    # loop through games
    for game_id in ids:
        game = filter_games(team_games, game_id=game_id)[0]
        # home team, scores, result (win/loss/draw)
        is_home = game["teams"]["home"]["name"] == team_name
        scored = game["goals"]["home" if is_home else "away"]
        conceded = game["goals"]["away" if is_home else "home"]
        winner = parse_scores(scored=scored, conceded=conceded)
        # opponent team name
        opponent = game["teams"]["away" if is_home else "home"]["name"]
        # game results
        game_summary[str(game_id)] = {
            "is_home": is_home,
            "scored": scored,
            "conceded": conceded,
            "result": winner,
            "opponent_name": opponent,
        }
    return game_summary


def generate_five_game_summary(game_results, ids, index):
    """generates prior five game summary

    Parameters
    ----------
    game_results
        game results, dataframe: home team, scores, result (win/loss/draw), opponent team
    ids
        game ids
    index
        game index

    Returns
    -------
        score, loss, outcome
    """
    # Total Score.
    score = 0
    # Total Loss
    loss = 0
    # Win/Loss/Draw
    outcome = []
    # Get prior 5 games
    for j in range(1, 6):
        game_prior = game_results[str(ids[index - j])]
        score += game_prior["scored"]
        loss += game_prior["conceded"]
        outcome.append(game_prior["result"][0])
    outcome = "".join(outcome)
    return score, loss, outcome


def generate_team_report(season_games, team_name):
    """generate team report

    Parameters
    ----------
    season_games
        all games in season
    team_name
        team name

    Returns
    -------
        dataframe

    """
    # filter team games
    team_games = filter_games(games=season_games, team_name=team_name)
    # get game ids in ascending order of timestamp
    game_ids = get_game_ids(team_games)
    # generates game summaries:  home team, scores, game results, opponent name
    game_results = generate_game_summary(
        team_games=team_games, ids=game_ids, team_name=team_name
    )
    # loop through games. start at 5.
    for i in range(5, len(game_ids)):
        this_game_id = game_ids[i]
        game = game_results[str(this_game_id)]
        # get prior 5 games: Total Score, Total Loss, Win/Loss/Draw
        game["total_score"], game["total_conceded"], game["momentum"] = (
            generate_five_game_summary(game_results=game_results, ids=game_ids, index=i)
        )

        # opponent
        # get opponent games in ascending order
        opponent_name = game["opponent_name"]
        opponent_games = filter_games(games=season_games, team_name=opponent_name)
        # get which index this game is for opponent
        opponent_game_ids = get_game_ids(opponent_games)
        opponent_game_index = opponent_game_ids.index(this_game_id)

        # check if index for opponent is greater than 4 (6th game or higher)
        if opponent_game_index > 4:
            # generates opponent game summaries:  home team, scores, game results
            opponent_game_results = generate_game_summary(
                team_games=opponent_games,
                ids=opponent_game_ids,
                team_name=opponent_name,
            )
            # get opponent prior 5 games summary
            (
                game["total_opponent_score"],
                game["total_opponent_conceded"],
                game["momentum_opponent"],
            ) = generate_five_game_summary(
                game_results=opponent_game_results,
                ids=opponent_game_ids,
                index=opponent_game_index,
            )
    # create df
    return pd.DataFrame(
        list(game_results.values())[5:], index=list(game_results.keys())[5:]
    )


if __name__ == "__main__":
    # loop through all seasons
    seasons = []
    for year in YEARS:
        # get all Premier League games (from API or disk)
        games = get_all_games(year=year, use_api=USE_API)
        # generate team report
        seasons.append(
            generate_team_report(season_games=games, team_name=SELECTED_TEAM)
        )
    # merge all seasons
    merged_df = pd.concat(seasons)
    print(merged_df)
