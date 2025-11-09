# Use an official Nginx runtime as a parent image
FROM nginx:latest

# Copy your index.html file into the container's Nginx default HTML directory
COPY index.html /usr/share/nginx/html/

# (Optional) If you have other files (CSS, JS, images), copy them as well
# For example:
# COPY css/ /usr/share/nginx/html/css/
# COPY js/ /usr/share/nginx/html/js/
# COPY images/ /usr/share/nginx/html/images/

# Expose port 80 for Nginx
EXPOSE 4000

# Nginx starts automatically when the container runs, so no CMD is needed.