import json
import random
import schedule
import time

# Load puzzles from JSON
with open("puzzles.json", "r") as f:
    puzzles = json.load(f)

# Configurable variables
starting_rating = 100
rating_step = 50
rating_range = 50

# Daily puzzle settings
daily_min_rating = 100
daily_max_rating = 1000

current_rating = starting_rating
daily_puzzle_cache = None  # Store the current daily puzzle

def get_puzzle_near_rating(target_rating, rating_range):
    filtered = [p for p in puzzles if target_rating - rating_range <= p["rating"] <= target_rating + rating_range]
    if not filtered:
        return None
    return random.choice(filtered)

def get_random_puzzle(min_rating, max_rating):
    filtered = [p for p in puzzles if min_rating <= p["rating"] <= max_rating]
    if not filtered:
        return None
    return random.choice(filtered)

def print_puzzle(puzzle):
    print("\n=== Puzzle ===")
    print(f"FEN: {puzzle['fen']}")
    print(f"PGN: {puzzle['pgn']}")
    print(f"Estimated Rating: {puzzle['rating']}\n")

def daily_puzzle():
    global daily_puzzle_cache
    puzzle = get_random_puzzle(daily_min_rating, daily_max_rating)
    if puzzle:
        daily_puzzle_cache = puzzle
        print("=== Daily Puzzle ===")
        print_puzzle(puzzle)

def main():
    global current_rating
    # Schedule daily puzzle every 24 hours
    schedule.every(24).hours.do(daily_puzzle)

    while True:
        print("Chess Puzzle DB")
        print("1: Get a puzzle near current rating")
        print("2: Next puzzle (a bit harder)")
        print("3: Show today's daily puzzle")
        print("0: Exit")
        choice = input("Enter choice: ")

        if choice == "1":
            puzzle = get_puzzle_near_rating(current_rating, rating_range)
            if puzzle:
                print_puzzle(puzzle)
        elif choice == "2":
            current_rating += rating_step
            puzzle = get_puzzle_near_rating(current_rating, rating_range)
            if puzzle:
                print_puzzle(puzzle)
        elif choice == "3":
            if daily_puzzle_cache is None:
                print("Daily puzzle not generated yet. Generating now...")
                daily_puzzle()
            else:
                print("=== Daily Puzzle ===")
                print_puzzle(daily_puzzle_cache)
        elif choice == "0":
            print("Exiting...")
            break
        else:
            print("Invalid choice! Please try again.\n")

        # Run scheduled jobs (daily puzzle)
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
