"""Run: python3 budget_tool.py (macOS) or py budget_tool.py (Windows)."""
import csv
from pathlib import Path


def affordable(items, budget):
    chosen = []
    for item in items:
        if item["price"] <= budget:
            chosen.append(item["name"])
    return chosen


def load_menu():
    path = Path(__file__).with_name("student-menu.csv")
    with path.open(encoding="utf-8-sig", newline="") as file:
        items = list(csv.DictReader(file))
    for item in items:
        item["price"] = int(item["price"])
    return items


def main():
    try:
        budget = int(input("Budget in yen: "))
    except ValueError:
        print("Enter a whole number, such as 1000.")
        return
    if budget < 0:
        print("Budget must be zero or more.")
        return
    try:
        names = affordable(load_menu(), budget)
    except FileNotFoundError:
        print("Put student-menu.csv beside budget_tool.py.")
        return
    print(names if names else "No options. Try another budget.")


if __name__ == "__main__":
    main()
