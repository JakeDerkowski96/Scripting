#!/usr/bin/env python3
"""Interactively modify Azure Sentinel analytic rule ARM templates.

Supports modifying rule status (enabled/disabled), query frequency, and query period.
Exports modified rules as new ARM template files with a user-specified prefix.
"""

import json
import sys


def select_files():
    """Prompt user for ARM template file paths and validate them."""
    while True:
        raw = input(
            "\nEnter file path(s) of Sentinel Analytics Rule ARM templates.\n"
            "Separate multiple paths with commas (CTRL+C to exit):\n"
        )
        paths = [p.strip().strip("'\"").removeprefix("& ") for p in raw.split(",")]

        if not all(p.endswith(".json") for p in paths):
            print("\nIncorrect file type. All files must be .json.")
            continue

        valid = True
        for path in paths:
            try:
                open(path, "r").close()
            except (FileNotFoundError, OSError):
                print(f"\nFile not found: {path}")
                valid = False
                break

        if valid:
            return paths


def select_values(properties):
    """Prompt user to select new values for each property."""
    definitions = {
        "enabled": {
            "name": "Rule Status",
            "options": {"1": ("Enabled", True), "2": ("Disabled", False)},
        },
        "queryFrequency": {
            "name": "Rule Frequency",
            "options": {
                "1": ("Days", "P{n}D"),
                "2": ("Hours", "PT{n}H"),
                "3": ("Minutes", "PT{n}M"),
            },
        },
        "queryPeriod": {
            "name": "Rule Period",
            "options": {
                "1": ("Days", "P{n}D"),
                "2": ("Hours", "PT{n}H"),
                "3": ("Minutes", "PT{n}M"),
            },
        },
    }

    new_values = {}
    for prop in properties:
        defn = definitions[prop]

        while True:
            print(f"\nSelect an option for {defn['name']}:")
            for key, (label, _) in defn["options"].items():
                print(f"  {key}: {label}")

            choice = input("\nEnter selection: ").strip()
            if choice not in defn["options"]:
                print("Invalid selection. Try again.")
                continue

            label, template = defn["options"][choice]

            if prop in ("queryFrequency", "queryPeriod"):
                while True:
                    time_input = input(f"\nEnter {label.lower()} as a positive integer: ").strip()
                    try:
                        n = int(time_input)
                        if n <= 0:
                            raise ValueError
                        break
                    except ValueError:
                        print("Please enter a positive integer.")

                new_values[prop] = template.format(n=n)
                unit = label.rstrip("s") if n == 1 else label
                print(f"Setting {defn['name']} to {n} {unit}")
            else:
                new_values[prop] = template
                print(f"Setting {defn['name']} to {label}")
            break

    return new_values


def modify_templates(paths, new_values, properties):
    """Apply new property values to ARM templates and export with prefix."""
    while True:
        prefix = input(
            "\nEnter a prefix for new filenames (alphanumeric, underscores, spaces):\n"
        ).strip()

        if not prefix:
            print("Prefix cannot be empty.")
            continue

        if all(c.isalnum() or c in " _" for c in prefix):
            break
        print("Invalid characters in prefix. Use only A-Z, a-z, 0-9, underscores, or spaces.")

    for filepath in paths:
        with open(filepath, "r") as f:
            data = json.load(f)

        for resource in data.get("resources", []):
            for prop in properties:
                if "properties" in resource:
                    resource["properties"][prop] = new_values[prop]

        filename = filepath.replace("\\", "/").split("/")[-1]
        new_path = filepath.replace(filename, prefix + filename)

        with open(new_path, "w") as f:
            json.dump(data, f, indent=4)

        print(f"Exported: {new_path}")


def main():
    property_map = {"1": "enabled", "2": "queryFrequency", "3": "queryPeriod"}

    paths = select_files()

    while True:
        print(
            "\nSelect properties to modify (comma-separated):\n"
            "  1: Rule Status (Enabled/Disabled)\n"
            "  2: Rule Frequency\n"
            "  3: Rule Period"
        )
        selections = input("\nEnter values: ").replace(" ", "").split(",")

        try:
            properties = list(dict.fromkeys(property_map[s] for s in selections))
            break
        except KeyError:
            print("Invalid selection. Use numbers 1-3.")

    new_values = select_values(properties)
    modify_templates(paths, new_values, properties)
    print("\nProcess completed.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting.")
        sys.exit(0)
