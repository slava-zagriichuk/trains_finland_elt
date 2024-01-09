from Utilities import psql
from Utilities import parameters
from Utilities.log import log

# get configs from config.txt
CONFIGS = parameters.get_configs()

# get destination (root) folder from configs
DESTINATION_FOLDER = CONFIGS['DESTINATION_FOLDER'][1:-1]

# get directions from directions.txt
DIRECTIONS = parameters.get_directions()


def main():
    # get 'todolist' of the files from specific date to load to db (from today by default)
    files_to_load = parameters.get_files_todo_from_date(destination_folder=DESTINATION_FOLDER,
                                                        directions=DIRECTIONS,
                                                        date='',
                                                        extension='csv')

    # make record of planned to process files to log file
    for file_path in files_to_load:
        log(file_path + ' planned to be loaded to db', './logs/db_log.txt')

    for file_path in files_to_load:
        # obtaining direction name from file path (./ folder of the file) and make it compatible to postgres
        table_name = file_path.split('/')[-2].replace(' ', '_').lower()

        # load csv file to the appropriate table
        psql.load_csv(table_name=table_name, csv_file_path=file_path, headers=True)


if __name__ == "__main__":
    main()
