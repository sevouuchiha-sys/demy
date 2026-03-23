from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)

# --- DATA STORE ---
students = [
    {"id": 1, "name": "John Doe", "grade": 10, "section": "Zechariah"},
    {"id": 2, "name": "Jane Smith", "grade": 11, "section": "Genesis"}
]

# --- HTML FRONTEND (Embedded for completeness) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student CRUD Pro</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <style>
        body { background-color: #f8f9fa; padding-top: 50px; }
        .card { border: none; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        .table-container { background: white; padding: 20px; border-radius: 10px; }
    </style>
</head>
<body>

<div class="container">
    <div class="row">
        <div class="col-md-4">
            <div class="card p-4">
                <h4 id="form-title">Add Student</h4>
                <hr>
                <input type="hidden" id="student-id">
                <div class="mb-3">
                    <label class="form-label">Full Name</label>
                    <input type="text" id="name" class="form-control" placeholder="Enter name">
                </div>
                <div class="mb-3">
                    <label class="form-label">Grade</label>
                    <input type="number" id="grade" class="form-control" placeholder="Enter grade">
                </div>
                <div class="mb-3">
                    <label class="form-label">Section</label>
                    <input type="text" id="section" class="form-control" placeholder="Enter section">
                </div>
                <button class="btn btn-primary w-100" onclick="saveStudent()" id="save-btn">Save Student</button>
                <button class="btn btn-secondary w-100 mt-2" onclick="clearForm()">Clear</button>
            </div>
        </div>

        <div class="col-md-8">
            <div class="table-container shadow-sm">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h4>Student Directory</h4>
                    <input type="text" id="searchInput" class="form-control w-50" placeholder="Search by name..." onkeyup="filterTable()">
                </div>
                <table class="table table-hover">
                    <thead class="table-dark">
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Grade</th>
                            <th>Section</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="student-list"></tbody>
                </table>
            </div>
        </div>
    </div>
</div>

<script>
    const API_URL = '/students';

    document.addEventListener('DOMContentLoaded', loadStudents);

    async function loadStudents() {
        const res = await fetch(API_URL);
        const data = await res.json();
        const list = document.getElementById('student-list');
        list.innerHTML = '';
        data.students.forEach(s => {
            list.innerHTML += `
                <tr>
                    <td>${s.id}</td>
                    <td>${s.name}</td>
                    <td>${s.grade}</td>
                    <td>${s.section}</td>
                    <td>
                        <button class="btn btn-sm btn-info text-white" onclick="editStudent(${s.id}, '${s.name}', ${s.grade}, '${s.section}')">Edit</button>
                        <button class="btn btn-sm btn-danger" onclick="deleteStudent(${s.id})">Delete</button>
                    </td>
                </tr>`;
        });
    }

    async function saveStudent() {
        const id = document.getElementById('student-id').value;
        const payload = {
            name: document.getElementById('name').value,
            grade: document.getElementById('grade').value,
            section: document.getElementById('section').value
        };

        if(!payload.name) return Swal.fire('Error', 'Name is required', 'error');

        const method = id ? 'PUT' : 'POST';
        const url = id ? `${API_URL}/${id}` : API_URL;

        const res = await fetch(url, {
            method: method,
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });

        if(res.ok) {
            Swal.fire('Success', `Student ${id ? 'updated' : 'added'}!`, 'success');
            clearForm();
            loadStudents();
        }
    }

    async function deleteStudent(id) {
        const result = await Swal.fire({
            title: 'Are you sure?',
            text: "This cannot be undone!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            confirmButtonText: 'Yes, delete it!'
        });

        if (result.isConfirmed) {
            await fetch(`${API_URL}/${id}`, { method: 'DELETE' });
            loadStudents();
            Swal.fire('Deleted!', 'Student record removed.', 'success');
        }
    }

    function editStudent(id, name, grade, section) {
        document.getElementById('student-id').value = id;
        document.getElementById('name').value = name;
        document.getElementById('grade').value = grade;
        document.getElementById('section').value = section;
        document.getElementById('form-title').innerText = "Edit Student #" + id;
        document.getElementById('save-btn').innerText = "Update Details";
        document.getElementById('save-btn').className = "btn btn-warning w-100";
    }

    function clearForm() {
        document.getElementById('student-id').value = '';
        document.getElementById('name').value = '';
        document.getElementById('grade').value = '';
        document.getElementById('section').value = '';
        document.getElementById('form-title').innerText = "Add Student";
        document.getElementById('save-btn').innerText = "Save Student";
        document.getElementById('save-btn').className = "btn btn-primary w-100";
    }

    function filterTable() {
        let input = document.getElementById("searchInput").value.toUpperCase();
        let rows = document.getElementById("student-list").getElementsByTagName("tr");
        for (let i = 0; i < rows.length; i++) {
            let nameCol = rows[i].getElementsByTagName("td")[1];
            if (nameCol) {
                let textValue = nameCol.textContent || nameCol.innerText;
                rows[i].style.display = textValue.toUpperCase().indexOf(input) > -1 ? "" : "none";
            }
        }
    }
</script>
</body>
</html>
"""

# --- BACKEND ROUTES ---

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/students', methods=['GET'])
def get_students():
    return jsonify({"students": students})

@app.route('/students', methods=['POST'])
def add_student():
    data = request.get_json()
    new_id = students[-1]['id'] + 1 if students else 1
    new_entry = {
        "id": new_id,
        "name": data.get('name'),
        "grade": data.get('grade'),
        "section": data.get('section')
    }
    students.append(new_entry)
    return jsonify(new_entry), 201

@app.route('/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    data = request.get_json()
    student = next((s for s in students if s['id'] == student_id), None)
    if student:
        student.update(data)
        return jsonify(student)
    return jsonify({"error": "Not found"}), 404

@app.route('/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    global students
    students = [s for s in students if s['id'] != student_id]
    return jsonify({"message": "Deleted"}), 200

if __name__ == '__main__':
    app.run(debug=True)
