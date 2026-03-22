from flask import Flask, jsonify, request, render_template_string, redirect, url_for

app = Flask(__name__)

# Sample in-memory data [cite: 55, 100]
students = [
    {"id": 1, "name": "Juan", "grade": 85, "section": "Zechariah"},
    {"id": 2, "name": "Maria", "grade": 90, "section": "Zechariah"},
    {"id": 3, "name": "Pedro", "grade": 70, "section": "Zion"}
]

@app.route('/')
def home():
    return "Welcome to the Student API! Go to /students to see the list." [cite: 59, 107]

# VIEW ALL STUDENTS [cite: 92, 109]
@app.route('/students', methods=['GET'])
def get_students():
    return jsonify(students) [cite: 94]

# GRADE EVALUATION ROUTE [cite: 22, 25]
@app.route('/student')
def get_student_evaluation():
    # Get grade from query parameter (default=0) [cite: 28]
    grade = int(request.args.get('grade', 0))
    # Determine pass or fail [cite: 30]
    remarks = "Pass" if grade >= 75 else "Fail"
    
    return jsonify({
        "name": "Juan",
        "grade": grade,
        "section": "Zechariah",
        "remarks": remarks
    }) [cite: 31-36]

# ADD NEW STUDENT [cite: 74]
@app.route('/add_student', methods=['POST'])
def add_student():
    name = request.form.get("name") [cite: 76]
    grade = int(request.form.get("grade")) [cite: 77]
    section = request.form.get("section") [cite: 78]
    
    # Simple validation [cite: 177]
    if grade < 0 or grade > 100:
        return jsonify({"error": "Grade must be between 0 and 100"}), 400 [cite: 178]

    new_student = {
        "id": len(students) + 1,
        "name": name,
        "grade": grade,
        "section": section
    } [cite: 79-85]
    
    students.append(new_student) [cite: 86]
    return jsonify({"message": "Student added successfully!", "student": new_student}) [cite: 87-90]

# SUMMARY ANALYTICS [cite: 149]
@app.route('/summary')
def summary():
    all_grades = [s["grade"] for s in students]
    passed = len([g for g in all_grades if g >= 75]) [cite: 152]
    failed = len(all_grades) - passed [cite: 153]
    avg = sum(all_grades) / len(all_grades) if all_grades else 0 [cite: 154]
    
    return jsonify({
        "average": avg,
        "passed": passed,
        "failed": failed
    }) [cite: 155]

if __name__ == '__main__':
    app.run(debug=True) [cite: 96]
