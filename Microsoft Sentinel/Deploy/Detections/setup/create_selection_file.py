import os
import csv
import argparse
import configparser

def create_csv(base_directory, csv_file):
    with open(csv_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Selected", "Subdirectory"])  # Header row

        for subdirectory in os.listdir(base_directory):
            full_path = os.path.join(base_directory, subdirectory)
            if os.path.isdir(full_path):  # Ensure it's a directory
                writer.writerow(["", subdirectory])  # Default "Selected" column to empty

    print(f"CSV file '{csv_file}' created successfully.")

if __name__ == "__main__":
    # Argument parsing
    parser = argparse.ArgumentParser(description="Create a CSV file from subdirectories.")
    parser.add_argument("--config", required=True, help="Path to configuration file")
    args = parser.parse_args()

    # Load configuration
    config = configparser.ConfigParser()
    config.read(args.config)
    base_directory = config["Paths"]["base_directory"]
    csv_file = config["Paths"]["csv_file"]

    # Call the function
    create_csv(base_directory, csv_file)