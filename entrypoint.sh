#!/bin/bash

# Navigate to the correct directory
cd src/lelapa_demos_unitech

# Run the scraper to fetch and store data
python data.py

# Start the FastAPI application
exec pdm run start --host 0.0.0.0
