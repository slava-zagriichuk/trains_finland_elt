from Utilities import psql
from Utilities import parameters

# get configs from config.txt
CONFIGS = parameters.get_configs()

# get directions from directions.txt
DIRECTIONS = parameters.get_directions()


def main():
    # create mat. views refresh function
    psql.create_trigger_function()

    for direction in DIRECTIONS:
        # make direction name compatible to postgres
        table_name = direction.replace(' ', '_').lower()

        # create table for specific direction data
        psql.create_table(table_name=table_name)

        # create materialized view for keeping the most recent requested journeys' data
        psql.create_mat_view_current(table_name=table_name)

        # create materialized view for keeping the most recent price range by days
        psql.create_mat_view_price_range(table_name=table_name)

        # create insert trigger for mat. views refresh function
        psql.create_trigger(table_name=table_name)


if __name__ == "__main__":
    main()
