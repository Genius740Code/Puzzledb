import json
import random

# Load puzzles from JSON
with open("puzzles.json", "r") as f:
    puzzles = json.load(f)

starting_rating = 100     # initial target rating
rating_step = 50          # how much the target rating increases each step
rating_range = 50         # how far above/below the target rating to search

current_rating = starting_rating

def get_puzzle_near_rating(target_rating, rating_range):
    # Filter puzzles within target rating ± rating_range
    filtered = [p for p in puzzles if target_rating - rating_range <= p["rating"] <= target_rating + rating_range]
    if not filtered:
        print("No puzzles found in this rating range. Try adjusting your range.")
        return None
    return random.choice(filtered)

def print_puzzle(puzzle):
    print("\n=== Puzzle ===")
    print(f"FEN: {puzzle['fen']}")
    print(f"PGN: {puzzle['pgn']}")
    print(f"Estimated Rating: {puzzle['rating']}\n")

def main():
    global current_rating
    while True:
        print("Chess Puzzle DB")
        print("1: Get a puzzle near current rating")
        print("2: Next puzzle (a bit harder)")
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
        elif choice == "0":
            print("Exiting...")
            break
        else:
            print("Invalid choice! Please try again.\n")

if __name__ == "__main__":
    main()
