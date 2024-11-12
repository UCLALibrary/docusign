FROM python:3.13-slim-bookworm

# Set correct timezone
RUN ln -sf /usr/share/zoneinfo/America/Los_Angeles /etc/localtime

# Create generic user and group
RUN useradd -c "generic app user" -d /home/docusign -s /bin/bash -m docusign

# Swtich to application directory, create it if it doesn't exist
WORKDIR /home/docusign/app

# Make sure new aspace user owns the directory
RUN chown -R docusign:docusign /home/docusign/app

# Switch to the new user
USER docusign

# Copy the rest of the application code to the working directory with aspace as the owner
COPY --chown=docusign:docusign . .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
