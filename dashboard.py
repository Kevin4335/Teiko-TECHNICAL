#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import os
from src.database import DatabaseManager
from src.analysis import analyze_baseline_subset

st.set_page_config(page_title="Clinical Trial Analysis", page_icon="🧬", layout="wide")

def main():
    st.title("Clinical Trial Analysis")
    st.markdown("### Immune Cell Population Study")
    
    db_path = "clinical_trial.db"
    if not os.path.exists(db_path):
        st.error("Database not found! Run `make pipeline` first.")
        return
    
    db = DatabaseManager(db_path)
    conn = db.connect()
    
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("", ["Part 2: Frequencies", "Part 3: Statistics", "Part 4: Subset"])
    
    if page == "Part 2: Frequencies":
        show_part2(conn)
    elif page == "Part 3: Statistics":
        show_part3(conn)
    elif page == "Part 4: Subset":
        show_part4(conn)
    
    db.close()


def show_part2(conn):
    st.header("Part 2: Cell Frequencies")
    query = """
        SELECT 
            sample,
            total_count,
            population,
            count,
            ROUND(percentage, 2) as percentage
        FROM cell_frequencies
        ORDER BY sample, population
    """
    df = pd.read_sql_query(query, conn)
    if len(df) == 0:
        st.warning("No data found.")
        return
    
    st.write(f"{len(df):,} records")
    summary = df.groupby('population')['percentage'].agg(['mean', 'median']).round(2)
    summary.index = summary.index.map(lambda x: x.replace('_', ' ').title())
    st.dataframe(summary)
    st.dataframe(df.head(50), height=400)

def show_part3(conn):
    st.header("Part 3: Statistical Analysis")
    st.caption("Melanoma, Miraclib, PBMC")
    
    comparison_df = pd.read_sql_query("""
        SELECT 
            cf.sample,
            cf.population,
            cf.percentage,
            s.response
        FROM cell_frequencies cf
        JOIN samples s ON cf.sample = s.sample_id
        WHERE s.condition = 'melanoma'
          AND s.treatment = 'miraclib'
          AND s.sample_type = 'PBMC'
          AND s.response IN ('yes', 'no')
    """, conn)
    stats_df = pd.read_sql_query("""
        SELECT 
            population,
            test_name,
            ROUND(statistic, 2) as statistic,
            ROUND(p_value, 4) as p_value,
            is_significant
        FROM statistical_results
        ORDER BY p_value
    """, conn)
    
    stats_display = stats_df.copy()
    stats_display['population'] = stats_display['population'].map(lambda x: x.replace('_', ' ').title())
    stats_display['Significant'] = stats_display['is_significant'].map(lambda x: '✓' if x == 1 else '')
    stats_display = stats_display[['population', 'p_value', 'Significant']]
    stats_display.columns = ['Population', 'P-Value', 'Sig']
    
    st.dataframe(stats_display, hide_index=True)
    
    significant = stats_display[stats_display['Sig'] == '✓']
    if len(significant) > 0:
        st.success(f"Significant: {', '.join(significant['Population'])}")
    
    plot_path = "outputs/responder_comparison_boxplot.png"
    if os.path.exists(plot_path):
        st.image(plot_path)

def show_part4(conn):
    st.header("Part 4: Baseline Subset")
    st.caption("Melanoma, PBMC, Miraclib, time=0")
    
    results, subset_df = analyze_baseline_subset(conn)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Samples", results['total_samples'])
    with col2:
        st.metric("Total Subjects", results['total_subjects'])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("**By Project**")
        st.write(pd.DataFrame(list(results['samples_by_project'].items()), columns=['Project', 'Count']))
    with col2:
        st.write("**By Response**")
        response_df = pd.DataFrame(list(results['subjects_by_response'].items()), columns=['Response', 'Count'])
        response_df['Response'] = response_df['Response'].map({'yes': 'Responders', 'no': 'Non-responders'})
        st.write(response_df)
    with col3:
        st.write("**By Gender**")
        gender_df = pd.DataFrame(list(results['subjects_by_gender'].items()), columns=['Gender', 'Count'])
        gender_df['Gender'] = gender_df['Gender'].map({'M': 'Male', 'F': 'Female'})
        st.write(gender_df)

if __name__ == "__main__":
    main()
