# Chat Application

This is a simple client-server chat application developed using Python and PyQt6 for the client GUI.

## Features

- **User Authentication:** Users can log in or sign up with a username and password.
- **Public and Private Messaging:** Users can send messages to everyone or privately to specific users.
- **Admin Controls:** Admins can kick, ban, and unban users using the admin console.
- **Database Storage:** Messages, users, and admin actions are stored in a MySQL database.

## Getting Started

### Prerequisites

- Python 3.x
- PyQt6
- MySQL server

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/chat-application.git
    cd chat-application
    ```

2. Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

3. Set up the MySQL database:
   - Create a database and configure the connection details in the server code.
   - Run the provided SQL queries in the `server.py` file to create the necessary tables.

4. Run the server:

    ```bash
    python server.py
    ```

5. Run the client:

    ```bash
    python client.py
    ```

## Usage

- Launch the client application and provide the host, port, username, and password.
- Log in or sign up, and start chatting with others.
- Admins can use the admin console to manage users and shut down the server.

## Contributing

Contributions are welcome! If you find any issues or have suggestions, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [GNU General Public License](GPL) file for details.
