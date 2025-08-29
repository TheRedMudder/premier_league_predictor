"get all fixtures"

import itertools
import time

import structure_data
from football_api import get_fixture_statistics


def get_all_fixtures(fixture_list, sleep_time=7, expected_request=None):
    """get all fixtures

    Parameters
    ----------
    fixture_list
        fixture id list
    sleep_time, optional
        sleep time between api request, by default 7
    expected_request, optional
        expected api request for progress
    """
    api_queries = 0
    use_api = False
    # loop through fixtures
    for fixture_id in fixture_list:
        # verify if fixture exist and is valid
        try:
            c = len(get_fixture_statistics(fixture_id=fixture_id, use_api=use_api))
        except FileNotFoundError:
            c = 0
        # get fixture if invalid or doesn't exist
        if c == 0:
            use_api = True
            get_fixture_statistics(fixture_id=fixture_id, use_api=use_api)
            use_api = False
            api_queries += 1
            if expected_request is not None:
                print(f"Percentage:{100*api_queries/expected_request}%")
            time.sleep(sleep_time)


def check_all_fixtures(fixture_list):
    """check if fixtures exist and are valid

    Parameters
    ----------
    fixture_list
        fixture list

    Returns
    -------
        invalid_list, not_found_list
    """
    invalid_list = []
    not_found_list = []
    for fixture_id in fixture_list:
        # try if fixture exist
        try:
            # check if fixture invalid
            if len(get_fixture_statistics(fixture_id=fixture_id, use_api=False)) == 0:
                invalid_list.append(fixture_id)

        except FileNotFoundError:
            not_found_list.append(fixture_id)
    return invalid_list, not_found_list


if __name__ == "__main__":
    teams = [
        "Chelsea",
        "Manchester United",
        "Wolves",
        "Tottenham",
        "Sunderland",
        "Leeds",
        "Brighton",
        "Nottingham Forest",
        "Liverpool",
        "Aston Villa",
        "Fulham",
        "Burnley",
        "Everton",
        "Bournemouth",
        "Brentford",
        "Newcastle",
        "Manchester City",
        "West Ham",
        "Arsenal",
        "Crystal Palace",
    ]
    missing_years = {team: [] for team in teams}
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    for year, team in itertools.product(years, teams):
        # get all Premier League games (from API or disk)
        season_games = structure_data.get_all_games(year=year, use_api=False)
        # filter team games
        team_games = structure_data.filter_games(games=season_games, team_name=team)
        # get game ids in ascending order of timestamp
        game_ids = structure_data.get_game_ids(team_games)
        if len(game_ids) == 0:
            missing_years[team].append(year)
        # check existing cache
        invalid, not_found = check_all_fixtures(game_ids)
        if len(invalid) != 0 or len(not_found) != 0:
            print(
                f"{year=}, {team=}, invalid={len(invalid)}, not_found={len(not_found)}"
            )
        # get all fixtures
        get_all_fixtures(
            game_ids, sleep_time=0.003, expected_request=len(invalid) + len(not_found)
        )
    # Teams with most data to least
    print(sorted(teams, key=lambda x: len(missing_years[x])))
