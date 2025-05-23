# Makefile for Becker Friedman Institute GitHub Pages site
# Development commands use Docker, production build is native

.PHONY: build serve serve-detached stop clean generate-db generate-files generate-pages reset-db build-prod shell

# Development build (using Docker)
build:
	docker build . -t bfi-github-pages

# Production build (native, no Docker)
build-prod:
	@echo "Installing dependencies..."
	python3 -m pip install -r requirements.txt
	bundle install
	@echo "Generating database..."
	python3 scripts/create_db.py original_html
	@echo "Generating pages from database..."
	python3 scripts/generate_pages_from_db.py
	@echo "Building site..."
	bundle exec jekyll build

# Generate the SQLite database from HTML files
generate-db:
	@echo "Generating SQLite database from HTML files..."
	docker run --rm -v $(PWD):/app bfi-github-pages python3 scripts/create_db.py original_html

# Reset the database (drop and recreate)
reset-db:
	@echo "Resetting SQLite database..."
	rm -f scripts/dropbox_links.db
	make generate-db

# Generate pages from database
generate-pages:
	@echo "Generating Jekyll pages from database..."
	docker run --rm -v $(PWD):/app bfi-github-pages python3 scripts/generate_pages_from_db.py

# Generate the static files
generate-files:
	@echo "Generating static files..."
	docker run --rm -v $(PWD):/app bfi-github-pages bundle exec jekyll build

# Serve the website locally (interactive mode)
serve: build generate-db generate-pages generate-files 
	@echo "Starting Jekyll server at http://localhost:4000"
	@echo "Press Ctrl+C to stop"
	docker run --rm -p 4000:4000 -v $(PWD):/app bfi-github-pages bundle exec jekyll serve --host 0.0.0.0

# Serve the website in detached mode
serve-detached: build generate-db generate-pages generate-files
	@echo "Starting Jekyll server at http://localhost:4000"
	docker run --name bfi-site -d -p 4000:4000 -v $(PWD):/app bfi-github-pages bundle exec jekyll serve --host 0.0.0.0
	@echo "Server running in background. Use 'make stop' to stop it."

# Stop the detached server
stop:
	docker stop bfi-site || true
	docker rm bfi-site || true

# Clean up Docker resources
clean: stop
	docker rmi bfi-github-pages || true
	rm -f scripts/dropbox_links.db
	rm -f dropbox_links.db
	rm -f *.md
	rm -rf _census_data

# Run bash inside the Docker container for debugging
shell:
	@echo "Starting bash inside the Docker container..."
	docker run --rm -it -v $(PWD):/app bfi-github-pages /bin/bash