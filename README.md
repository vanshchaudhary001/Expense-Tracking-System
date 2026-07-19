# Expense Management System

This project is an expense management system that consists of a Streamlit frontend application and a FastAPI backend server.


## Project Structure

- **frontend/**: Contains the Streamlit application code.
- **backend/**: Contains the FastAPI backend server code.
- **tests/**: Contains the test cases for both frontend and backend.
- **requirements.txt**: Lists the required Python packages.
- **README.md**: Provides an overview and instructions for the project.


## Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/expense-management-system.git
   cd expense-management-system
   ```
1. **Install dependencies:**:   
   ```commandline
    pip install -r requirements.txt
   ```
1. **Run the FastAPI server:**:   
   ```commandline
    uvicorn server.server:app --reload
   ```
1. **Run the Streamlit app:**:   
   ```commandline
    streamlit run frontend/app.py
   ```

## Local DB fallback and development notes

- The backend tries to connect to a MySQL server at `localhost:3306`. If MySQL is not available, the backend will automatically fall back to a local SQLite database file named `expense_manager.db` located in the project root. The SQLite DB is auto-created and seeded with a sample row used by tests and the demo UI.

- To run with MySQL (recommended for production-like behavior) using Docker, run:

```bash
docker run --name expense-mysql -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=expense_manager -p 3306:3306 -d mysql:8.0
# wait until the container is ready, then seed the table:
docker exec -i expense-mysql mysql -uroot -proot expense_manager <<'SQL'
CREATE TABLE IF NOT EXISTS expenses (
  id INT AUTO_INCREMENT PRIMARY KEY,
  expense_date DATE,
  amount DECIMAL(10,2),
  category VARCHAR(255),
  notes TEXT
);
INSERT INTO expenses (expense_date, amount, category, notes) VALUES ('2024-08-15', 10.00, 'Shopping', 'Bought potatoes');
SQL
```

- To run locally without Docker/MySQL, simply start the backend and frontend as shown above; the app will create and use `expense_manager.db` and seed example data automatically.