#!/usr/bin/env python3
"""
Generate Jekyll pages from the database.
Creates both year index pages and state pages based on actual database content.
"""

import os
import sqlite3
import yaml
from pathlib import Path


def load_states():
    """Load state data from _data/states.yml"""
    with open('_data/states.yml', 'r') as f:
        return {state['abbr']: state for state in yaml.safe_load(f)}


def get_database_stats():
    """Get statistics from the database"""
    conn = sqlite3.connect('dropbox_links.db')
    cursor = conn.cursor()
    
    # Get all years and states in the database
    cursor.execute('SELECT DISTINCT year FROM dropbox_files ORDER BY year')
    years = [row[0] for row in cursor.fetchall()]
    
    stats = {}
    for year in years:
        cursor.execute('''
            SELECT state, COUNT(*) as link_count 
            FROM dropbox_files 
            WHERE year = ? 
            GROUP BY state 
            ORDER BY state
        ''', (year,))
        stats[year] = dict(cursor.fetchall())
    
    conn.close()
    return years, stats


def generate_year_index_page(year, states_with_data, state_lookup):
    """Generate the main index page for a year"""
    
    # Filter states to only those with data
    available_states = []
    for state_abbr in sorted(states_with_data.keys()):
        if state_abbr in state_lookup:
            state_info = state_lookup[state_abbr].copy()
            state_info['link_count'] = states_with_data[state_abbr]
            available_states.append(state_info)
    
    # Create front matter with available states data
    front_matter = {
        'layout': 'default',
        'permalink': f'/{year}/',
        'title': f'{year} Census Data',
        'census_year': year,
        'available_states': available_states
    }
    
    # Build content with proper Jekyll template syntax
    content = f"""# {year} Census Data

## Overview
This page provides access to manufacturing census data for all states in {year}.

## Available States
The following states have data available for {year}:

<div class="row">
""" + "{% for state in page.available_states %}" + f"""
  <div class="col-md-3 col-sm-4 col-6 mb-3">
    <div class="card h-100">
      <div class="card-body">
        <h5 class="card-title">""" + "{{ state.name }}" + """</h5>
        <p class="card-text">""" + "{{ state.link_count }}" + """ images</p>
        <a href=""" + f"\"{{{{ site.baseurl }}}}/census_data/{year}/{{{{ state.abbr | downcase }}}}.html\"" + """ class="btn btn-primary">View Data</a>
      </div>
    </div>
  </div>
""" + "{% endfor %}" + f"""
</div>

## Historical Context
The {year} census provides detailed manufacturing statistics, offering insights into America's industrial development during this period.
"""
    
    # Write file with proper YAML front matter
    with open(f'{year}.md', 'w') as f:
        f.write('---\n')
        yaml.dump(front_matter, f, default_flow_style=False)
        f.write('---\n\n')
        f.write(content)


def generate_state_page(year, state_abbr, link_count, state_lookup):
    """Generate a state page for a specific year"""
    
    if state_abbr not in state_lookup:
        print(f"Warning: State {state_abbr} not found in states.yml")
        state_name = state_abbr  # fallback
    else:
        state_name = state_lookup[state_abbr]['name']
    
    # Get actual links from database
    conn = sqlite3.connect('dropbox_links.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT filename, dropbox_url 
        FROM dropbox_files 
        WHERE state = ? AND year = ?
        ORDER BY filename
    ''', (state_abbr, year))
    links = cursor.fetchall()
    conn.close()
    
    # Create front matter (keep links separate to avoid YAML issues)
    front_matter = {
        'layout': 'census_data',
        'title': f'{state_name} Census Data - {year}',
        'census_year': year,
        'state': state_abbr,
        'link_count': link_count
    }
    
    # Store links separately for content generation
    link_data = [{'filename': filename, 'url': url} for filename, url in links]
    
    # Generate content with actual links (not Jekyll loops to avoid complexity)
    links_html = ""
    for link in link_data:
        links_html += f"""  <div class="col-md-6 col-lg-4 mb-3">
    <div class="card">
      <div class="card-body">
        <h6 class="card-title">{link['filename']}</h6>
        <a href="{link['url']}" target="_blank" class="btn btn-sm btn-primary">View Image</a>
      </div>
    </div>
  </div>
"""
    
    content = f"""## Overview
This page provides access to manufacturing census data for {state_name} in {year}.

## Available Images ({link_count} total)

<div class="row">
{links_html}</div>

## Historical Context
The {year} census provides detailed manufacturing statistics for {state_name}, offering insights into the state's industrial development during this period.
"""
    
    # Ensure directory exists
    os.makedirs(f'_census_data/{year}', exist_ok=True)
    
    # Write file
    with open(f'_census_data/{year}/{state_abbr.lower()}.md', 'w') as f:
        f.write('---\n')
        yaml.dump(front_matter, f, default_flow_style=False)
        f.write('---\n\n')
        f.write(content)


def main():
    """Main function to generate all pages"""
    print("Loading state data...")
    state_lookup = load_states()
    
    print("Getting database statistics...")
    years, stats = get_database_stats()
    
    print(f"Found data for years: {years}")
    
    # Generate year index pages
    for year in years:
        print(f"Generating year index page for {year}...")
        generate_year_index_page(year, stats[year], state_lookup)
        
        # Generate state pages for this year
        for state_abbr, link_count in stats[year].items():
            print(f"  Generating state page for {state_abbr} ({link_count} links)")
            generate_state_page(year, state_abbr, link_count, state_lookup)
    
    print("Page generation complete!")
    print(f"Generated {len(years)} year index pages")
    total_state_pages = sum(len(stats[year]) for year in years)
    print(f"Generated {total_state_pages} state pages")


if __name__ == '__main__':
    main()