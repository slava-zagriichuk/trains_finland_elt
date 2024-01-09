import datetime

def log(message, logfile):
    """
    Write log message into file (process_log.txt by default) in format [date time] message.

    Parameters:
    - message (str) : message to log.
    - logfile (str) : output file path.

    Return:
    - bool: True if writing is successful, False otherwise.
    """
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S')

    try:
        with open(logfile, 'a') as file:
            file.write("[{}] {}\n".format(formatted_datetime, message))
        return True
    except Exception as e:
        print(f"Error writing output to {logfile}: {e}")
        return False

