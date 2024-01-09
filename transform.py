from Utilities import processing
from Utilities import parameters
from Utilities.log import log

# get configs from config.txt
CONFIGS = parameters.get_configs()

# get destination (root) folder from configs
DESTINATION_FOLDER = CONFIGS['DESTINATION_FOLDER'][1:-1]

# get directions from directions.txt
DIRECTIONS = parameters.get_directions()


def main():
    # get 'todolist' of the files to process
    # there are 2 funcs for this: get_files_todo_unpaired() or get_files_todo_from_date()
    files_todo = parameters.get_files_todo_from_date(destination_folder=DESTINATION_FOLDER,
                                                     directions=DIRECTIONS,
                                                     extension='txt',
                                                     date='')

    # make record of planned to process files to log file
    for file_path in files_todo:
        log(file_path + ' planned to be processed', "./logs/processing_log.txt")

    # processing of all the files from todolist
    for file_path in files_todo:
        # parse raw file with json responses to the list of dictionaries
        parsed_file = processing.read_parse_file(file_path=file_path)

        # extract the necessary attributes to csv table
        # file_name without extension is request date
        request_date = file_path[-14:-4]
        processed_data = processing.process_data(parsed_file=parsed_file,
                                                 request_date=request_date,
                                                 header=True)

        # write to the file with the same name but .csv extension
        processing.write_output(output_data=processed_data, output_file=file_path[:-3] + 'csv')

        # make record to the logfile
        log(file_path[:-3] + 'csv' + ' has been recorded', "./logs/processing_log.txt")


if __name__ == "__main__":
    main()
