import pandas as pd
from scipy import stats
from typing import Dict, Tuple


def calculate_cell_frequencies(conn) -> pd.DataFrame:
    query = """
        SELECT sample_id, population, count
        FROM cell_counts
        ORDER BY sample_id, population
    """
    df = pd.read_sql_query(query, conn)
    totals = df.groupby('sample_id')['count'].sum().reset_index()
    totals.columns = ['sample', 'total_count']
    df = df.rename(columns={'sample_id': 'sample'})
    df = df.merge(totals, on='sample')
    df['percentage'] = (df['count'] / df['total_count']) * 100
    df = df[['sample', 'total_count', 'population', 'count', 'percentage']]
    return df


def compare_responders_vs_nonresponders(conn) -> Tuple[pd.DataFrame, Dict]:
    query = """
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
    """
    df = pd.read_sql_query(query, conn)
    populations = df['population'].unique()
    statistical_results = {}
    
    for population in populations:
        pop_data = df[df['population'] == population]
        responders = pop_data[pop_data['response'] == 'yes']['percentage']
        non_responders = pop_data[pop_data['response'] == 'no']['percentage']
        statistic, p_value = stats.mannwhitneyu(responders, non_responders, alternative='two-sided')
        
        statistical_results[population] = {
            'test_name': 'Mann-Whitney U',
            'statistic': statistic,
            'p_value': p_value,
            'is_significant': p_value < 0.05,
            'responders_mean': responders.mean(),
            'responders_median': responders.median(),
            'responders_std': responders.std(),
            'responders_n': len(responders),
            'non_responders_mean': non_responders.mean(),
            'non_responders_median': non_responders.median(),
            'non_responders_std': non_responders.std(),
            'non_responders_n': len(non_responders)
        }
    
    return df, statistical_results


def analyze_baseline_subset(conn) -> Dict:
    query = """
        SELECT 
            sample_id,
            project,
            subject,
            sex,
            response
        FROM samples
        WHERE condition = 'melanoma'
          AND sample_type = 'PBMC'
          AND treatment = 'miraclib'
          AND time_from_treatment_start = 0
    """
    df = pd.read_sql_query(query, conn)
    results = {
        'total_samples': len(df),
        'total_subjects': df['subject'].nunique(),
        'samples_by_project': df.groupby('project').size().to_dict(),
        'subjects_by_response': df.groupby('response')['subject'].nunique().to_dict(),
        'subjects_by_gender': df.groupby('sex')['subject'].nunique().to_dict(),
        'samples_by_response': df.groupby('response').size().to_dict(),
        'samples_by_gender': df.groupby('sex').size().to_dict()
    }
    
    return results, df
