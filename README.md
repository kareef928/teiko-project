# Clinical Trial Immune Cell Analysis

This repository contains an analysis pipeline for clinical trial data involving immune cell populations and treatment response, including a 4-part analysis workflow and Streamlit dashboard.

## Live Dashboard

**Access the interactive dashboard here:** [Clinical Trial Analysis Dashboard](https://kareef928-teiko-project-srccreate-dashboard-kv7nw9.streamlit.app/)

## Project Overview

1. **Data Management** - Database schema design and data loading
2. **Initial Analysis** - Relative frequency calculations
3. **Statistical Analysis** - Mann-Whitney U tests comparing responders vs non-responders
4. **Subset Analysis** - Baseline sample analysis

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/kareef928/teiko-project.git
   cd teiko-project
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv teiko-proj
   source teiko-proj/bin/activate  # On Windows: teiko-proj\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the analysis pipeline**
   ```bash
   # Part 1: Data Management
   python src/part1_data_processing.py
   
   # Part 2: Initial Analysis
   python src/part2_initial_analysis.py
   
   # Part 3: Statistical Analysis
   python src/part3_statistical_analysis.py
   
   # Part 4: Subset Analysis
   python src/part4_subset_analysis.py
   ```

5. **Launch the dashboard**
   ```bash
   streamlit run src/create_dashboard.py
   ```

## Database Schema Design

### Schema Overview

The project uses a relational SQLite database with two main tables:

#### `cell_counts` Table
```sql
CREATE TABLE cell_counts (
    sample_id TEXT PRIMARY KEY,
    b_cell INTEGER,
    cd8_t_cell INTEGER,
    cd4_t_cell INTEGER,
    nk_cell INTEGER,
    monocyte INTEGER
);
```

#### `metadata` Table
```sql
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
);
```

### Design Rationale

1. **Separation of Concerns**
   - `cell_counts`: The count data for each cell population
   - `metadata`: The clinical and experimental metadata
   - This separation allows for efficient querying and avoids data redundancy

2. **Primary Key Design**
   - `sample_id` as primary key in both tables allows for efficient joins
   - Supports one-to-one relationships between the counts and metadata tables

### Scaling for Larger Data

For larger-scale deployment with hundreds of projects, thousands of samples, and various types of analytics:

1. **Database Optimization**
   - Add indexes on frequently queried columns (project, treatment, response) to speed up database searches
   - Implement table partitioning by project or time period for faster queries
   - Consider using PostgreSQL which handles larger datasets better than SQLite

2. **Performance Enhancements**
   - Implement caching for frequently accessed data to avoid recalculating the same results
   - Add data archiving strategies for old projects to separate storage
   - Keep only recent/active data in main database to maintain fast query performance

3. **Analytics Scalability**
   - The current schema supports various analytics: statistical testing, machine learning applications, etc
   - The normalized structure allows for easy extension to include additional cell populations or clinical parameters

## Code Structure

### File Organization
```
teiko-project/                  
├── README.md
├── data
│   ├── cell-count.csv
│   ├── cell_info.db
│   ├── part2_summary_table.csv
│   ├── part3_boxplot.png
│   ├── part3_significant_results.csv
│   ├── part3_stat_results.csv
│   ├── part4_project_counts.csv
│   ├── part4_response_counts.csv
│   └── part4_sex_counts.csv
├── requirements.txt
└── src
    ├── create_dashboard.py
    ├── part1_data_processing.py
    ├── part2_initial_analysis.py
    ├── part3_statistical_analysis.py
    └── part4_subset_analysis.py
```

### Design Motivation

1. Modular Architecture
   - Each analysis part is contained in a separate file for easy maintenance
   - Enables independent testing and modification of each component

2. Data Pipeline Approach
   - Sequential processing with clear data flow: raw CSV → database → summary table → statistical results
   - Each step saves intermediate outputs (e.g., part2_summary_table.csv, part3_boxplot.png)
   - All intermediate files are saved, making debugging and verification easier

3. Separation of Analysis and Visualization
   - Analysis scripts (parts 1-4) focus on computation and save results to the data folder
   - Dashboard (create_dashboard.py) focuses on presentation by loading and displaying saved results
   - Allows for multiple visualization approaches: same data can be displayed in different ways

## Analysis Workflow

### Part 1: Data Management
- Creates SQLite database with two tables: cell_counts (sample_id, cell populations) and metadata (sample_id, clinical info)
- Loads CSV data into tables with proper primary key (sample_id)
- Verifies data loading by testing joins between tables and checking for duplicates

### Part 2: Initial Analysis
- Calculates relative frequencies: (cell_count / total_cells) * 100 for each population per sample
- Creates summary table (part2_summary_table.csv) with sample, population, and percentage columns

### Part 3: Statistical Analysis
- Performs Mann-Whitney U tests comparing cell population frequencies between responders (yes) and non-responders (no)
- Filters data to melanoma patients treated with miraclib who have PBMC samples
- Identifies significant differences (p < 0.05) and saves results

### Part 4: Subset Analysis
- Queries baseline samples (time_from_treatment_start = 0) from melanoma patients treated with miraclib who have PBMC samples
- Analyzes sample distribution: counts by project, response status, and sex




