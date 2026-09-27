#!/usr/bin/env python3
import os
from src.database import DatabaseManager
from src.analysis import (
    calculate_cell_frequencies,
    compare_responders_vs_nonresponders,
    analyze_baseline_subset
)
from src.visualization import plot_responder_comparison_boxplot

def main():
    print("=" * 60)
    print("ANALYSIS PIPELINE: Parts 2-4")
    print("=" * 60)
    
    db_path = "clinical_trial.db"
    
    print(f"\nConnecting to database: {db_path}")
    db = DatabaseManager(db_path)
    conn = db.connect()
    
    print("\n" + "=" * 60)
    print("PART 2: Calculating Cell Type Frequencies")
    print("=" * 60)
    
    freq_df = calculate_cell_frequencies(conn)
    print(f"Calculated frequencies for {len(freq_df)} records")
    
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cell_frequencies")
    
    for _, row in freq_df.iterrows():
        cursor.execute("""
            INSERT INTO cell_frequencies (sample, total_count, population, count, percentage)
            VALUES (?, ?, ?, ?, ?)
        """, (row['sample'], row['total_count'], row['population'], row['count'], row['percentage']))
    
    conn.commit()
    
    print("\nSample frequencies (first sample):")
    sample_freq = freq_df[freq_df['sample'] == 'sample00000'].sort_values('population')
    for _, row in sample_freq.iterrows():
        print(f"  {row['population']}: {row['count']} ({row['percentage']:.2f}%)")
    
    
    print("\n" + "=" * 60)
    print("PART 3: Statistical Analysis - Responders vs Non-Responders")
    print("=" * 60)
    print("Filters: Melanoma, Miraclib, PBMC")
    
    comparison_df, stats_results = compare_responders_vs_nonresponders(conn)
    
    print(f"\nTotal samples analyzed: {comparison_df['sample'].nunique()}")
    print(f"  Responders: {comparison_df[comparison_df['response']=='yes']['sample'].nunique()}")
    print(f"  Non-responders: {comparison_df[comparison_df['response']=='no']['sample'].nunique()}")
    
    print("\nStatistical Test Results (Mann-Whitney U test):")
    print("-" * 80)
    
    significant_populations = []
    
    for population, results in sorted(stats_results.items()):
        sig_marker = "***" if results['is_significant'] else ""
        print(f"\n{population.replace('_', ' ').title()}: {sig_marker}")
        print(f"  Responders:     mean={results['responders_mean']:.2f}%, median={results['responders_median']:.2f}%, n={results['responders_n']}")
        print(f"  Non-responders: mean={results['non_responders_mean']:.2f}%, median={results['non_responders_median']:.2f}%, n={results['non_responders_n']}")
        print(f"  U-statistic: {results['statistic']:.2f}, p-value: {results['p_value']:.4f}")
        
        if results['is_significant']:
            significant_populations.append(population)
    
    cursor = conn.cursor()
    cursor.execute("DELETE FROM statistical_results")
    
    for population, results in stats_results.items():
        cursor.execute("""
            INSERT INTO statistical_results 
            (population, test_name, statistic, p_value, is_significant, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            population,
            results['test_name'],
            results['statistic'],
            results['p_value'],
            1 if results['is_significant'] else 0,
            f"Responders: {results['responders_n']}, Non-responders: {results['non_responders_n']}"
        ))
    
    conn.commit()
    
    print("\n" + "-" * 80)
    print("Generating boxplot visualization...")
    
    os.makedirs("outputs", exist_ok=True)
    fig = plot_responder_comparison_boxplot(comparison_df, save_path="outputs/responder_comparison_boxplot.png")
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    if significant_populations:
        print(f"\nSignificant populations (p < 0.05): {len(significant_populations)}")
        for pop in significant_populations:
            print(f"  - {pop.replace('_', ' ').title()}")
    else:
        print("\nNo significant differences found at p < 0.05")
    
    
    print("\n" + "=" * 60)
    print("PART 4: Baseline Subset Analysis")
    print("=" * 60)
    print("Filters: Melanoma, PBMC, Miraclib, Baseline (time=0)")
    
    subset_results, subset_df = analyze_baseline_subset(conn)
    
    print(f"\nTotal baseline samples: {subset_results['total_samples']}")
    print(f"Total unique subjects: {subset_results['total_subjects']}")
    
    print("\n1. Samples by Project:")
    for project, count in sorted(subset_results['samples_by_project'].items()):
        print(f"   {project}: {count} samples")
    
    print("\n2. Subjects by Response:")
    for response, count in sorted(subset_results['subjects_by_response'].items()):
        response_label = "Responders" if response == 'yes' else "Non-responders"
        print(f"   {response_label}: {count} subjects")
    
    print("\n3. Subjects by Gender:")
    for gender, count in sorted(subset_results['subjects_by_gender'].items()):
        gender_label = "Male" if gender == 'M' else "Female"
        print(f"   {gender_label}: {count} subjects")
    
    print("\n4. Additional Breakdowns:")
    print(f"   Samples by response:")
    for response, count in sorted(subset_results['samples_by_response'].items()):
        response_label = "Responders" if response == 'yes' else "Non-responders"
        print(f"     {response_label}: {count} samples")
    
    print(f"   Samples by gender:")
    for gender, count in sorted(subset_results['samples_by_gender'].items()):
        gender_label = "Male" if gender == 'M' else "Female"
        print(f"     {gender_label}: {count} samples")
    
    
    db.close()
    
    print("\n" + "=" * 60)
    print("Analysis pipeline complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
