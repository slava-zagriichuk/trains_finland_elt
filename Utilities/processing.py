import json
import datetime
from Utilities.log import log

# Hard coding of headers to the output file
HEADERS = [
    'journey_id',
    'departure_time',
    'departure_station',
    'arrival_station',
    'arrival_time',
    'price',
    'train_number',
    'train_type',
    'eco_seats_available',
    'request_date',
]


def parse_json_line(line):
    """
    Parsing single line json into dict.

    Parameters:
    - line (str) : single lined json expression.

    Return:
    - parsed_line (dict) : parsed json expression successfully.
    - None : string couldn't be parsed for any reason.
    """
    try:
        parsed_line = json.loads(line)
        return parsed_line
    except Exception as e:
        log(e, "./logs/processing_log.txt")
        log(line + "\ncouldn't be parsed", "./logs/processing_log.txt")
        return None


def read_parse_file(file_path):
    """
    Parse multiline file with json responses into list of dictionaries.

    Parameters:
    - file_path (str) : path to file.

    Return:
    - parsed_file (list with dictionaries) : list of parsed json strings.
    - None : something wrong with file.
    """
    try:
        with open(file_path, 'r') as file:
            parsed_file = [parse_json_line(line) for line in file if parse_json_line(line)]
        return parsed_file
    except FileNotFoundError:
        log(f"Error: File not found - {file_path}", "./logs/processing_log.txt")
        return None
    except Exception as e:
        log(f"Error: {e}", "./logs/processing_log.txt")
        return None


def process_line_to_csv(parsed_line, request_date):
    """
    Process (extract attributes from) parsed single json response into csv-formatted string.

    Parameters:
    - parsed_line (dict) : parsed json response (single)

    Return:
    - str : csv-formatted extracted attributes.
    Empty string if no attributes could be extracted.
    """
    result = ''
    try:
        # each response describes 0 or more trip details
        for journey in parsed_line['data']['searchJourney']:
            # sometimes there are journeys with error, which can ruin the loop. Just skip them
            if journey['error']:
                # print(journey['error'])
                continue

            if journey['legs'][0]['type'] != 'COMMUTER':
                # productAttributes is a list with 27 dictionaries, from which
                # ECO_CLASS_SEAT without attributes is needed to be extracted
                availability = journey['legs'][0]['productAttributes']
                eco_seats_available = [item['availability'] for item in availability if
                                       item['name'] == 'ECO_CLASS_SEAT' and item['attribute'] is None]
            # Commuters have no available seats option
            else:
                eco_seats_available = [-1]

            # list of all the extracted parameters + request date
            attributes_list = [
                journey['id'],
                journey['departureTime'],
                journey['departureStation'],
                journey['arrivalStation'],
                journey['arrivalTime'],
                str(journey['totalPrice'] / 100),
                journey['legs'][0]['trainNumber'],
                journey['legs'][0]['trainType'],
                str(eco_seats_available[0]),
                request_date,
            ]

            # turning into csv format every attributes_list line by line
            result += ','.join(attributes_list) + '\n'
    except Exception as e:
        log(f"Error: {e}", "./logs/processing_log.txt")
        log(f"line begins: {parsed_line[:60]}", "./logs/processing_log.txt")
    return result


def process_data(parsed_file, request_date, header=True):
    """
    Turn the whole parsed file into csv-formatted string.

    Parameters:
    - parsed_file (list) : parsed file into the list of dictionaries (json-responses).

    Return:
    - str : final csv-formatted data.
    """
    output_data = ','.join(HEADERS) + '\n' if header else ''

    for parsed_line in parsed_file:
        output_data += process_line_to_csv(parsed_line, request_date)

    # remove the artifact: last '\n' symbol
    return output_data[:-1]


def write_output(output_data, output_file):
    """
    Simply write output data to the file.

    Parameters:
    - output_data (str) : processed data
    - output_file (str) : output file path

    Return:
    - bool: True if writing is successful, False otherwise.
    """
    try:
        with open(file=output_file, mode='w') as file:
            file.write(output_data)
        return True
    except Exception as e:
        log(f"Error writing output to {output_file}: {e}", "./logs/processing_log.txt")
        return False

