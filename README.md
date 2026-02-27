FastAPI Task Management System

This project is a simple backend built using FastAPI.

It allows users to:
- Create tasks
- View tasks
- Update tasks
- Delete tasks
- Filter tasks
- View statistics

Storage Method:
Tasks are stored in a file called tasks.txt.
Each task is saved as one JSON object per line (JSON Lines format).

How to Run:

1. Clone the repository:
git clone https://github.com/haleyannrobinson2-web/fastapi-task-manager.git

2. Navigate into the project folder:
cd fastapi-task-manager

3. Create a virtual environment:
python3 -m venv venv
source venv/bin/activate

4. Install dependencies:
pip install fastapi uvicorn

5. Run the server:
uvicorn main:app --reload

6. Open in browser:
http://127.0.0.1:8000/docs

Running the application:

Start the server:
uvicorn main:app --reload

The API will be available at:
http://127.0.0.1:8000





Author:
Haley Robinson
