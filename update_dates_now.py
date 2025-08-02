#!/usr/bin/env python3
"""
Simple script to update GUIDE_CITIES dates immediately
Run this script to update the dates to the next Monday
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from src.scripts.datahi import (
        get_next_monday_date, 
        update_guide_cities_dates,
        GUIDE_CITIES
    )
    
    print("Pharmacy Data Scraper - Date Update")
    print("=" * 40)
    print()
    
    # Show current state
    print("Current GUIDE_CITIES:")
    for city in GUIDE_CITIES:
        print(f"  - {city}")
    print()
    
    # Show next Monday's date
    next_monday = get_next_monday_date()
    print(f"Next Monday's date: {next_monday}")
    print()
    
    # Update dates
    print("Updating dates...")
    update_guide_cities_dates()
    print("✅ Dates updated successfully!")
    print()
    
    # Show updated state
    print("Updated GUIDE_CITIES:")
    for city in GUIDE_CITIES:
        print(f"  - {city}")
    print()
    
    print("The dates have been updated to the next Monday.")
    print("You can run this script again next Monday to update to the following Monday.")
    
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you have the required dependencies installed:")
    print("  pip install requests beautifulsoup4 pytz")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
