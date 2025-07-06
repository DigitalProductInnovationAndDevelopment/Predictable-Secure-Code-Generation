import os


def list_code_files(dir_path):
    """
    Recursively walks through dir_path and returns a list of all file paths.

    Args:
        dir_path (str): Path to the directory containing code files.

    Returns:
        List[str]: A list of full paths to each file in the directory tree.
    """
    code_files = []
    for root, _, files in os.walk(dir_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            code_files.append(file_path)
    return code_files


# Example usage:
# files = list_code_files("../ProjectBase/CodeBase/")
# for f in files:
#     print(f)
