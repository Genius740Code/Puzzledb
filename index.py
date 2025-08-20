import json
import random

# Load puzzles from JSON
with open("puzzles.json", "r") as f:
    puzzles = json.load(f)

def get_random_puzzle():
    puzzle = random.choice(puzzles)
    print("\n=== Random Puzzle ===")
    print(f"FEN: {puzzle['fen']}")
    print(f"PGN: {puzzle['pgn']}")
    print(f"Estimated Rating: {puzzle['rating']}\n")

def main():
    while True:
        print("Chess Puzzle DB")
        print("1: Get a random puzzle")
        print("0: Exit")
        choice = input("Enter choice: ")
        
        if choice == "1":
            get_random_puzzle()
        elif choice == "0":
            print("Exiting...")
            break
        else:
            print("Invalid choice! Please try again.\n")

if __name__ == "__main__":
    main()
