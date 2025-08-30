"prediction pipelines"

import pandas as pd
import seaborn as sns
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier

# Models
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import KFold, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.svm import SVC

import structure_data


def decode_five_game_momentum(five_game_momentum):
    """decode five game momentum

    Parameters
    ----------
    five_game_momentum
        _description_

    Returns
    -------
        _description_
    """
    res_map = {"W": 1, "D": 0, "L": -1}
    return [res_map[game] for game in five_game_momentum]


def split_momemtum(d, cat):
    """split momentum

    Parameters
    ----------
    d
        dataframe
    cat
        category

    Returns
    -------
        series split momentum
    """
    five_game_split = d[cat].apply(decode_five_game_momentum).tolist()
    five_games = pd.DataFrame(
        five_game_split,
        columns=[f"{cat}_prior_game_{i+1}" for i in range(5)],
        index=d.index,
    )
    return pd.concat([d, five_games], axis=1)


if __name__ == "__main__":
    # get all games for selected team
    # USE_API = False
    # SELECTED_TEAM = "Chelsea"

    # SELECTED_TEAM = "Manchester United"

    # SELECTED_TEAM = "Wolves"

    # SELECTED_TEAM = "Tottenham"

    # SELECTED_TEAM = "Sunderland"

    # SELECTED_TEAM = "Leeds"

    # SELECTED_TEAM = "Brighton"

    # SELECTED_TEAM = "Nottingham Forest"

    # SELECTED_TEAM = "Liverpool"
# 
    SELECTED_TEAM = "Aston Villa"
    
    YEARS = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    # team_games = structure_data.generate_historic_team_report(
    #     team_name=SELECTED_TEAM, years=YEARS, use_api=USE_API
    # )


    seasons = []
    for year in YEARS:
        # get all Premier League games (from API or disk)
        games = structure_data.get_all_games(year=year, use_api=False)
        # generate team report
        seasons.append(
            structure_data.generate_team_report(season_games=games, team_name=SELECTED_TEAM)
        )
    # merge all seasons
    df = pd.concat(seasons)

    # Don't allow drops more than 5
    initial_rows = df.shape[0]
    df=df.dropna()
    assert (initial_rows-df.shape[0])<5, "Dropping 5 or more rows"

    # decode prior game performance

    # select features for ML Pipelines

    # pick ML pipelines

    # train/validate models

    # display results

    # drop unknown (`scored`, `conceded`),Opponent (`opponent_name`), Predictions (`result`)
    # transform Decode (`momentum`,`momentum_opponent`)

    # Decode
    # momentum_df = split_momemtum(d=df, cat="momentum")
    # pre_df = split_momemtum(d=momentum_df, cat="momentum_opponent")

    # Drop
    # Split data

    # X
    # print(df.shape)
    # df.dropna(axis=1)
    # print(df.shape)

    X = df.drop(
        [
            "scored",
            "conceded",
            "opponent_name",
            "result",
            "momentum",
            "momentum_opponent",
            "is_home",
        ],
        axis=1,
    )
    # Y
    res = df["result"]
    le = LabelEncoder()
    y = le.fit_transform(res)

    # Display X,Y, Correlation Matrix
    sns.heatmap(X.corr())

    # Prediction

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.33, random_state=42
    )

    # Scaling/No Scaling Pipeline
    col_name = X.columns.tolist()
    scale_prior = ColumnTransformer(transformers=[("num", StandardScaler(), col_name)])
    pass_only = ColumnTransformer(transformers=[("num", "passthrough", col_name)])

    # Pipelines
    pipelines = {}
    # random forest
    pipelines["random_forest"] = Pipeline(
        steps=[("prep", scale_prior), ("m", RandomForestClassifier())]
    )
    # logistic regression
    pipelines["logistic_regression"] = Pipeline(
        steps=[("prep", scale_prior), ("m", LogisticRegression())]
    )
    # support vector
    pipelines["support_vector"] = Pipeline(steps=[("prep", scale_prior), ("m", SVC())])
    # k-nearest-neighbors
    pipelines["k_nearest_neighbors"] = Pipeline(
        steps=[("prep", scale_prior), ("m", KNeighborsClassifier())]
    )
    # gradient boosting
    pipelines["gradient_boosting"] = Pipeline(
        steps=[("prep", pass_only), ("m", GradientBoostingClassifier())]
    )
    best_predictor = (None,None)
    scores = []
    kFold = KFold(n_splits=10, shuffle=False)
    avg_k_fold = {}
    for name, pipe in pipelines.items():
        avg_k_fold[name] = []
    for i, (train_index, test_index) in enumerate(kFold.split(X)):
        X_train, X_test, y_train, y_test = (
            X.iloc[train_index],
            X.iloc[test_index],
            y[train_index],
            y[test_index],
        )
        # Compare
        results = []
        fitted = {}
        for name, pipe in pipelines.items():
            pipe.fit(X_train, y_train)
            fitted[name] = pipe
            y_pred = pipe.predict(X_test)
            acc = accuracy_score(y_test, y_pred)

            results.append((name, acc))

            avg_k_fold[name].append(acc)

        # Sort by accuracy
        results_sorted = sorted(results, key=lambda x: x[1], reverse=True)
        print(f"K-Value:{i}")
        for name, acc in results_sorted:
            print(f"{name:22s}  accuracy={acc:.4f}")
        print("\n\n")

    # For each value in dict calculate average
    print(pd.DataFrame(avg_k_fold).mean().sort_values())
    best_predictor = (pd.DataFrame(avg_k_fold).mean().sort_values().index[-1], pd.DataFrame(avg_k_fold).mean().sort_values()[-1])
    # print(X) 
    # predict_future=(pd.DataFrame([{"total_score":14,"total_conceded":2,"total_opponent_score":9,"total_opponent_conceded":4}])) # Chelsea L
    # predict_future=(pd.DataFrame([{"total_score":6,"total_conceded":7,"total_opponent_score":4,"total_opponent_conceded":6}])) # Manchester United

    # predict_future=(pd.DataFrame([{"total_score":4,"total_conceded":10,"total_opponent_score":6,"total_opponent_conceded":4}])) # Wolves

    # predict_future=(pd.DataFrame([{"total_score":8,"total_conceded":7,"total_opponent_score":4,"total_opponent_conceded":7}])) # Tottenham

    # predict_future=(pd.DataFrame([{"total_score":5,"total_conceded":6,"total_opponent_score":7,"total_opponent_conceded":5}])) # Sunderland

    # predict_future=(pd.DataFrame([{"total_score":4,"total_conceded":8,"total_opponent_score":5,"total_opponent_conceded":8}])) # Leeds

    # predict_future=(pd.DataFrame([{"total_score":13,"total_conceded":2,"total_opponent_score":15,"total_opponent_conceded":8}])) # Brighton

    # predict_future=(pd.DataFrame([{"total_score":4,"total_conceded":3,"total_opponent_score":6,"total_opponent_conceded":12}])) # Nottingham Fores

    # predict_future=(pd.DataFrame([{"total_score":14,"total_conceded":12,"total_opponent_score":11,"total_opponent_conceded":3}])) # Liverpool

    predict_future=(pd.DataFrame([{"total_score":7,"total_conceded":4,"total_opponent_score":6,"total_opponent_conceded":5}])) # Aston Villa

    print("\n\n\n\n\n\n")
    # print(results)
    for name, pipe in pipelines.items():
        
        if name == best_predictor[0]:
            print(f"Using {best_predictor[0]} for {SELECTED_TEAM} with confidence: {best_predictor[1]}")
            print(pipe.predict(predict_future))
            print(le.inverse_transform(pipe.predict(predict_future)))