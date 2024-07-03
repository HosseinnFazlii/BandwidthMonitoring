
# Django Monitoring Project with Telegram Bot Integration

This project allows you to monitor server bandwidth via a Django web application and interact with the data using a Telegram bot. The bot can register servers, list them, and provide server details. It supports role-based access with superadmins and admins.

## Features

- Register servers and monitor their bandwidth
- Interact with the server data via a Telegram bot
- Role-based access control (Superadmin, Admin, User)
- Superadmins can manage admins

## Prerequisites

- Docker and Docker Compose
- Telegram Bot Token
- Superadmin Telegram User ID

## Setup

### 1. Clone the Repository

First, clone the repository to your local machine:

```bash
git clone https://github.com/your-username/django-monitoring-bot.git
cd django-monitoring-bot
```

### 2. Create a `.env` File

Create a `.env` file in the root directory with the following content:

```
SUPERADMIN_ID=your_superadmin_telegram_id
TELEGRAM_TOKEN=your_telegram_bot_token
```

Replace `your_superadmin_telegram_id` and `your_telegram_bot_token` with your actual values.

### 3. Build and Run the Docker Containers

Build and start the Docker containers for the Django application, Redis, and Celery:

```bash
docker-compose up --build
```

### 4. Apply Migrations

In a new terminal window, run the following command to apply migrations:

```bash
docker-compose exec backend python manage.py migrate
```

### 5. Set the Telegram Webhook

Ensure your Telegram bot's webhook is set correctly. Replace `your_server_url` with your actual server URL:

```bash
docker-compose exec backend python manage.py setwebhook your_server_url/webhook/
```

## Using the Application

### Starting the Bot

1. Open your Telegram app and start a chat with your bot.
2. Type `/start` to initialize the bot. You should see a welcome message and a keyboard with options.

### Registering a Server

1. Click on `Register Server` button or type `/registerserver`.
2. Follow the prompts to enter server details (hostname, IP address, API key, etc.).

### Listing Servers

1. Click on `List Servers` button or type `/listservers`.
2. The bot will display a list of servers registered under your user ID.

### Viewing Server Details

1. After listing the servers, click on a server's name to view its details.
2. The bot will display all information related to the selected server.

### Deleting a Server

1. While viewing the server details, click on `Delete Server`.
2. The bot will confirm the deletion and remove the server from your list.

### Help

1. Click on `Help` button or type `/help` to see a list of available commands and their descriptions.

## Role-Based Access

### Superadmin

- Can manage admins and view all servers.
- Access the `/admin` command to manage user roles.

### Admin

- Can view all servers but cannot manage user roles.

### User

- Can only view and manage servers they have registered.

## Notes

- Ensure your environment variables in the `.env` file are correct.
- The project uses `python-decouple` to manage environment variables.
- Modify the `docker-compose.yml` and `Dockerfile` as needed for your environment.
