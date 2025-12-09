"""
NCAA Casablanca API ETL DAG

Multi-stage pipeline for ingesting live scores, schedules, and game data from the NCAA Casablanca API.

Stages:
1. Extract schedules for multiple sports (basketball, football, soccer)
2. Extract scoreboard data for active games
3. Transform and enrich game data
4. Load to PostgreSQL with proper relationships
5. Validate data quality and completeness
"""

from datetime import datetime, timedelta
from pathlib import Path
import json

from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.trigger_rule import TriggerRule

from ncaa.api import get_casablanca_service
from ncaa.api.models import GameState


def extract_schedules(**context):
    """Extract schedule data for multiple sports and date ranges."""
    service = get_casablanca_service()
    execution_date = context["ds"]

    sports_config = [
        {"sport": "basketball-men", "gender": "men", "days": 7},
        {"sport": "basketball-women", "gender": "women", "days": 7},
        {"sport": "football", "gender": None, "days": 7},
    ]

    all_schedules = []

    for config in sports_config:
        try:
            schedules = service.schedule.get_upcoming_schedules(
                sport=config["sport"], division="d1", days=config["days"]
            )

            for schedule in schedules:
                for game_wrapper in schedule.games:
                    game = game_wrapper.game
                    game_data = {
                        "game_id": game.gameID if hasattr(game, "gameID") else None,
                        "sport": config["sport"],
                        "gender": config["gender"],
                        "home_team": game.home.names.full,
                        "away_team": game.away.names.full,
                        "home_score": game.home.score
                        if hasattr(game.home, "score")
                        else None,
                        "away_score": game.away.score
                        if hasattr(game.away, "score")
                        else None,
                        "game_state": game.gameState,
                        "start_time_epoch": game.startTimeEpoch,
                        "venue": game.venue if hasattr(game, "venue") else None,
                        "location": game.location
                        if hasattr(game, "location")
                        else None,
                        "network": game.network if hasattr(game, "network") else None,
                        "home_rank": game.home.rank
                        if hasattr(game.home, "rank")
                        else None,
                        "away_rank": game.away.rank
                        if hasattr(game.away, "rank")
                        else None,
                        "home_conference": game.home.conferences[0].conferenceName
                        if game.home.conferences
                        else None,
                        "away_conference": game.away.conferences[0].conferenceName
                        if game.away.conferences
                        else None,
                    }
                    all_schedules.append(game_data)

        except Exception as e:
            print(f"Error extracting {config['sport']}: {e}")
            continue

    data_dir = Path("/opt/airflow/data")
    data_dir.mkdir(exist_ok=True)

    schedules_file = data_dir / f"schedules_{execution_date}.json"
    with open(schedules_file, "w") as f:
        json.dump(all_schedules, f, indent=2)

    context["task_instance"].xcom_push(key="schedules_file", value=str(schedules_file))
    context["task_instance"].xcom_push(key="schedules_count", value=len(all_schedules))

    return len(all_schedules)


def extract_live_scores(**context):
    """Extract live scoreboard data for in-progress games."""
    service = get_casablanca_service()
    execution_date = context["ds"]

    sports = [
        {"gender": "men", "division": "d1"},
        {"gender": "women", "division": "d1"},
    ]

    all_scores = []

    for sport_config in sports:
        try:
            live_games = service.basketball.get_live_games(
                gender=sport_config["gender"], division=sport_config["division"]
            )

            for game_wrapper in live_games:
                game = game_wrapper.game
                score_data = {
                    "game_id": f"basketball-{sport_config['gender']}-{game.startTimeEpoch}",
                    "sport": f"basketball-{sport_config['gender']}",
                    "home_team": game.home.names.full,
                    "away_team": game.away.names.full,
                    "home_score": game.home.score,
                    "away_score": game.away.score,
                    "game_state": game.gameState,
                    "current_period": game.currentPeriod,
                    "contest_clock": game.contestClock,
                    "start_time_epoch": game.startTimeEpoch,
                    "network": game.network,
                    "extracted_at": datetime.utcnow().isoformat(),
                }
                all_scores.append(score_data)

        except Exception as e:
            print(f"Error extracting live scores for {sport_config['gender']}: {e}")
            continue

    data_dir = Path("/opt/airflow/data")
    scores_file = data_dir / f"live_scores_{execution_date}.json"

    with open(scores_file, "w") as f:
        json.dump(all_scores, f, indent=2)

    context["task_instance"].xcom_push(key="scores_file", value=str(scores_file))
    context["task_instance"].xcom_push(key="scores_count", value=len(all_scores))

    return len(all_scores)


def check_live_games(**context):
    """Branch operator: check if there are live games to process."""
    scores_count = context["task_instance"].xcom_pull(
        task_ids="extract_live_scores", key="scores_count"
    )

    if scores_count and scores_count > 0:
        return "load_live_scores"
    else:
        return "skip_live_scores"


def transform_schedule_data(**context):
    """Transform and enrich schedule data."""
    schedules_file = context["task_instance"].xcom_pull(
        task_ids="extract_schedules", key="schedules_file"
    )

    with open(schedules_file, "r") as f:
        schedules = json.load(f)

    transformed = []
    for game in schedules:
        game["is_ranked_matchup"] = bool(
            game.get("home_rank") and game.get("away_rank")
        )
        game["is_conference_game"] = game.get("home_conference") == game.get(
            "away_conference"
        )

        if game["start_time_epoch"]:
            game["game_date"] = (
                datetime.fromtimestamp(game["start_time_epoch"]).date().isoformat()
            )
            game["game_time"] = (
                datetime.fromtimestamp(game["start_time_epoch"]).time().isoformat()
            )

        transformed.append(game)

    data_dir = Path("/opt/airflow/data")
    transformed_file = data_dir / f"transformed_schedules_{context['ds']}.json"

    with open(transformed_file, "w") as f:
        json.dump(transformed, f, indent=2)

    context["task_instance"].xcom_push(
        key="transformed_file", value=str(transformed_file)
    )

    return len(transformed)


def load_schedules(**context):
    """Load schedule data to PostgreSQL."""
    transformed_file = context["task_instance"].xcom_pull(
        task_ids="transform_schedule_data", key="transformed_file"
    )

    with open(transformed_file, "r") as f:
        schedules = json.load(f)

    hook = PostgresHook(postgres_conn_id="ncaa_db")

    insert_query = """
        INSERT INTO casablanca_games (
            game_id, sport, gender, home_team, away_team,
            home_score, away_score, game_state, start_time_epoch,
            venue, location, network, home_rank, away_rank,
            home_conference, away_conference, is_ranked_matchup,
            is_conference_game, game_date, game_time, extracted_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (game_id, extracted_at)
        DO UPDATE SET
            home_score = EXCLUDED.home_score,
            away_score = EXCLUDED.away_score,
            game_state = EXCLUDED.game_state,
            updated_at = CURRENT_TIMESTAMP;
    """

    conn = hook.get_conn()

    try:
        with conn.cursor() as cursor:
            for game in schedules:
                cursor.execute(
                    insert_query,
                    (
                        game.get("game_id"),
                        game.get("sport"),
                        game.get("gender"),
                        game.get("home_team"),
                        game.get("away_team"),
                        game.get("home_score"),
                        game.get("away_score"),
                        game.get("game_state"),
                        game.get("start_time_epoch"),
                        game.get("venue"),
                        game.get("location"),
                        game.get("network"),
                        game.get("home_rank"),
                        game.get("away_rank"),
                        game.get("home_conference"),
                        game.get("away_conference"),
                        game.get("is_ranked_matchup"),
                        game.get("is_conference_game"),
                        game.get("game_date"),
                        game.get("game_time"),
                        context["ds"],
                    ),
                )
            conn.commit()
    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Failed to load schedules: {e}") from e
    finally:
        conn.close()

    return len(schedules)


def load_live_scores(**context):
    """Load live score data to PostgreSQL."""
    scores_file = context["task_instance"].xcom_pull(
        task_ids="extract_live_scores", key="scores_file"
    )

    with open(scores_file, "r") as f:
        scores = json.load(f)

    hook = PostgresHook(postgres_conn_id="ncaa_db")

    insert_query = """
        INSERT INTO casablanca_live_scores (
            game_id, sport, home_team, away_team, home_score, away_score,
            game_state, current_period, contest_clock, start_time_epoch,
            network, extracted_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        );
    """

    conn = hook.get_conn()

    try:
        with conn.cursor() as cursor:
            for score in scores:
                cursor.execute(
                    insert_query,
                    (
                        score.get("game_id"),
                        score.get("sport"),
                        score.get("home_team"),
                        score.get("away_team"),
                        score.get("home_score"),
                        score.get("away_score"),
                        score.get("game_state"),
                        score.get("current_period"),
                        score.get("contest_clock"),
                        score.get("start_time_epoch"),
                        score.get("network"),
                        score.get("extracted_at"),
                    ),
                )
            conn.commit()
    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Failed to load live scores: {e}") from e
    finally:
        conn.close()

    return len(scores)


def skip_live_scores(**context):
    """Placeholder task when no live games."""
    print("No live games to process")
    return 0


def validate_data(**context):
    """Validate loaded data quality."""
    hook = PostgresHook(postgres_conn_id="ncaa_db")

    schedules_count = context["task_instance"].xcom_pull(
        task_ids="extract_schedules", key="schedules_count"
    )

    result = hook.get_first(
        "SELECT COUNT(*) FROM casablanca_games WHERE extracted_at = %s",
        parameters=(context["ds"],),
    )

    loaded_count = result[0] if result else 0

    if loaded_count != schedules_count:
        raise ValueError(
            f"Validation failed: expected {schedules_count} games, found {loaded_count}"
        )

    # Check for data quality issues
    quality_checks = {
        "missing_teams": "SELECT COUNT(*) FROM casablanca_games WHERE home_team IS NULL OR away_team IS NULL",
        "missing_times": "SELECT COUNT(*) FROM casablanca_games WHERE start_time_epoch IS NULL",
        "invalid_scores": "SELECT COUNT(*) FROM casablanca_games WHERE home_score < 0 OR away_score < 0",
    }

    issues = {}
    for check_name, query in quality_checks.items():
        result = hook.get_first(query)
        if result and result[0] > 0:
            issues[check_name] = result[0]

    if issues:
        print(f"Data quality warnings: {issues}")

    return loaded_count


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    "ncaa_casablanca_etl",
    default_args=default_args,
    description="Extract NCAA live scores and schedules from Casablanca API",
    schedule_interval="*/15 * * * *",  # Every 15 minutes
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["ncaa", "casablanca", "basketball", "live-scores"],
) as dag:
    create_tables = PostgresOperator(
        task_id="create_tables",
        postgres_conn_id="ncaa_db",
        sql="""
            -- Main games table
            CREATE TABLE IF NOT EXISTS casablanca_games (
                id SERIAL PRIMARY KEY,
                game_id VARCHAR(255) NOT NULL,
                sport VARCHAR(100) NOT NULL,
                gender VARCHAR(20),
                home_team VARCHAR(255) NOT NULL,
                away_team VARCHAR(255) NOT NULL,
                home_score INTEGER,
                away_score INTEGER,
                game_state VARCHAR(50),
                start_time_epoch BIGINT,
                venue VARCHAR(255),
                location VARCHAR(255),
                network VARCHAR(100),
                home_rank INTEGER,
                away_rank INTEGER,
                home_conference VARCHAR(100),
                away_conference VARCHAR(100),
                is_ranked_matchup BOOLEAN DEFAULT FALSE,
                is_conference_game BOOLEAN DEFAULT FALSE,
                game_date DATE,
                game_time TIME,
                extracted_at DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(game_id, extracted_at)
            );
            
            -- Live scores history table
            CREATE TABLE IF NOT EXISTS casablanca_live_scores (
                id SERIAL PRIMARY KEY,
                game_id VARCHAR(255) NOT NULL,
                sport VARCHAR(100) NOT NULL,
                home_team VARCHAR(255) NOT NULL,
                away_team VARCHAR(255) NOT NULL,
                home_score INTEGER NOT NULL,
                away_score INTEGER NOT NULL,
                game_state VARCHAR(50) NOT NULL,
                current_period INTEGER,
                contest_clock VARCHAR(20),
                start_time_epoch BIGINT,
                network VARCHAR(100),
                extracted_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Create indexes
            CREATE INDEX IF NOT EXISTS idx_games_sport ON casablanca_games(sport);
            CREATE INDEX IF NOT EXISTS idx_games_state ON casablanca_games(game_state);
            CREATE INDEX IF NOT EXISTS idx_games_date ON casablanca_games(game_date);
            CREATE INDEX IF NOT EXISTS idx_games_extracted ON casablanca_games(extracted_at);
            CREATE INDEX IF NOT EXISTS idx_games_ranked ON casablanca_games(is_ranked_matchup);
            CREATE INDEX IF NOT EXISTS idx_live_game_id ON casablanca_live_scores(game_id);
            CREATE INDEX IF NOT EXISTS idx_live_extracted ON casablanca_live_scores(extracted_at);
        """,
    )

    extract_schedules_task = PythonOperator(
        task_id="extract_schedules",
        python_callable=extract_schedules,
    )

    extract_live_scores_task = PythonOperator(
        task_id="extract_live_scores",
        python_callable=extract_live_scores,
    )

    check_live_games_task = BranchPythonOperator(
        task_id="check_live_games",
        python_callable=check_live_games,
    )

    transform_task = PythonOperator(
        task_id="transform_schedule_data",
        python_callable=transform_schedule_data,
    )

    load_schedules_task = PythonOperator(
        task_id="load_schedules",
        python_callable=load_schedules,
    )

    load_live_scores_task = PythonOperator(
        task_id="load_live_scores",
        python_callable=load_live_scores,
    )

    skip_live_scores_task = PythonOperator(
        task_id="skip_live_scores",
        python_callable=skip_live_scores,
    )

    validate_task = PythonOperator(
        task_id="validate_data",
        python_callable=validate_data,
        trigger_rule=TriggerRule.NONE_FAILED,
    )

    # Define task dependencies
    create_tables >> [extract_schedules_task, extract_live_scores_task]
    extract_schedules_task >> transform_task >> load_schedules_task
    extract_live_scores_task >> check_live_games_task
    check_live_games_task >> [load_live_scores_task, skip_live_scores_task]
    [load_schedules_task, load_live_scores_task, skip_live_scores_task] >> validate_task
