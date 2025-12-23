FROM manimcommunity/manim:stable

USER root
# Install any additional dependencies if needed
# RUN pip install ...

WORKDIR /app

# Ensure directories exist
RUN mkdir -p /app/scenes /app/media

# Default command can be overridden
# We use the manim entrypoint from the base image
