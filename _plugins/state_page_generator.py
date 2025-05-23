from jekyll import Generator, Page
import os
import sqlite3


class StatePageGenerator(Generator):
    def generate(self, site):
        # Check if default state template is enabled
        if not site.config.get('default_state_template'):
            return

        # Get all years from the census_data collection
        years = set()
        for doc in site.collections['census_data'].docs:
            if 'year' in doc.data:
                years.add(doc.data['year'])

        # Connect to the database
        db_path = os.path.join(site.source, 'scripts', 'dropbox_links.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # For each year and state combination
        for year in years:
            for state in site.data['states']:
                # Check if a specific file exists for this state/year
                state_file = None
                for doc in site.collections['census_data'].docs:
                    if (doc.data.get('year') == year and
                            doc.data.get('state') == state['abbr']):
                        state_file = doc
                        break

                # If no specific file exists, create a default page
                if not state_file:
                    # Get links from database
                    cursor.execute('''
                        SELECT filename, dropbox_url 
                        FROM dropbox_files 
                        WHERE state = ? AND year = ?
                    ''', (state['abbr'], year))
                    links = cursor.fetchall()
                    
                    page = StatePage(site, year, state, links)
                    site.pages.append(page)

        conn.close()


class StatePage(Page):
    def __init__(self, site, year, state, links=None):
        super().__init__(site)
        self.base = site.source
        self.dir = year
        self.name = f"{state['abbr'].lower()}.html"

        # Read the default state template
        template_path = os.path.join(
            self.base, '_layouts', 'default_state.html'
        )
        with open(template_path, 'r') as f:
            self.content = f.read()

        # Set the page data
        self.data = {
            'year': year,
            'state': state['abbr'],
            'title': f"{state['name']} Census Data - {year}",
            'layout': 'default_state',
            'links': links or []
        } 