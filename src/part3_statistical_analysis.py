import pandas as pd
import sqlite3
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu

# part 3: perform statistical analysis to determine if there are differences in immune cell population frequencies between patients who
# respond to miraclib and those who do not, filtered for patients with melanoma with PBMC samples


def load_data(summary_path: str, db_path: str):
    """
    Load summary table and metadata table

    Args:
        summary_path (str): Path to table of relative frequencies of each cell population for each sample (derived from part 2)
        db_path (str): Path to database to retrieve the metadata table

    Returns:
        tuple: (summary_df, metadata_df) - summary DataFrame and metadata DataFrame
    """
    # retrieve the summary dataframe that was created in part 2
    summary_df = pd.read_csv(summary_path)

    # retrieve the metadata df from the database
    conn = sqlite3.connect(db_path)
    metadata_df = pd.read_sql_query("SELECT * FROM metadata", conn)
    conn.close()
    return summary_df, metadata_df


def merge_filter_data(summary_df: pd.DataFrame, metadata_df: pd.DataFrame):
    """
    Merge summary and metadata tables, and then filter for melanoma, miraclib, and PBMC samples

    Args:
        summary_df (pd.DataFrame): Table of relative frequencies of each cell population for each sample
        metadata_df (pd.DataFrame): Table of metadata for each sample

    Returns:
        pd.DataFrame: Filtered table with merged data for melanoma, miraclib, and PBMC samples
    """

    # join the summary and metadata tables on sample
    merged_table = summary_df.merge(
        metadata_df, left_on="sample", right_on="sample_id", how="inner"
    )

    # filter the data for melanoma, miraclib, and PBMC
    filtered_table = merged_table[
        (merged_table["condition"] == "melanoma")
        & (merged_table["treatment"] == "miraclib")
        & (merged_table["sample_type"] == "PBMC")
    ]

    return filtered_table


def plot_boxplots(filtered_table: pd.DataFrame):
    """
    Plot boxplots showing the relative frequencies of each population by response group

    Args:
        filtered_table (pd.DataFrame): The filtered table with relative frequency information
    """
    plt.figure(figsize=(10, 6))

    # two boxplots per population, one being responders (yes) and the other being non-responders (no)
    sns.boxplot(data=filtered_table, x="population", y="percentage", hue="response")
    plt.title("Relative Frequencies of each Cell Population by Response")
    plt.xlabel("Cell Population")
    plt.ylabel("Relative Frequency (%)")
    plt.legend(title="Response")
    plt.tight_layout()

    # save the plot as a PNG file
    plt.savefig("data/part3_boxplot.png", dpi=300, bbox_inches="tight")
    plt.show()


def statistical_tests(filtered_table: pd.DataFrame):
    """
    Perform Mann-Whitney U test to test differences in cell population relative frequencies between responders/non-responders
    Mann-Whitney U test is a non-parametric statistical test used to compare two independent groups

    Args:
        filtered_table (pd.DataFrame): The filtered table with relative frequency information

    Returns:
        results_df (pd.DataFrame): DataFrame with population names and corresponding p-values
    """

    # get unique cell types
    cell_types = filtered_table["population"].unique()
    results = []
    for pop in cell_types:

        # get the relative percentage of the current population from the filtered table where response is yes/no
        yes_percentage = filtered_table[
            (filtered_table["population"] == pop)
            & (filtered_table["response"] == "yes")
        ]["percentage"]
        no_percentage = filtered_table[
            (filtered_table["population"] == pop) & (filtered_table["response"] == "no")
        ]["percentage"]

        # perform two-sided mann whitney u test to see if there is a significant difference between the responders/non-responders within the population
        _, p = mannwhitneyu(yes_percentage, no_percentage, alternative="two-sided")

        # save the population and corresponding p value
        results.append({"population": pop, "p_value": p})
    results_df = pd.DataFrame(results)
    results_df.to_csv("data/part3_stat_results.csv", index=False)
    return results_df


def significant_results(results_df: pd.DataFrame):
    """
    Print and save the populations that have significant differences in relative frequencies between responders and non-responders

    Args:
        results_df (pd.DataFrame): The population and associated p-value from the Mann-Whitney U test

    Returns:
        pd.DataFrame: DataFrame containing only the significant results
    """

    # get the populations and p values from the results dataframe where the p value is significant
    sig = results_df[results_df["p_value"] < 0.05]
    if not sig.empty:
        print("\nSignificant results found in: ")
        print(sig)
        # save significant results to CSV
        sig.to_csv("data/part3_significant_results.csv", index=False)
    else:
        print("\nNo significant differences found")

    return sig


if __name__ == "__main__":
    summary_path = "data/part2_summary_table.csv"
    db_path = "data/cell_info.db"

    # get summary and metadata dfs
    summary_df, metadata_df = load_data(summary_path, db_path)
    print(summary_df)
    print(metadata_df)

    # get the merged filtered table
    filtered_table = merge_filter_data(summary_df, metadata_df)
    print(filtered_table)

    # make the boxplots from the filtered tables
    plot_boxplots(filtered_table)

    # population and p values df from mann whitney u test
    results_df = statistical_tests(filtered_table)
    print(results_df)

    # rows from results_df with significant p-value
    significant_results(results_df)
