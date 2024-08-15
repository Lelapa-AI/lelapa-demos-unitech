#!/bin/bash

# Navigate to the correct directory
cd src/lelapa_demos_unitech

# Run the scraper to fetch and store data
python scraper.py

# Start the FastAPI application
exec pdm run start
