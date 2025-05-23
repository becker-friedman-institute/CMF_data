# Census of Manufacturers Data Archive

This project, led by scholars [Anders Humlum](https://www.andershumlum.com/), [Rick Hornbeck](https://www.chicagobooth.edu/faculty/directory/h/richard-hornbeck), and [Martin Rotemberg (NYU)](https://sites.google.com/view/mrotemberg/), involves digitizing the U.S. Census of Manufactures (CMF) from 1850, 1860, 1870, and 1880, capturing all existing establishment-level records.

## Overview

This Jekyll-based website provides access to historical manufacturing census data through:

- **Year-based browsing** (1850, 1860, 1870, 1880)
- **State-specific pages** with downloadable image links
- **Clean data sections** for processed datasets
- **Responsive design** with University of Chicago branding

## Process

The site uses a **database-driven approach** to generate content:

1. **HTML Parsing**: Original HTML files are parsed to extract Dropbox image links
2. **Database Creation**: Links are stored in a SQLite database organized by year and state
3. **Page Generation**: Jekyll pages are dynamically generated from the database
4. **Static Site Building**: Jekyll builds the final static website

```
original_html/ → SQLite Database → Generated Pages → Jekyll Site
```

## Requirements

- **Docker** (for containerized builds)
- **Make** (for task automation)

That's it! All other dependencies (Python, Jekyll, Ruby) are handled inside Docker containers.

## Local Development

### 1. Clone the Repository

```bash
git clone https://github.com/becker-friedman-institute/CMF_data.git
cd CMF_data
```

### 2. Generate Database and Pages

```bash
# Create database from HTML files and generate Jekyll pages
make generate-pages
```

This will:
- Parse all HTML files in `original_html/`
- Create `dropbox_links.db` with extracted links
- Generate year index pages (e.g., `1850.md`)
- Generate state pages in `_census_data/[year]/[state].md`

### 3. Serve the Site Locally

```bash
# Build and serve with live reload
make serve
```

The site will be available at: http://localhost:4000

### 4. Clean Generated Files (Optional)

```bash
# Remove generated database and pages
make clean
```

## Available Make Commands

| Command | Description |
|---------|-------------|
| `make serve` | Generate pages and serve site locally |
| `make serve-only` | Serve existing site without regenerating |
| `make generate-pages` | Generate database and Jekyll pages |
| `make create-db` | Create database from HTML files only |
| `make build` | Build static site for production |
| `make clean` | Remove generated files |

## Project Structure

```
├── _layouts/           # Jekyll templates
│   ├── base.html       # Main layout with UChicago header
│   └── census_data.html # Template for census pages
├── _data/              # Jekyll data files
│   ├── states.yml      # State names and abbreviations
│   └── clean_data_categories.yml
├── _clean_data/        # Manual documentation pages
├── _census_data/       # Generated state pages (ignored by git)
├── assets/
│   ├── css/           # Custom stylesheets
│   └── data/          # CSV data files
├── original_html/     # Source HTML files with Dropbox links
├── scripts/
│   ├── create_db.py           # Parse HTML → SQLite database
│   └── generate_pages_from_db.py # Database → Jekyll pages
├── .github/workflows/ # GitHub Pages deployment
├── Dockerfile         # Development environment
├── Makefile          # Task automation
├── _config.yml       # Jekyll configuration
└── requirements.txt  # Python dependencies
```

## GitHub Pages Deployment

The site automatically deploys to GitHub Pages when code is pushed to the `main` branch. The deployment process:

1. **Parses HTML files** to create the database
2. **Generates Jekyll pages** from the database
3. **Builds the static site** with Jekyll
4. **Deploys to GitHub Pages**

No manual intervention required - everything is automated via GitHub Actions.

## Data Sources

- **Original HTML Files**: Located in `original_html/` directory
- **Dropbox Links**: Extracted and stored in SQLite database
- **State Information**: Configured in `_data/states.yml`

## Development Notes

- **Generated files** (`_census_data/`, `*.db`) are excluded from version control
- **Docker containers** ensure consistent build environments
- **Jekyll collections** organize census data and clean data separately
- **Responsive design** works on desktop and mobile devices

## Contributing

1. Make changes to layouts, scripts, or source files
2. Test locally with `make serve`
3. Commit changes (generated files are auto-excluded)
4. Push to trigger automatic deployment

---

## About the Becker Friedman Institute

The [Becker Friedman Institute for Economics](https://bfi.uchicago.edu) at the University of Chicago serves as a hub for cutting-edge analysis and research across the economic disciplines.