import os
print("Current Working Directory:", os.getcwd())



def gale_shapley_with_priority(courses, students):
    # Free courses list (courses that still need TAs)
    free_courses = [course for course, details in courses.items() if details['students_needed'] > 0]
    matches = {}  # Stores TA to course matchings
    proposals = {course: [] for course in courses}  # Track proposals by course

    while free_courses:
        for course in free_courses[
                      :]:  # Iterate over a copy of free_courses to avoid modifying the list while iterating
            # Filter students who took this course and are not yet proposed by this course
            eligible = [s for s in students
                        if student_took_course(s, course)
                        and s['name'] not in proposals[course]]

            # Sort eligible students by GPA and prioritize graduate students
            eligible = sorted(eligible, key=lambda x: (x['GPA'], x['role'] == 'grad'), reverse=True)

            if eligible:
                student = eligible[0]  # Select the highest priority student
                proposals[course].append(student['name'])

                # If student isn't matched yet, match them
                if student['name'] not in matches:
                    matches[student['name']] = course
                    courses[course]['students_needed'] -= 1
                    if courses[course]['students_needed'] == 0:
                        free_courses.remove(course)  # Remove filled course from free_courses

                # If student is already matched, check if they prefer the new course
                else:
                    current_course = matches[student['name']]
                    if students.index(student) < students.index(
                            [s for s in students if s['name'] == student['name']][0]):
                        # Switch to the new course
                        matches[student['name']] = course
                        courses[course]['students_needed'] -= 1
                        courses[current_course]['students_needed'] += 1  # Return previous course need
                        if courses[course]['students_needed'] == 0:
                            free_courses.remove(course)  # Remove filled course from free_courses
                        if courses[current_course]['students_needed'] > 0 and current_course not in free_courses:
                            free_courses.append(
                                current_course)  # Add the old course back to free_courses if it needs TAs

    return matches


eligible_students = filter_eligible_students(students)
matches = gale_shapley_with_priority(courses, eligible_students)
print("Matches:", matches)