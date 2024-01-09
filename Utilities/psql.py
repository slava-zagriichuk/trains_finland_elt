import psycopg2
import csv
from configparser import ConfigParser
from Utilities.processing import HEADERS
from Utilities.log import log


def config(filename='./database.ini', section='postgresql'):
    """
    Extract database parameters from config file. By default from database.ini for PostgreSQL db.

    Parameters:
    - filename (str) : configurations file.
    - section (str): section marked [section]

    Return:
    - parsed_line (dict) : parsed db configurations.
    """
    # create a parser
    parser = ConfigParser()
    
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    return db


def create_table(table_name):
    """
    Create table with prescribed columns.

    Parameters:
    - table_name (str) : table name

    Return:
    - bool: True if successful, False otherwise.
    """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        log('Connecting to the PostgreSQL database...', './logs/db_log.txt')
        conn = psycopg2.connect(**params)

        # create a cursor
        cursor = conn.cursor()

        # construct a create table statement
        create_table_query = """CREATE TABLE IF NOT EXISTS {} (
                id SERIAL PRIMARY KEY,
                {} VARCHAR(40),
                {} TIMESTAMPTZ,
                {} VARCHAR(3),
                {} VARCHAR(3),
                {} TIMESTAMPTZ,
                {} NUMERIC(5,2),
                {} VARCHAR(4),
                {} VARCHAR(3),
                {} SMALLINT,
                {} DATE
            );""".format(table_name, *HEADERS)

        # execute a statement
        cursor.execute(create_table_query)
        log(f"{table_name} has been created", './logs/db_log.txt')

        # commit changes
        conn.commit()

        # close the communication with the PostgreSQL
        cursor.close()
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        log(error, './logs/db_log.txt')
        return False
    finally:
        if conn is not None:
            conn.close()
            log('Database connection closed.', './logs/db_log.txt')


def create_trigger_function():
    """
    Create trigger function for refreshing both materialized views.

    Return:
    - bool: True if successful, False otherwise.
    """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        log('Connecting to the PostgreSQL database...', './logs/db_log.txt')
        conn = psycopg2.connect(**params)

        # create a cursor
        cursor = conn.cursor()

        # construct create a materialized view statement
        create_function_query = """CREATE OR REPLACE FUNCTION refresh_materialized_views()
              RETURNS TRIGGER AS
                $$
                BEGIN
                  IF TG_ARGV[0] IS NOT NULL THEN
                    EXECUTE FORMAT('REFRESH MATERIALIZED VIEW %I', CONCAT(TG_ARGV[0], '_current'));
                    EXECUTE FORMAT('REFRESH MATERIALIZED VIEW %I', CONCAT(TG_ARGV[0], '_price_range'));
                  END IF;
                  RETURN NULL;
                END;
                $$ LANGUAGE plpgsql;"""

        # execute a statement
        cursor.execute(create_function_query)
        log("Function refresh_materialized_views() has been created", './logs/db_log.txt')

        # commit changes
        conn.commit()

        # close the communication with the PostgreSQL
        cursor.close()
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        log(error, './logs/db_log.txt')
        return False
    finally:
        if conn is not None:
            conn.close()
            log('Database connection closed.', './logs/db_log.txt')


def create_mat_view_current(table_name, recreate=False):
    """
    Create materialized view: table with the most fresh journeys info.

    Parameters:
    - table_name (str) : table name for which mat. view will be created
    - recreate (bool) : recreate the view?

    Return:
    - bool: True if successful, False otherwise.
    """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        log('Connecting to the PostgreSQL database...', './logs/db_log.txt')
        conn = psycopg2.connect(**params)

        # create a cursor
        cursor = conn.cursor()

        # drop the materialized view if needed
        if recreate:
            drop_mat_view_query = f"""DROP MATERIALIZED VIEW {table_name + '_current'}"""
            cursor.execute(drop_mat_view_query)
            log(f"Old materialized view {table_name + '_current'} has been dropped", './logs/db_log.txt')

        # construct create a materialized view statement
        create_mat_view_query = f"""CREATE MATERIALIZED VIEW {table_name + '_current'} AS
                    SELECT departure_time::TIMESTAMP::DATE AS dep_date,
                    departure_time::TIMESTAMP::TIME AS dep_time,
                    arrival_time-departure_time AS time_travel,
                    arrival_time::TIMESTAMP::DATE AS arr_date,
                    arrival_time::TIMESTAMP::TIME AS arr_time,
                    eco_seats_available, price
                    FROM {table_name}
                    WHERE request_date = (SELECT MAX(request_date) FROM {table_name})
                    WITH DATA;"""

        # execute a statement
        cursor.execute(create_mat_view_query)
        log(f"Materialized view {table_name + '_current'} has been created", './logs/db_log.txt')

        # commit changes
        conn.commit()

        # close the communication with the PostgreSQL
        cursor.close()
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        log(error, './logs/db_log.txt')
        return False
    finally:
        if conn is not None:
            conn.close()
            log('Database connection closed.', './logs/db_log.txt')


def create_mat_view_price_range(table_name, recreate=False):
    """
    Create materialized view: table with the most fresh price range journeys info.

    Parameters:
    - table_name (str) : table name for which mat. view will be created
    - recreate (bool) : recreate the view?

    Return:
    - bool: True if successful, False otherwise.
    """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        log('Connecting to the PostgreSQL database...', './logs/db_log.txt')
        conn = psycopg2.connect(**params)

        # create a cursor
        cursor = conn.cursor()

        # drop the materialized view if needed
        if recreate:
            drop_mat_view_query = f"""DROP MATERIALIZED VIEW {table_name + '_price_range'}"""
            cursor.execute(drop_mat_view_query)
            log(f"Old materialized view {table_name + '_current'} has been dropped", './logs/db_log.txt')

        # construct create a materialized view statement
        create_mat_view_query = f"""CREATE MATERIALIZED VIEW {table_name + '_price_range'} AS
                    SELECT departure_time::TIMESTAMP::DATE AS dep_date, MIN(price), MAX(price)
                    FROM {table_name}
                    WHERE request_date = (SELECT MAX(request_date) FROM {table_name})
                    -- AND departure_time::TIMESTAMP::TIME BETWEEN '06:00' AND '23:00'
                    GROUP BY dep_date
                    ORDER BY dep_date
                    WITH DATA;"""

        # execute a statement
        cursor.execute(create_mat_view_query)
        log(f"Materialized view {table_name + '_current'} has been created", './logs/db_log.txt')

        # commit changes
        conn.commit()

        # close the communication with the PostgreSQL
        cursor.close()
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        log(error, './logs/db_log.txt')
        return False
    finally:
        if conn is not None:
            conn.close()
            log('Database connection closed.', './logs/db_log.txt')


def create_trigger(table_name):
    """
    Create insert trigger for the table.

    Parameters:
    - table_name (str) : table name for which trigger will be created

    Return:
    - bool: True if successful, False otherwise.
    """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        log('Connecting to the PostgreSQL database...', './logs/db_log.txt')
        conn = psycopg2.connect(**params)

        # create a cursor
        cursor = conn.cursor()

        # construct create a materialized view statement
        create_trigger_query = f"""CREATE TRIGGER trigger_{table_name}
                AFTER UPDATE ON {table_name}
                FOR EACH STATEMENT
                EXECUTE FUNCTION refresh_materialized_views('{table_name}');"""

        # execute a statement
        cursor.execute(create_trigger_query)
        log(f"Trigger trigger_{table_name} has been created", './logs/db_log.txt')

        # commit changes
        conn.commit()

        # close the communication with the PostgreSQL
        cursor.close()
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        log(error, './logs/db_log.txt')
        return False
    finally:
        if conn is not None:
            conn.close()
            log('Database connection closed.', './logs/db_log.txt')


def load_csv(table_name, csv_file_path, headers=True):
    """
    Load csv file to the table.

    Parameters:
    - table_name (str) : table for data to be loaded
    - csv_file_path (str) : path to csv file
    - headers (bool): True if csv file contains headers

    Return:
    - bool: True if successful, False otherwise.
    """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        log('Connecting to the PostgreSQL database...', './logs/db_log.txt')
        conn = psycopg2.connect(**params)

        # create a cursor
        cursor = conn.cursor()

        with open(csv_file_path, 'r') as csv_file:
            # Create a CSV reader
            csv_reader = csv.reader(csv_file)

            # Skip the header if it exists
            if headers:
                next(csv_reader, None)

            # Iterate through each row in the CSV file
            for row in csv_reader:
                # Construct the INSERT statement
                insert_query = f"""INSERT INTO {table_name} ({', '.join(HEADERS)})
                VALUES ({', '.join(['%s'] * len(HEADERS))});
                """

                # Execute the INSERT statement with the row data
                cursor.execute(insert_query, row)

            # fake update function doing nothing
            update_query = f"""UPDATE {table_name}
            SET train_type = train_type
            WHERE id = 1"""

            # Execute the fake UPDATE statement
            cursor.execute(update_query)

        log(f"{csv_file_path} were added to {table_name}", './logs/db_log.txt')

        # commit changes
        conn.commit()

        # close the communication with the PostgreSQL
        cursor.close()
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        log(error, './logs/db_log.txt')
        return False
    except Exception as e:
        log(f"Error: {e}", './logs/db_log.txt')
        return False
    finally:
        if conn is not None:
            conn.close()
            log('Database connection closed.', './logs/db_log.txt')
