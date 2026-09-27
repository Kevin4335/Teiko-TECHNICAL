import sqlite3
from typing import Optional
import pandas as pd


class DatabaseManager:
    def __init__(self, db_path: str = "clinical_trial.db"):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
    
    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        return self.conn
    
    def close(self):
        if self.conn:
            self.conn.close()
    
    def create_schema(self):
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS samples (
                sample_id TEXT PRIMARY KEY,
                project TEXT NOT NULL,
                subject TEXT NOT NULL,
                condition TEXT NOT NULL,
                age INTEGER,
                sex TEXT,
                treatment TEXT NOT NULL,
                response TEXT,
                sample_type TEXT NOT NULL,
                time_from_treatment_start INTEGER NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cell_counts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sample_id TEXT NOT NULL,
                population TEXT NOT NULL,
                count INTEGER NOT NULL,
                FOREIGN KEY (sample_id) REFERENCES samples(sample_id),
                UNIQUE(sample_id, population)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cell_frequencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sample TEXT NOT NULL,
                total_count INTEGER NOT NULL,
                population TEXT NOT NULL,
                count INTEGER NOT NULL,
                percentage REAL NOT NULL,
                FOREIGN KEY (sample) REFERENCES samples(sample_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS statistical_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                population TEXT NOT NULL,
                test_name TEXT NOT NULL,
                statistic REAL,
                p_value REAL,
                is_significant INTEGER,
                alpha REAL DEFAULT 0.05,
                notes TEXT
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_samples_condition 
            ON samples(condition)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_samples_treatment 
            ON samples(treatment)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_samples_sample_type 
            ON samples(sample_type)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_samples_response 
            ON samples(response)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_cell_counts_sample 
            ON cell_counts(sample_id)
        """)
        
        self.conn.commit()
    
    def load_data_from_csv(self, csv_path: str):
        df = pd.read_csv(csv_path)
        
        print(f"   Loaded {len(df)} rows from CSV")
        
        cursor = self.conn.cursor()
        cell_populations = ['b_cell', 'cd8_t_cell', 'cd4_t_cell', 'nk_cell', 'monocyte']
        rows_inserted = 0
        for idx, row in df.iterrows():
            cursor.execute("""
                INSERT OR REPLACE INTO samples 
                (sample_id, project, subject, condition, age, sex, treatment, 
                 response, sample_type, time_from_treatment_start)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row['sample'],
                row['project'],
                row['subject'],
                row['condition'],
                row['age'],
                row['sex'],
                row['treatment'],
                row['response'],
                row['sample_type'],
                row['time_from_treatment_start']
            ))
            
            for population in cell_populations:
                cursor.execute("""
                    INSERT OR REPLACE INTO cell_counts (sample_id, population, count)
                    VALUES (?, ?, ?)
                """, (row['sample'], population, row[population]))
            
            rows_inserted += 1
            if rows_inserted % 1000 == 0:
                self.conn.commit()
                print(f"   Inserted {rows_inserted} samples...")
        
        self.conn.commit()
        print(f"   Total samples inserted: {rows_inserted}")
        
        cursor.execute("SELECT COUNT(*) FROM samples")
        sample_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM cell_counts")
        cell_count = cursor.fetchone()[0]
        
        print(f"   Verification: {sample_count} samples, {cell_count} cell count records")
        
        return sample_count, cell_count

