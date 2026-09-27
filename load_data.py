#!/usr/bin/env python3
import os
import sys
from src.database import DatabaseManager


def main():
    print("=" * 60)
    print("PART 1: Database Initialization and Data Loading")
    print("=" * 60)
    
    db_path = "clinical_trial.db"
    csv_path = "cell-count.csv"
    
    if not os.path.exists(csv_path):
        print(f"ERROR: {csv_path} not found!")
        sys.exit(1)
    
    if os.path.exists(db_path):
        print(f"\nRemoving existing database: {db_path}")
        os.remove(db_path)
    
    print(f"\n1. Initializing database: {db_path}")
    db = DatabaseManager(db_path)
    db.connect()
    
    print("   Creating schema...")
    db.create_schema()
    
    print(f"\n2. Loading data from {csv_path}")
    sample_count, cell_count = db.load_data_from_csv(csv_path)
    
    print("\n3. Verifying data load...")
    cursor = db.conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM samples")
    total_samples = cursor.fetchone()[0]
    print(f"   Samples table: {total_samples} records")
    cursor.execute("SELECT COUNT(*) FROM cell_counts")
    total_cell_counts = cursor.fetchone()[0]
    print(f"   Cell counts table: {total_cell_counts} records")
    cursor.execute("""
        SELECT s.sample_id, s.condition, s.treatment, s.response, 
               cc.population, cc.count
        FROM samples s
        JOIN cell_counts cc ON s.sample_id = cc.sample_id
        WHERE s.sample_id = 'sample00000'
        ORDER BY cc.population
    """)
    print("\n   Sample data (sample00000):")
    for row in cursor.fetchall():
        sample_id, condition, treatment, response, population, count = row
        print(f"      {population}: {count} cells")
    cursor.execute("""
        SELECT condition, COUNT(*) as count
        FROM samples
        GROUP BY condition
        ORDER BY count DESC
    """)
    print("\n   Samples by condition:")
    for row in cursor.fetchall():
        print(f"      {row[0]}: {row[1]} samples")
    cursor.execute("""
        SELECT treatment, COUNT(*) as count
        FROM samples
        GROUP BY treatment
        ORDER BY count DESC
    """)
    print("\n   Samples by treatment:")
    for row in cursor.fetchall():
        print(f"      {row[0]}: {row[1]} samples")
    db.close()
    
    print("\n" + "=" * 60)
    print(f"Database file: {os.path.abspath(db_path)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
