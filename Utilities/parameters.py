import datetime
import os


def get_configs():
    """
    Read configs from config file to dictionary. If no file - returns dict with 1 crucial parameter.

    Return:
    - dict: dictionary with parameters.
    """
    try:
        with open('config.txt', 'r') as file:
            configs = {line.strip().split('=')[0]: line.strip().split('=')[1] for line in file if '=' in line}
        return configs
    except FileNotFoundError:
        print(f"Critical Error: File not found - 'config.txt'")
        return {'DESTINATION_FOLDER': '"./data"'}


def get_directions():
    """
    Read directions from directions file to list. If no file - returns empty list.

    Return:
    - list: list of directions.
    """
    try:
        with open('directions.txt', 'r') as file:
            directions = [line[:-1] for line in file]
        return directions
    except FileNotFoundError:
        print(f"Critical Error: File not found - 'config.txt'")
        return []


def get_files_todo_from_date(destination_folder, directions, extension, date=''):
    """
    Returns list of all files named yyyy-mm-dd.xxx in all directions starting from the given date.

    Function compares the name of file with the given date.

    Parameters:
    - destination_folder (str) : root folder.
    - directions (iter) : list of directions.
    - extension (str) : extension of needed files, without '.'
    - date (str) : date in yyyy-mm-dd format. Today date if empty.

    Return:
    - list: list of files' full paths.
    """
    # set data from attrs, default is today
    date_from = datetime.date.fromisoformat(date) if date else datetime.date.today()

    files_todo_list = []
    for direction in directions:
        # list of files in direction folder (e.g ./HKI TPE/)
        for file_name in os.listdir(os.path.join(destination_folder, direction)):
            try:
                # file to process must be named yyyy-mm-dd.txt
                file_date = datetime.date.fromisoformat(file_name[:-4])
                if file_date >= date_from and file_name[-3:] == extension:
                    # add full path to the result
                    path = os.path.join(destination_folder, direction, file_name)
                    files_todo_list.append(path)

            except Exception as e:
                print(f"Error with file name {file_name}: {e}")
                pass

    return files_todo_list


def get_files_todo_unpaired(destination_folder, directions):
    """
    Returns list of all files named yyyy-mm-dd.txt in all directions if they don't have a .csv pair.

    Each processed file was named the same with .txt by default.

    Parameters:
    - destination_folder (str) : root folder.
    - directions (iter) : list of directions.

    Return:
    - list: list of files' full paths.
    """

    files_todo_list = []
    for direction in directions:
        # list of files in direction folder (e.g ./HKI TPE/)
        for file_name in os.listdir(os.path.join(destination_folder, direction)):
            # define full path
            path = os.path.join(destination_folder, direction, file_name)

            # check if file with the same name but .csv exists
            if not os.path.exists(path[:-3] + 'csv'):
                # add path to the result if not
                files_todo_list.append(path)

    return files_todo_list
