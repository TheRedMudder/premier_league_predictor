"get all fixtures"

import time

from football_api import get_fixture_statistics


def get_all_fixtures(fixture_list, sleep_time=7):
    """get all fixtures

    Parameters
    ----------
    fixture_list
        fixture id list
    sleep_time, optional
        sleep time between api request, by default 7
    """
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
