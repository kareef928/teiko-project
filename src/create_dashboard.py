import streamlit as st
import pandas as pd
import plotly.express as px

# set page config
st.set_page_config(page_title="Clinical Trial Analysis Dashboard", layout="wide")

# main title
st.title("Clinical Trial Analysis Dashboard")
st.markdown("---")

# sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox(
    "Select Part:",
    [
        "Part 1: Data Management",
        "Part 2: Initial Analysis",
        "Part 3: Statistical Analysis",
        "Part 4: Subset Analysis",
    ],
)

# part 1: data management
if page == "Part 1: Data Management":
    st.header("Part 1: Data Management")
    st.write(
        "In this section we create a SQLite database and extract a CSV containing counts of different cell populations as well as metadata about the samples. "
        "We design a relational database schema with two tables: one containing information of just the cell counts across the populations, and the other "
        "being the metadata for the samples. We do this to facilitate downstream analysis and avoid redundant loading of unnecessary columns. "
        "Below, we show the database schema for both tables, along with sample data from each table to verify the data loading process. "
    )

    # load and display database info
    try:
        import sqlite3

        conn = sqlite3.connect("data/cell_info.db")

        # show table schemas
        st.subheader("Database Schema")
        tables = pd.read_sql_query(
            "SELECT name FROM sqlite_master WHERE type='table'", conn
        )

        # display info about the columns in each table
        for table in tables["name"]:
            with st.expander(f"Table: {table}"):
                schema = pd.read_sql_query(f"PRAGMA table_info({table})", conn)
                st.dataframe(schema)

        # show sample data
        st.subheader("Sample Data")
        col1, col2 = st.columns(2)

        # show cell counts
        with col1:
            st.write("Cell Counts (first 5 rows):")
            cell_counts = pd.read_sql_query("SELECT * FROM cell_counts LIMIT 5", conn)
            st.dataframe(cell_counts)

        with col2:
            st.write("Metadata (first 5 rows):")
            metadata = pd.read_sql_query("SELECT * FROM metadata LIMIT 5", conn)
            st.dataframe(metadata)

        conn.close()

    except Exception as e:
        st.error(f"Error loading database: {e}")

# part 2: initial analysis
elif page == "Part 2: Initial Analysis":
    st.header("Part 2: Initial Analysis")
    st.write(
        "In this section we take the cell counts table and generate a new summary table that calculates the relative "
        "frequency of each population in each sample. To do this, for each sample, we generate a total count of all "
        "the populations for that sample and calculate the count of a particular population over the total count * 100 "
        "to get the relative percentage for that population in that sample. Below, we show statistics regarding the summary "
        "table, as well as several rows of the summary table itself and details regarding the distribution of counts for each population. "
    )

    try:
        # load summary table
        summary_df = pd.read_csv("data/part2_summary_table.csv")

        # display summary statistics
        st.subheader(
            "Summary Statistics of Relative Frequencies of Immune Cell Populations"
        )
        col1, col2 = st.columns(2)

        # show the number of samples and populations
        with col1:
            st.metric("Total Samples", len(summary_df["sample"].unique()))
            st.metric("Total Populations", len(summary_df["population"].unique()))

        # show the most and least common cell populations
        with col2:
            most_common = summary_df.groupby("population")["percentage"].mean().idxmax()
            most_common_value = (
                summary_df.groupby("population")["percentage"].mean().max()
            )
            st.metric(
                "Most Abundant Cell Population across all Samples",
                f"{most_common}: {most_common_value:.2f}%",
            )

            least_common = (
                summary_df.groupby("population")["percentage"].mean().idxmin()
            )
            least_common_value = (
                summary_df.groupby("population")["percentage"].mean().min()
            )
            st.metric(
                "Least Abundant Cell Population across all Samples",
                f"{least_common}: {least_common_value:.2f}%",
            )

        # show sample data
        st.subheader("Sample Data from Summary Statistics")
        st.dataframe(summary_df.head(10))

        # show distribution of relative percentage per each population
        st.subheader("Distribution of Relative Percentage for each Population")
        pop_percentage_stats = (
            summary_df.groupby("population")["percentage"]
            .agg(["mean", "std", "count"])
            .round(2)
        )
        st.dataframe(pop_percentage_stats)

    except Exception as e:
        st.error(f"Error loading Part 2 data: {e}")

# part 3: statistical analysis
elif page == "Part 3: Statistical Analysis":
    st.header("Part 3: Statistical Analysis")
    st.write(
        "In this section we perform statistical analysis to determine if there are significant differences in immune cell population frequencies "
        "between patients who respond to treatment and those who do not. We use Mann-Whitney U tests, which are non-parametric statistical tests "
        "used to compare two independent groups. We filter the data to focus on melanoma patients treated with miraclib who have PBMC samples. "
        "Below, we display boxplots showing the distribution of cell populations by response status, along with statistical test results and "
        "the populations with significant differences between responders and non-responders."
    )

    try:
        # display the boxplot
        st.subheader("Boxplot: Cell Population Frequencies by Response")
        st.image("data/part3_boxplot.png", use_container_width=True)

        # display statistical results
        st.subheader("Statistical Results")
        col1, col2 = st.columns(2)

        with col1:
            st.write("All Test Results:")
            all_results = pd.read_csv("data/part3_stat_results.csv")
            st.dataframe(all_results)

        with col2:
            st.write("Significant Results (p < 0.05):")
            try:
                sig_results = pd.read_csv("data/part3_significant_results.csv")
                if not sig_results.empty:
                    st.dataframe(sig_results)
                else:
                    st.info("No significant differences found")
            except:
                st.info("No significant results file found")

    except Exception as e:
        st.error(f"Error loading Part 3 data: {e}")

# part 4: subset analysis
elif page == "Part 4: Subset Analysis":
    st.header("Part 4: Subset Analysis")
    st.write(
        "In this section we perform different analyses of a specific subset of our data: melanoma patients treated with miraclib who have PBMC samples "
        "collected at baseline (time from treatment start = 0). We query the database to extract this subset and analyze the distribution of samples "
        "across different projects, response status, and demographic characteristics. This analysis helps us understand the baseline "
        "characteristics of our study population and provides insights into the composition of our clinical trial cohort. "
        "Below, we display summary statistics including sample counts by project, subject counts by response status, and demographic distributions."
    )

    try:
        # load the three query results
        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("1. Samples by Project")
            project_counts = pd.read_csv("data/part4_project_counts.csv")

            # rename project names for better display
            project_counts["project"] = project_counts["project"].replace(
                {"prj1": "Project 1", "prj3": "Project 3"}
            )

            st.dataframe(project_counts)

            # create pie chart
            fig = px.pie(
                project_counts,
                values="sample_count",
                names="project",
                title="Samples by Project",
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("2. Subjects by Response")
            response_counts = pd.read_csv("data/part4_response_counts.csv")
            st.dataframe(response_counts)

            # create pie chart
            fig = px.pie(
                response_counts,
                values="subject_count",
                names="response",
                title="Subjects by Response Status",
            )
            st.plotly_chart(fig, use_container_width=True)

        with col3:
            st.subheader("3. Subjects by Sex")
            sex_counts = pd.read_csv("data/part4_sex_counts.csv")
            st.dataframe(sex_counts)

            # create pie chart
            fig = px.pie(
                sex_counts, values="subject_count", names="sex", title="Subjects by Sex"
            )
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error loading Part 4 data: {e}")

# footer
st.markdown("---")
