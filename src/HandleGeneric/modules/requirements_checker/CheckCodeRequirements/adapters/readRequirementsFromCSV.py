import csv


def read_requirements_csv(file_path):
    """
    Reads a CSV file with columns 'id' and 'description' and returns
    a dict suitable for compare_requirements().
    """
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {row["id"]: row["description"].strip() for row in reader}
