# Use full Python 3.12 image to include audioop
FROM python:3.12

# Set working directory
WORKDIR /app

# Copy all files to container
COPY . /app

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose the port your Flask server runs on
EXPOSE 8080

# Run the bot
CMD ["python", "bot.py"]
