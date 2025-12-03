from datetime import datetime
from ncaa import get_casablanca_service


def print_game_info(game_wrapper):
    game = game_wrapper.game
    print(f"\n{game.away.names.short} @ {game.home.names.short}")
    print(f"  Score: {game.away.score} - {game.home.score}")
    print(f"  State: {game.gameState.value}")
    if game.network:
        print(f"  Network: {game.network}")
    if game.venue:
        print(f"  Venue: {game.venue}")
    if game.location:
        print(f"  Location: {game.location}")


def demo_mens_basketball_scoreboard():
    print("=" * 60)
    print("Demo: Men's Basketball Scoreboard")
    print("=" * 60)

    service = get_casablanca_service()

    today = datetime.now().strftime("%Y/%m/%d")
    print(f"\nFetching men's basketball games for {today}...")

    try:
        scoreboard = service.get_mens_basketball_scoreboard(today)
        print(f"Found {len(scoreboard.games)} games")

        for game_wrapper in scoreboard.games[:5]:
            print_game_info(game_wrapper)
    except Exception as e:
        print(f"Error: {e}")


def demo_womens_basketball_scoreboard():
    print("\n" + "=" * 60)
    print("Demo: Women's Basketball Scoreboard")
    print("=" * 60)

    service = get_casablanca_service()

    today = datetime.now().strftime("%Y/%m/%d")
    print(f"\nFetching women's basketball games for {today}...")

    try:
        scoreboard = service.get_womens_basketball_scoreboard(today)
        print(f"Found {len(scoreboard.games)} games")

        for game_wrapper in scoreboard.games[:5]:
            print_game_info(game_wrapper)
    except Exception as e:
        print(f"Error: {e}")


def demo_basketball_schedule():
    print("\n" + "=" * 60)
    print("Demo: Men's Basketball Schedule")
    print("=" * 60)

    service = get_casablanca_service()

    today = datetime.now().strftime("%Y/%m/%d")
    print(f"\nFetching men's basketball schedule for {today}...")

    try:
        schedule = service.get_basketball_schedule("men", today)
        print(f"Found {len(schedule.games)} games")

        if schedule.updated_at:
            print(f"Schedule last updated: {schedule.updated_at}")

        for game_wrapper in schedule.games[:5]:
            print_game_info(game_wrapper)
    except Exception as e:
        print(f"Error: {e}")


def demo_live_games():
    print("\n" + "=" * 60)
    print("Demo: Live Men's Basketball Games")
    print("=" * 60)

    service = get_casablanca_service()

    print("\nFetching live games...")

    try:
        live_games = service.get_live_games("men")
        print(f"Found {len(live_games)} live games")

        if live_games:
            for game_wrapper in live_games:
                print_game_info(game_wrapper)
        else:
            print("\nNo live games at the moment")
    except Exception as e:
        print(f"Error: {e}")


def demo_upcoming_games():
    print("\n" + "=" * 60)
    print("Demo: Upcoming Men's Basketball Games (Next 3 Days)")
    print("=" * 60)

    service = get_casablanca_service()

    print("\nFetching upcoming games...")

    try:
        upcoming_games = service.get_upcoming_games("basketball-men", days=3)
        print(f"Found {len(upcoming_games)} upcoming games in the next 3 days")

        for game_wrapper in upcoming_games[:10]:
            print_game_info(game_wrapper)
    except Exception as e:
        print(f"Error: {e}")


def demo_football_schedule():
    print("\n" + "=" * 60)
    print("Demo: Football Schedule")
    print("=" * 60)

    service = get_casablanca_service()

    today = datetime.now().strftime("%Y/%m/%d")
    print(f"\nFetching football schedule for {today}...")

    try:
        schedule = service.get_football_schedule(today)
        print(f"Found {len(schedule.games)} games")

        for game_wrapper in schedule.games[:5]:
            game = game_wrapper.game
            print(f"\n{game.away.names.short} @ {game.home.names.short}")
            if game.venue:
                print(f"  Venue: {game.venue}")
            if game.weather:
                print(f"  Weather: {game.weather.condition}, {game.weather.temperature}")
    except Exception as e:
        print(f"Error: {e}")


def main():
    print("\n" + "=" * 60)
    print("NCAA Casablanca API Demo")
    print("=" * 60)

    demo_mens_basketball_scoreboard()
    demo_womens_basketball_scoreboard()
    demo_basketball_schedule()
    demo_live_games()
    demo_upcoming_games()


if __name__ == "__main__":
    main()
