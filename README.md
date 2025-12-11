# Organization Management Service

A backend service built with **Python (FastAPI)** and **MongoDB** that supports creating and managing organizations in a multi-tenant style architecture.

## 📋 Table of Contents
- [Objective](#objective)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Architecture & Design](#architecture--design)
- [Design Choices & Trade-offs](#design-choices--trade-offs)

---

## 🎯 Objective
The goal of this project is to implement a REST API for managing organizations. The system utilizes a **Master Database** for global metadata and creates **Dynamic Collections** for each organization to ensure data isolation (Multi-tenancy).

## 🛠 Tech Stack
- **Framework**: FastAPI (Python 3.9+)
- **Database**: MongoDB
- **ODM**: Beanie (for Master DB) & Motor (for Async Driver)
- **Authentication**: JWT (JSON Web Tokens) with BCrypt hashing
- **Server**: Uvicorn

---

## 📂 Project Structure
The project follows a modular, class-based design pattern.

```text
org_manager/
├── app/
│   ├── __init__.py
│   ├── main.py             # Application entry point & Routing
│   ├── config.py           # Environment variable management
│   ├── database.py         # MongoDB connection & dynamic collection logic
│   ├── models.py           # Database Schemas & Pydantic models
│   ├── auth.py             # JWT handling and Password hashing
│   └── services.py         # Business logic (Class-based controllers)
├── requirements.txt        # Python dependencies
└── README.md               # Documentation

# 🏃 Steps to Run the Application

### 1. Prerequisites
Ensure you have the following installed on your system:
*   [Python 3.9+](https://www.python.org/downloads/)
*   [MongoDB](https://www.mongodb.com/try/download/community) (Make sure the service is running on port `27017`)
*   [Git](https://git-scm.com/)

### 2. Clone the Repository
```bash
git clone <your-repository-url>
cd org_manager
```

### 3. Create a Virtual Environment
It is highly recommended to use a virtual environment to isolate dependencies.

**For Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**For macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
Install the required Python packages listed in `requirements.txt`.
```bash
pip install -r requirements.txt
```

### 5. Configure Environment (Optional)
The application comes with default settings for local development. If you want to change the database URL or secret keys, create a `.env` file in the root directory:

```ini
# .env
MONGO_URI=mongodb://localhost:27017
MASTER_DB_NAME=master_db
SECRET_KEY=change_this_to_a_secure_key
```

### 6. Run the Server
Start the application using Uvicorn (the ASGI server).
```bash
uvicorn app.main:app --reload
```
*Note: The `--reload` flag enables auto-reload, so the server restarts when you save code changes.*

### 7. Test the Application
Once the server is running, open your web browser and navigate to the interactive API documentation:

*   **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

#### Quick Test Flow:
1.  **Create Org:** Use `POST /org/create` to register.
2.  **Login:** Use `POST /admin/login` to get an `access_token`.
3.  **Authorize:** Click the "Authorize" button (top right), type `Bearer <your_token>`, and click "Authorize".
4.  **Manage:** Now you can use `PUT /org/update` or `DELETE /org/delete`.

### ⚠️ Database Configuration Note

Please note that I could not provide a live MongoDB Atlas cluster connection due to free tier limitations. 

To ensure a smooth review process, I have kept the database configuration modular. You can connect to your own instance by modifying the `MONGO_URI` in `app/config.py` or the `.env` file. 

*I apologize for this inconvenience and thank you for accommodating this.*
