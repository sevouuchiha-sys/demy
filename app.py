import os
import sqlite3
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)
DB_NAME = 'database.db'

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema on startup."""
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                grade INTEGER,
                section TEXT
            )
        ''')
        conn.commit()

# Initialize database
init_db()

@app.route('/')
def home():
    return render_template('index.html')

# --- CRUD API ROUTES ---

@app.route('/students', methods=['GET'])
def get_students():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM students').fetchall()
    conn.close()
    return jsonify({"students": [dict(row) for row in rows]})

@app.route('/students', methods=['POST'])
def add_student():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"error": "Name is required"}), 400
    
    conn = get_db_connection()
    cur = conn.execute(
        'INSERT INTO students (name, grade, section) VALUES (?, ?, ?)',
        (data.get('name'), data.get('grade'), data.get('section'))
    )
    new_id = cur.lastrowid
    conn.commit()
    conn.close()
    return jsonify({"id": new_id, **data}), 201

@app.route('/students/<int:id>', methods=['PUT'])
def update_student(id):
    data = request.get_json()
    conn = get_db_connection()
    conn.execute(
        'UPDATE students SET name = ?, grade = ?, section = ? WHERE id = ?',
        (data.get('name'), data.get('grade'), data.get('section'), id)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Student updated successfully"})

@app.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM students WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Student deleted successfully"})

if __name__ == '__main__':
    # Use environment variable for Port (required for Render)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Student Manager</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <div class="container mt-5">
        <h2 class="text-center mb-4">Student CRUD System</h2>
        
        <div class="row">
            <div class="col-md-4">
                <div class="card shadow-sm p-3">
                    <h5 id="form-title">Add Student</h5>
                    <input type="hidden" id="student-id">
                    <input type="text" id="name" class="form-control mb-2" placeholder="Name">
                    <input type="number" id="grade" class="form-control mb-2" placeholder="Grade">
                    <input type="text" id="section" class="form-control mb-3" placeholder="Section">
                    <button class="btn btn-primary w-100" onclick="saveStudent()">Save</button>
                    <button class="btn btn-link w-100 mt-1" onclick="resetForm()">Clear</button>
                </div>
            </div>

            <div class="col-md-8">
                <div class="card shadow-sm p-3">
                    <table class="table table-hover">
                        <thead class="table-dark">
                            <tr>
                                <th>Name</th><th>Grade</th><th>Section</th><th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="student-list"></tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script>
        const API = '/students';
        
        async function load() {
            const res = await fetch(API);
            const data = await res.json();
            const list = document.getElementById('student-list');
            list.innerHTML = data.students.map(s => `
                <tr>
                    <td>${s.name}</td><td>${s.grade}</td><td>${s.section}</td>
                    <td>
                        <button class="btn btn-sm btn-info text-white" onclick='editStudent(${JSON.stringify(s)})'>Edit</button>
                        <button class="btn btn-sm btn-danger" onclick="deleteStudent(${s.id})">Delete</button>
                    </td>
                </tr>
            `).join('');
        }

        async function saveStudent() {
            const id = document.getElementById('student-id').value;
            const data = {
                name: document.getElementById('name').value,
                grade: document.getElementById('grade').value,
                section: document.getElementById('section').value
            };
            await fetch(id ? `${API}/${id}` : API, {
                method: id ? 'PUT' : 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            resetForm(); load();
        }

        async function deleteStudent(id) {
            if(confirm("Delete student?")) {
                await fetch(`${API}/${id}`, { method: 'DELETE' });
                load();
            }
        }

        function editStudent(s) {
            document.getElementById('student-id').value = s.id;
            document.getElementById('name').value = s.name;
            document.getElementById('grade').value = s.grade;
            document.getElementById('section').value = s.section;
            document.getElementById('form-title').innerText = "Edit Student";
        }

        function resetForm() {
            document.getElementById('student-id').value = '';
            document.getElementById('name').value = '';
            document.getElementById('grade').value = '';
            document.getElementById('section').value = '';
            document.getElementById('form-title').innerText = "Add Student";
        }

        load();
    </script>
</body>
</html>
