import pandas as pd
import sqlite3

# part 4: perform queries/filtering to extract subsets of the data to understand early treatment effects


def get_baseline_melanoma_miraclib_data(db_path: str):
    """
    Get all melanoma PBMC samples at baseline from miraclib-treated patients

    Args:
        db_path (str): Path to database to retrieve the metadata table

    Returns:
        baseline_df (pd.DataFrame): DataFrame that joins the cell_counts and metadata tables, and contains
        baseline melanoma PBMC samples from patients treated with miraclib
    """
    conn = sqlite3.connect(db_path)

    # join cell_counts and metadata on sample_id, and filter the data using a sql query
    query = """
    SELECT *
    FROM cell_counts cc
    JOIN metadata m ON cc.sample_id = m.sample_id
    WHERE m.condition = 'melanoma'
    AND m.treatment = 'miraclib'
    AND m.time_from_treatment_start = 0
    AND m.sample_type = 'PBMC'
    """

    baseline_df = pd.read_sql_query(query, conn)
    conn.close()
    return baseline_df


def analyze_data_subset(baseline_df: pd.DataFrame):
    """
    Analyze the filtered data to get the required counts and save results

    Args:
        baseline_df (pd.DataFrame): DataFrame with baseline data

    Returns:
        tuple: (project_counts, response_counts, sex_counts) - DataFrames with the analysis results
    """

    # 1. number of samples from each project
    print("\n1. Number of samples from each project:")
    project_counts = baseline_df["project"].value_counts().sort_index()
    for project, count in project_counts.items():
        print(f"{project}: {count} samples")

    # convert to DataFrame and save
    project_counts_df = project_counts.reset_index()
    project_counts_df.columns = ["project", "sample_count"]
    project_counts_df.to_csv("data/part4_project_counts.csv", index=False)

    # 2. number of subjects that are responders and non-responders
    print("\n2. Number of subjects that are responders/non-responders:")

    # nunique counts the number of unique subjects per response (ensures there are no duplicates)
    response_counts = baseline_df.groupby("response")["subject"].nunique()
    print(f"Responders (yes): {response_counts["yes"]} subjects")
    print(f"Non-responders (no): {response_counts["no"]} subjects")

    # convert to DataFrame and save
    response_counts_df = response_counts.reset_index()
    response_counts_df.columns = ["response", "subject_count"]
    response_counts_df.to_csv("data/part4_response_counts.csv", index=False)

    # 3. number of subjects that are male and female
    print("\n3. Number of subjects that are male and female:")
    sex_counts = baseline_df.groupby("sex")["subject"].nunique()
    print(f"Males (M): {sex_counts["M"]} subjects")
    print(f"Females (F): {sex_counts["F"]} subjects")

    # convert to DataFrame and save
    sex_counts_df = sex_counts.reset_index()
    sex_counts_df.columns = ["sex", "subject_count"]
    sex_counts_df.to_csv("data/part4_sex_counts.csv", index=False)

    return project_counts_df, response_counts_df, sex_counts_df


if __name__ == "__main__":
    db_path = "data/cell_info.db"

    # extract the baseline df
    baseline_df = get_baseline_melanoma_miraclib_data(db_path)
    print(baseline_df)

    # perform the data subset analysis
    analyze_data_subset(baseline_df)
