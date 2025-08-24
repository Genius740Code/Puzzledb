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

# Current puzzle state for hints
current_puzzle = None
hints_used = 0


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


def print_puzzle(puzzle, show_hints=False):
    global current_puzzle, hints_used
    current_puzzle = puzzle
    hints_used = 0
    
    print("\n=== Puzzle ===")
    print(f"FEN: {puzzle['fen']}")
    print(f"PGN: {puzzle['pgn']}")
    print(f"Estimated Rating: {puzzle['rating']}")
    print(f"Tags: {', '.join(puzzle.get('tags', []))}")
    print(f"Moves to solve: {puzzle.get('move_count', 'Unknown')}")
    print(f"Description: {puzzle.get('description', 'No description available')}")
    
    if show_hints:
        print(f"Hint 1 (Piece): {puzzle.get('hint1', 'No hint available')}")
        if puzzle.get('hint2'):
            print(f"Hint 2 (Move): {puzzle.get('hint2', 'No hint available')}")
    
    print("\nOptions: (h)int, (s)olution, (n)ext puzzle, (m)enu")


def show_hint():
    global hints_used, current_puzzle
    
    if current_puzzle is None:
        print("No active puzzle! Please select a puzzle first.\n")
        return
    
    hints_used += 1
    
    # Get hints array (piece, move, piece, move, etc.)
    hints = current_puzzle.get('hints', [])
    
    if hints_used <= len(hints):
        hint = hints[hints_used - 1]
        hint_type = "Piece" if (hints_used - 1) % 2 == 0 else "Move"
        move_number = (hints_used + 1) // 2
        
        if hint_type == "Piece":
            print(f"\n💡 Hint {hints_used} (Move {move_number}): Look for a {hint} move!")
        else:
            print(f"\n💡 Hint {hints_used} (Move {move_number}): Try {hint}")
    else:
        print("\n💡 No more hints available! Use 's' for the full solution.")


def show_solution():
    global current_puzzle
    
    if current_puzzle is None:
        print("No active puzzle! Please select a puzzle first.\n")
        return
    
    solution = current_puzzle.get('solution', ['No solution available'])
    move_count = current_puzzle.get('move_count', len(solution))
    
    print(f"\n✅ Solution ({move_count} move{'s' if move_count != 1 else ''}):")
    for i, move in enumerate(solution, 1):
        print(f"  {i}. {move}")
    
    if current_puzzle.get('description'):
        print(f"\nExplanation: {current_puzzle['description']}")


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


def puzzle_interaction_loop():
    """Handle hints, solutions, and navigation for current puzzle"""
    global current_puzzle
    
    if current_puzzle is None:
        return
    
    while True:
        choice = input("\nAction (h/s/n/m): ").lower().strip()
        
        if choice == 'h':
            show_hint()
        elif choice == 's':
            show_solution()
        elif choice == 'n':
            # Get next puzzle with increased rating
            global current_rating
            current_rating += rating_step
            puzzle = get_puzzle_near_rating(current_rating, rating_range)
            if puzzle:
                print_puzzle(puzzle)
            else:
                print("No puzzle found with current filters.\n")
                break
        elif choice == 'm':
            break
        else:
            print("Invalid choice! Use: (h)int, (s)olution, (n)ext puzzle, (m)enu")


def main():
    global current_rating, required_tags, blacklist_tags

    # Schedule daily puzzle every 24 hours
    schedule.every(24).hours.do(daily_puzzle)

    while True:
        print("\n" + "="*50)
        print("Chess Puzzle DB")
        print("="*50)
        print("1: Get a puzzle near current rating")
        print("2: Get random puzzle in rating range")
        print("3: Show today's daily puzzle")
        print("4: Set required tags")
        print("5: Set blacklist tags")
        print("6: Show current settings")
        print("0: Exit")
        print("="*50)
        choice = input("Enter choice: ")

        if choice == "1":
            puzzle = get_puzzle_near_rating(current_rating, rating_range)
            if puzzle:
                print_puzzle(puzzle)
                puzzle_interaction_loop()
            else:
                print("No puzzle found with current filters.\n")
        elif choice == "2":
            min_rating = int(input(f"Min rating (current: {current_rating - rating_range}): ") or current_rating - rating_range)
            max_rating = int(input(f"Max rating (current: {current_rating + rating_range}): ") or current_rating + rating_range)
            puzzle = get_random_puzzle(min_rating, max_rating)
            if puzzle:
                print_puzzle(puzzle)
                puzzle_interaction_loop()
            else:
                print("No puzzle found with current filters.\n")
        elif choice == "3":
            if daily_puzzle_cache is None:
                print("Daily puzzle not generated yet. Generating now...")
                daily_puzzle()
            else:
                print("=== Daily Puzzle ===")
                print_puzzle(daily_puzzle_cache)
            puzzle_interaction_loop()
        elif choice == "4":
            print(f"Current required tags: {required_tags}")
            tags = input("Enter required tags (comma separated, empty to clear): ").strip()
            required_tags = set([t.strip() for t in tags.split(",") if t.strip()]) if tags else set()
            print(f"Required tags set to: {required_tags}")
        elif choice == "5":
            print(f"Current blacklist tags: {blacklist_tags}")
            tags = input("Enter blacklist tags (comma separated, empty to clear): ").strip()
            blacklist_tags = set([t.strip() for t in tags.split(",") if t.strip()]) if tags else set()
            print(f"Blacklist tags set to: {blacklist_tags}")
        elif choice == "6":
            print(f"\nCurrent Settings:")
            print(f"Current Rating: {current_rating}")
            print(f"Rating Range: ±{rating_range}")
            print(f"Required Tags: {required_tags if required_tags else 'None'}")
            print(f"Blacklist Tags: {blacklist_tags if blacklist_tags else 'None'}")
            print(f"Daily Rating Range: {daily_min_rating}-{daily_max_rating}")
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