import sqlite3
import pandas as pd


# part 2: exploratory data analysis (calculate relative frequencies of each cell type in the cell_counts dataframe)


def calc_relative_celltype_freqs(df: pd.DataFrame, cell_types: list):
    """
    Generate a summary table of the relative frequency of each cell population per sample and population

    Args:
        df (pd.DataFrame): DataFrame of the samples as well as cell counts for each population within each sample
        cell_types (list): A list of the cell populations we want to find the relative frequencies of

    Returns:
        long_df (pd.DataFrame): DataFrame with sample, total_count, population, count, and percentage columns
    """

    # calculate total count for each sample
    df["total_count"] = df[cell_types].sum(axis=1)

    # melt the dataframe so each row is one row per sample per population
    long_df = cell_counts_df.melt(
        id_vars=["sample_id", "total_count"],
        value_vars=cell_types,
        var_name="population",
        value_name="count",
    )

    # calculate relative percentage of the count of a particular population in a sample over the total count of all populations in the sample
    long_df["percentage"] = (long_df["count"] / long_df["total_count"] * 100).round(2)

    # rename for output
    long_df = long_df.rename(columns={"sample_id": "sample"})

    # save long_df as summary table for part 3
    long_df.to_csv("data/part2_summary_table.csv", index=False)
    return long_df


if __name__ == "__main__":

    # connect to database
    conn = sqlite3.connect("data/cell_info.db")

    # load table as dataframe
    cell_counts_df = pd.read_sql_query("SELECT * from cell_counts", conn)

    conn.close()

    # list of cell types we want to calculate the relative frequencies for
    cell_types = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]

    # get relative frequency table for each cell type for each sample
    cell_type_df = calc_relative_celltype_freqs(cell_counts_df, cell_types)
    print(cell_type_df)
