import json
import random
import schedule
import time
from datetime import datetime

try:
    import schedule
except ImportError:
    print("Installing required libraries from req.txt...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "req.txt"])
    print("Installation complete!")

# Load puzzles from JSON
with open("puzzles.json", "r") as f:
    puzzles = json.load(f)

# Configurable variables
starting_rating = 100
rating_step = 50
rating_range = 50

# Daily puzzle settings (will scale each day)
daily_min_rating = 100
daily_max_rating = 1000
daily_scale_step = 50  # how much to increase per day

current_rating = starting_rating
daily_puzzle_cache = None
last_day = None  # to track when a new day starts

# Tag filters
blacklist_tags = {"endgame"}     # exclude puzzles with these tags
required_tags = set()            # only allow puzzles with these tags (if not empty)


def filter_by_tags(puzzle):
    tags = set(puzzle.get("tags", []))
    if tags & blacklist_tags:
        return False
    if required_tags and not (tags & required_tags):
        return False
    return True


def get_puzzle_near_rating(target_rating, rating_range):
    filtered = [
        p for p in puzzles
        if target_rating - rating_range <= p["rating"] <= target_rating + rating_range
        and filter_by_tags(p)
    ]
    if not filtered:
        return None
    return random.choice(filtered)


def get_random_puzzle(min_rating, max_rating):
    filtered = [
        p for p in puzzles
        if min_rating <= p["rating"] <= max_rating
        and filter_by_tags(p)
    ]
    if not filtered:
        return None
    return random.choice(filtered)


def print_puzzle(puzzle):
    print("\n=== Puzzle ===")
    print(f"FEN: {puzzle['fen']}")
    print(f"PGN: {puzzle['pgn']}")
    print(f"Estimated Rating: {puzzle['rating']}")
    print(f"Tags: {', '.join(puzzle.get('tags', []))}\n")


def update_daily_scale():
    """
    Increase puzzle difficulty each day, reset on Monday.
    """
    global daily_min_rating, daily_max_rating, last_day

    today = datetime.now().date()
    weekday = datetime.now().weekday()  # 0 = Monday, 6 = Sunday

    if last_day != today:
        if weekday == 0:  # Reset every Monday
            daily_min_rating = 100
            daily_max_rating = 1000
            print("\n[Reset] New week! Puzzle ratings reset.")
        else:
            # Increase difficulty gradually
            daily_min_rating += daily_scale_step
            daily_max_rating += daily_scale_step
            print(f"\n[Scale Up] Puzzle rating range increased to {daily_min_rating}-{daily_max_rating}")

        last_day = today


def daily_puzzle():
    global daily_puzzle_cache
    update_daily_scale()  # adjust rating scale first
    puzzle = get_random_puzzle(daily_min_rating, daily_max_rating)
    if puzzle:
        daily_puzzle_cache = puzzle
        print("=== Daily Puzzle ===")
        print_puzzle(puzzle)


def main():
    global current_rating, required_tags, blacklist_tags

    # Schedule daily puzzle every 24 hours
    schedule.every(24).hours.do(daily_puzzle)

    while True:
        print("Chess Puzzle DB")
        print("1: Get a puzzle near current rating")
        print("2: Next puzzle (a bit harder)")
        print("3: Show today's daily puzzle")
        print("4: Set required tags")
        print("5: Set blacklist tags")
        print("0: Exit")
        choice = input("Enter choice: ")

        if choice == "1":
            puzzle = get_puzzle_near_rating(current_rating, rating_range)
            if puzzle:
                print_puzzle(puzzle)
            else:
                print("No puzzle found with current filters.\n")
        elif choice == "2":
            current_rating += rating_step
            puzzle = get_puzzle_near_rating(current_rating, rating_range)
            if puzzle:
                print_puzzle(puzzle)
            else:
                print("No puzzle found with current filters.\n")
        elif choice == "3":
            if daily_puzzle_cache is None:
                print("Daily puzzle not generated yet. Generating now...")
                daily_puzzle()
            else:
                print("=== Daily Puzzle ===")
                print_puzzle(daily_puzzle_cache)
        elif choice == "4":
            tags = input("Enter required tags (comma separated, empty to clear): ").strip()
            required_tags = set([t.strip() for t in tags.split(",") if t.strip()]) if tags else set()
            print(f"Required tags set to: {required_tags}")
        elif choice == "5":
            tags = input("Enter blacklist tags (comma separated, empty to clear): ").strip()
            blacklist_tags = set([t.strip() for t in tags.split(",") if t.strip()]) if tags else set()
            print(f"Blacklist tags set to: {blacklist_tags}")
        elif choice == "0":
            print("Exiting...")
            break
        else:
            print("Invalid choice! Please try again.\n")

        # Run scheduled jobs (daily puzzle + scaling)
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
