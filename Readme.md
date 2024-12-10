# Backend Server for Task Management and Report Subscription System

## Key Features

### User Authentication
- **Log In**: Secure user login functionality.
- **Sign Up**: Create new user accounts.

### Task Management API
- **Create Task**: Add new tasks.
- **Delete Task**: Remove tasks.
- **Retrieve Task**: Fetch task details.
- **Update Task**: Modify existing tasks.
- **Batch Task**: Perform bulk operations on tasks.
- **Restore Task**: Recover deleted tasks.

### Subscription API
- **Subscribe/Unsubscribe to Reports**: Manage subscriptions for periodic reports.

### Report Generation
- **Automated Reports**: Generate and send reports automatically on a daily, weekly, or monthly schedule.

### Dockerfile  
The `Dockerfile` defines the necessary steps to build and configure the environment for the backend server.


## How To Use

To clone and run this application, you'll need [Git](https://git-scm.com) and [Node.js](https://nodejs.org/en/download/) (which comes with [npm](http://npmjs.com)) installed on your computer. From your command line:

```bash
# Clone this repository
$ git clone https://github.com/ZiaDs11/automation-task

# Go into the repository
$ cd root

# Create virtual ennvironment 
$ python -m venv env 

# Activate virtual ennvironment 
$ . env/Script/activate

# Install dependencies
$ pip install -r requirement.txt

# Run the app
$ python main.py

# Database 
The backend server uses an SQLite database located at:
'root/instance/Vodafone.db' No additional installation 
```

## Testing the Backend Server

After starting the backend server, follow these steps to test the API endpoints:

1. Open your **Postman** application.
2. Import the Postman collection file named **`New Collection.postman_collection`**.
3. Use the imported collection to test the available endpoints.
