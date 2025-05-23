import os
import yaml
from pathlib import Path

def load_states():
    with open('_data/states.yml', 'r') as f:
        return yaml.safe_load(f)

def generate_state_page(year, state):
    template = f"""---
layout: census_data
title: {state['name']} Census Data - {year}
year: {year}
state: {state['abbr']}
---

# {state['name']} Census Data - {year}

## Overview
This page provides access to manufacturing census data for {state['name']} in {year}.

## Data Access
The data for {state['name']} in {year} is available in the following formats:

- [Raw Data]({{ site.baseurl }}/clean-data/{year}/{state['abbr'].lower()}/)
- [Processed Data]({{ site.baseurl }}/clean-data/{year}/{state['abbr'].lower()}/processed/)

## Historical Context
The {year} census provides detailed manufacturing statistics for {state['name']}, offering insights into the state's industrial development during this period.
"""
    
    # Create directory if it doesn't exist
    os.makedirs(f'_census_data/{year}', exist_ok=True)
    
    # Write the file
    with open(f'_census_data/{year}/{state["abbr"].lower()}.md', 'w') as f:
        f.write(template)

def main():
    states = load_states()
    year = '1850'
    
    for state in states:
        generate_state_page(year, state)
        print(f"Generated page for {state['name']}")

if __name__ == '__main__':
    main() 