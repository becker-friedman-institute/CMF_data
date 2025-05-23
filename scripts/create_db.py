import os
import glob
import sqlite3
import argparse
from bs4 import BeautifulSoup

def setup_database():
    """Create and return a connection to the SQLite database with the necessary table"""
    conn = sqlite3.connect('dropbox_links.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS dropbox_files (
        id INTEGER PRIMARY KEY,
        state TEXT,
        year INTEGER,
        filename TEXT,
        dropbox_url TEXT,
        source_file TEXT
    )
    ''')
    conn.commit()
    
    return conn

def extract_state_year_from_filename(file_path):
    """Extract state and year from a filename; returns (state, year) or (None, None) if cannot parse"""
    try:
        base_filename = os.path.basename(file_path)
        if '_' in base_filename:
            parts = base_filename.split('_')
            state = parts[0]
            year = parts[1].split('.')[0]
            
            # Basic validation
            if len(state) == 2 and year.isdigit() and len(year) == 4:
                return state, year
    except Exception:
        pass
    
    # Return None for files that don't match the pattern
    return None, None

def parse_html_file(file_path):
    """Parse a single HTML file and return a list of (filename, url) tuples"""
    results = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')
            links = soup.find_all('a')
            
            for link in links:
                dropbox_url = link.get('href')
                filename = link.text.strip()
                if dropbox_url and filename:
                    results.append((filename, dropbox_url))
    except Exception as e:
        print(f"Error parsing {file_path}: {str(e)}")
    
    return results

def store_links_in_db(conn, file_path, state, year, links):
    """Store the extracted links in the database"""
    cursor = conn.cursor()
    source_file = os.path.basename(file_path)
    
    for filename, dropbox_url in links:
        cursor.execute('''
        INSERT INTO dropbox_files (state, year, filename, dropbox_url, source_file)
        VALUES (?, ?, ?, ?, ?)
        ''', (state, year, filename, dropbox_url, source_file))
    
    conn.commit()
    return len(links)

def process_directory(directory_path, additional_files=None):
    """Process all HTML files in the given directory and any additional specified files"""
    conn = setup_database()
    
    # Process standard pattern files
    standard_pattern = os.path.join(directory_path, "??_????.html")
    html_files = glob.glob(standard_pattern)
    
    # Add additional files if provided
    if additional_files:
        for file in additional_files:
            full_path = os.path.join(directory_path, file)
            if os.path.exists(full_path) and full_path not in html_files:
                html_files.append(full_path)
    
    total_links = 0
    
    for html_file in html_files:
        state, year = extract_state_year_from_filename(html_file)
        
        # Handle files that don't match the naming convention
        if state is None:
            print(f"Warning: File {html_file} doesn't match naming convention. Using placeholder values.")
            state = "UN"  # Unknown state
            year = "0000"  # Unknown year
        
        links = parse_html_file(html_file)
        count = store_links_in_db(conn, html_file, state, year, links)
        total_links += count
        
        print(f"Processed {html_file} - State: {state}, Year: {year}, Links: {count}")
    
    conn.close()
    print(f"Database creation complete! Total links processed: {total_links}")

def main():
    parser = argparse.ArgumentParser(description='Parse HTML files for Dropbox links and store in SQLite')
    parser.add_argument('directory', help='Directory containing the HTML files to process')
    parser.add_argument('--additional', nargs='+', help='Additional non-standard files to process')
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.directory):
        print(f"Error: {args.directory} is not a valid directory")
        return
    
    process_directory(args.directory, args.additional)

if __name__ == "__main__":
    main()