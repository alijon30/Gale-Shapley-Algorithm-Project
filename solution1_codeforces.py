import pandas as pd

# Load students data from students.csv
students_df = pd.read_csv('/Users/alijonkarimberdiev/PycharmProjects/DataStructure/Gale-Shapley Algorithm/students.csv')

# Load courses data from courses.csv
courses_df = pd.read_csv('/Users/alijonkarimberdiev/PycharmProjects/DataStructure/Gale-Shapley Algorithm/courses.csv')

# Convert courses data to dictionary format for processing
courses = {row['course_name']: {'students_needed': row['students_needed'], 'class_size': row['class_size']}
           for index, row in courses_df.iterrows()}

# Convert students data to a list of dictionaries for processing
students = students_df.to_dict(orient='records')



def filter_eligible_students(students):
    # Filter students based on GPA >= 3.5 and DSA grade = 'A'
    return [student for student in students if student['GPA'] >= 3.5 and student['DSA_grade'] == 'A']

eligible_students = filter_eligible_students(students)


def student_took_course(student, course):
    # Check if the 'courses_taken' field exists and is a string
    courses_taken = student.get('courses_taken', '')

    if not isinstance(courses_taken, str):  # If not a string, return False
        return False

    # Split the courses_taken field by ", " to get a list of courses
    courses_list = courses_taken.split(", ")

    # Check if the specific course is in the list
    for course_taken in courses_list:
        if course in course_taken:
            return True
    return False

def gale_shapley_with_priority(courses, students):
    # Free courses list (courses that still need TAs)
    free_courses = [course for course, details in courses.items() if details['students_needed'] > 0]
    matches = {}  # Stores TA to course matchings
    proposals = {course: [] for course in courses}  # Track proposals by course

    def course_priority(course_name):
        """Helper function to get course priority based on 'students_needed' or any other criteria."""
        return courses[course_name]['students_needed']  # Higher students_needed means higher priority

    while free_courses:
        for course in free_courses[:]:  # Iterate over a copy of free_courses
            # Filter students who took this course and are not yet proposed by this course
            eligible = [s for s in students
                        if student_took_course(s, course)
                        and s['name'] not in proposals[course]]

            # Sort eligible students by GPA and prioritize graduate students
            eligible = sorted(eligible, key=lambda x: (x['GPA'], x['role'] == 'grad'), reverse=True)

            # Debug: print the current state of the course and its eligible students
            print(f"Course: {course}, Eligible students: {[s['name'] for s in eligible]}")

            if not eligible:
                # If no eligible students, break out of the loop to avoid infinite loop
                print(f"No eligible students for course {course}. Moving on.")
                free_courses.remove(course)
                continue

            student = eligible[0]  # Select the highest priority student
            proposals[course].append(student['name'])  # Mark the student as proposed

            # If the student is not matched to any course, match them
            if student['name'] not in matches:
                print(f"Assigning {student['name']} to course {course}.")
                matches[student['name']] = course
                courses[course]['students_needed'] -= 1
                if courses[course]['students_needed'] == 0:
                    free_courses.remove(course)  # Course is fully matched, remove from free_courses

            # If the student is already matched, check preference
            else:
                current_course = matches[student['name']]
                # Use course_priority to compare the priority of the new course and the current course
                if course_priority(course) > course_priority(current_course):
                    # If the new course has higher priority, switch the student to the new course
                    print(f"Switching {student['name']} from course {current_course} to course {course}.")
                    matches[student['name']] = course
                    courses[course]['students_needed'] -= 1
                    courses[current_course]['students_needed'] += 1  # Old course needs a new TA

                    # If new course is fully matched, remove from free_courses
                    if courses[course]['students_needed'] == 0:
                        free_courses.remove(course)

                    # If old course needs more TAs, add it back to free_courses
                    if courses[current_course]['students_needed'] > 0 and current_course not in free_courses:
                        free_courses.append(current_course)

    return matches


def generate_report(matches, students, courses, report_filename='ta_assignment_report.txt'):
    # Group students by courses
    course_assignments = {}
    for student, course in matches.items():
        if course not in course_assignments:
            course_assignments[course] = []
        course_assignments[course].append(student)

    # Generate the report
    with open(report_filename, 'w') as report_file:
        report_file.write("TA Assignment Report\n")
        report_file.write("=" * 30 + "\n\n")

        # List courses and their assigned TAs
        report_file.write("Courses and Assigned TAs:\n")
        for course, students_list in course_assignments.items():
            report_file.write(f"Course {course} has the following TAs: {', '.join(students_list)}\n")

        # Gather all assigned students
        assigned_students = set(matches.keys())

        # List unassigned students
        report_file.write("\nUnassigned Students:\n")
        unassigned_students = [student['name'] for student in students if student['name'] not in assigned_students]

        if unassigned_students:
            for student in unassigned_students:
                report_file.write(f"{student} is not assigned to any course.\n")
        else:
            report_file.write("All eligible students have been assigned to courses.\n")

    print(f"Report generated and saved as {report_filename}")


# Run the Gale-Shapley algorithm
matches = gale_shapley_with_priority(courses, eligible_students)

# Generate the report and save it
generate_report(matches, students, courses)

# Display the results of the matching process
for student, course in matches.items():
    print(f"Student {student} is assigned to course {course}.")