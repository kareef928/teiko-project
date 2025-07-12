import sqlite3
import pandas as pd


# part 1: data management - create database schema and load data


def load_csv_data(csv_file: str):
    """
    Load data from CSV into two tables as the schema above

    Args:
        csv_file (str, optional): The original csv file with all columns in one table. Defaults to "data/cell-count.csv".
    """
    # read the csv
    full_df = pd.read_csv(csv_file)

    # create the two tables as outlined in the schema
    cell_count_cols = [
        "sample",
        "b_cell",
        "cd8_t_cell",
        "cd4_t_cell",
        "nk_cell",
        "monocyte",
    ]
    metadata_columns = [
        "sample",
        "project",
        "subject",
        "condition",
        "age",
        "sex",
        "treatment",
        "response",
        "sample_type",
        "time_from_treatment_start",
    ]

    cell_counts_df = full_df[cell_count_cols].copy()
    metadata_df = full_df[metadata_columns].copy()

    # rename 'sample' to 'sample_id' for specificity
    cell_counts_df = cell_counts_df.rename(columns={"sample": "sample_id"})
    metadata_df = metadata_df.rename(columns={"sample": "sample_id"})

    # connect to database
    conn = sqlite3.connect("data/cell_info.db")
    cursor = conn.cursor()

    # drop and recreate tables to ensure proper schema
    cursor.execute("DROP TABLE IF EXISTS cell_counts")
    cursor.execute("DROP TABLE IF EXISTS metadata")

    # recreate tables with proper primary keys
    cursor.execute(
        """
        CREATE TABLE cell_counts (
            sample_id TEXT PRIMARY KEY,
            b_cell INTEGER,
            cd8_t_cell INTEGER,
            cd4_t_cell INTEGER,
            nk_cell INTEGER,
            monocyte INTEGER
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE metadata (
            sample_id TEXT PRIMARY KEY,
            project TEXT,
            subject TEXT,
            condition TEXT,
            age INTEGER,
            sex TEXT,
            treatment TEXT,
            response TEXT,
            sample_type TEXT,
            time_from_treatment_start INTEGER
        )
    """
    )

    # insert data using pandas
    cell_counts_df.to_sql("cell_counts", conn, if_exists="append", index=False)
    metadata_df.to_sql("metadata", conn, if_exists="append", index=False)

    conn.commit()
    conn.close()
    print("Data loading complete")


def verify_data_loading():
    """
    Verify that data was loaded correctly. Testing individual tables as well as their relationship
    """

    conn = sqlite3.connect("data/cell_info.db")

    # check cell_counts table
    print("cell_counts table head:")
    cell_counts_head = pd.read_sql_query("SELECT * FROM cell_counts LIMIT 5", conn)
    print(cell_counts_head)
    print()

    # check metadata table
    print("metadata table head:")
    metadata_head = pd.read_sql_query("SELECT * FROM metadata LIMIT 5", conn)
    print(metadata_head)
    print()

    # test a join to make sure the relationship works
    print("joined data head:")
    join_test = pd.read_sql_query(
        """
        SELECT cc.sample_id, cc.b_cell, m.treatment, m.condition
        FROM cell_counts cc
        JOIN metadata m ON cc.sample_id = m.sample_id
        LIMIT 5
    """,
        conn,
    )
    print(join_test)

    conn.close()


if __name__ == "__main__":

    # load data and create schema
    csv_file = "data/cell-count.csv"
    load_csv_data(csv_file=csv_file)

    # quick verification that data was loaded properly
    verify_data_loading()
