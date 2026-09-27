.PHONY: setup pipeline dashboard clean

# Install all dependencies
setup:
	@echo "Installing dependencies..."
	python -m pip install -r requirements.txt
	@echo "Setup complete!"

# Run the complete data pipeline
pipeline:
	@echo "Running data pipeline..."
	@echo "Step 1: Loading data into database..."
	python load_data.py
	@echo "Step 2: Running analysis..."
	python run_analysis.py
	@echo "Pipeline complete!"

# Start the dashboard server
dashboard:
	@echo "Starting dashboard..."
	@echo "Dashboard will be available at http://localhost:8501"
	streamlit run dashboard.py

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	rm -f *.db *.sqlite *.sqlite3
	rm -rf __pycache__
	rm -rf outputs/
	@echo "Clean complete!"
