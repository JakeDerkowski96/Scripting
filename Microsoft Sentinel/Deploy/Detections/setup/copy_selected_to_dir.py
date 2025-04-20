import os
import shutil
import csv
import argparse
import configparser

def process_csv(base_directory, csv_file, output_directory):
    # Create output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    with open(csv_file, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            selected = row["Selected"]
            subdirectory = row["Subdirectory"]

            if selected and selected.strip():  # Non-empty and not null
                source_path = os.path.join(base_directory, subdirectory)
                destination_path = os.path.join(output_directory, subdirectory)

                if os.path.isdir(source_path):  # Copy directory contents
                    shutil.copytree(source_path, destination_path, dirs_exist_ok=True)
                    print(f"Copied '{subdirectory}' to '{output_directory}' folder.")

    print("Processing complete.")

if __name__ == "__main__":
    # Argument parsing
    parser = argparse.ArgumentParser(description="Process a CSV file and copy directories.")
    parser.add_argument("--config", required=True, help="Path to configuration file")
    args = parser.parse_args()

    # Load configuration
    config = configparser.ConfigParser()
    config.read(args.config)
    base_directory = config["Paths"]["base_directory"]
    csv_file = config["Paths"]["csv_file"]
    output_directory = os.path.join(os.path.expanduser("~"), "Desktop", config["Paths"]["output_directory"])

    # Call the function
    process_csv(base_directory, csv_file, output_directory)