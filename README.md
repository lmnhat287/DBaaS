
# DBaaS

## Introduction
DBaaS (Database as a Service) is a MongoDB management system with a web interface, supporting login, user roles, backup/restore, database and collection management.

## Features
- User login/registration
- Role-based access (admin/user)
- Manage databases, collections, documents
- Backup and restore data
- Search and export data
- User-friendly web interface

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/lmnhat287/DBaaS.git
   cd DBaaS
   ```
2. Create a virtual environment and install packages:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Create a `.env` file with connection info:
   ```env
   SECRET_KEY=your-secret-key
   MONGO_URI=your-mongo-uri
   FLASK_APP=run.py
   FLASK_ENV=production
   ```
4. Run the application:
   ```bash
   flask run
   ```

## Deploy on EC2
- See detailed instructions in the `deployment/` folder
- Use Nginx and Gunicorn for production

## License
MIT License

## Contact
- Author: lmnhat287
- Email: lmnhat148@gmail.com
