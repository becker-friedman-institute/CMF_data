FROM ruby:3.2.2

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    findutils \
    python3-full \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r requirements.txt --break-system-packages

# Copy Gemfile first (for better caching)
COPY Gemfile* ./

# Install Ruby dependencies
RUN bundle install

# Create necessary directories
RUN mkdir -p _site assets/data assets/original

# Copy the rest of the application
COPY . .

# Generate database and build site
RUN python3 scripts/create_db.py original_html && \
    bundle exec jekyll build

# Expose port 4000
EXPOSE 4000

# Start Jekyll server
CMD ["bundle", "exec", "jekyll", "serve", "--host", "0.0.0.0"]