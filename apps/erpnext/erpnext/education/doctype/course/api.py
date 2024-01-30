from frappe.utils.pdf import get_pdf
import frappe
import pdfkit
import jinja2
import os
from frappe.utils import getdate, nowdate
from frappe.utils import cstr, get_datetime, formatdate
from datetime import datetime
from datetime import date
from itertools import groupby
from operator import itemgetter
import copy
import requests
import numpy as np

@frappe.whitelist()
def evaluate_quiz():
    import json
    dni = frappe.form_dict.dni
    quiz_response = frappe.form_dict.quiz_response
    quiz_name = frappe.form_dict.quiz_name
    course = frappe.form_dict.course
    program = frappe.form_dict.program
    time_taken = frappe.form_dict.time_taken

    student = frappe.get_all("Student", {"dni": dni}, ["name"])[0].name

    quiz_response = json.loads(quiz_response)
    quiz = frappe.get_doc("Quiz", quiz_name)
    quizes = len(frappe.get_all("Quiz Activity", {'quiz': quiz.name, 'owner': frappe.session.user}))
    result, score, status = quiz.evaluate(quiz_response, quiz_name)

    # if has_super_access():
    #     return {'result': result, 'score': score, 'status': status,'quizes': (quizes + 1),'quiz':quiz}

    if student:
        enrollment = get_or_create_course_enrollment(student, course, program)
        if quiz.allowed_attempt(enrollment, quiz_name):
            enrollment.add_quiz_activity(quiz_name, quiz_response, result, score, status, time_taken)
            return {'result': result, 'score': score, 'status': status, 'quizes':(quizes+1),'quiz':quiz}
        else:
            return None


def get_or_create_course_enrollment(student_id, course, program):
    student = frappe.get_doc("Student", student_id)
    course_enrollment = get_enrollment("course", course, student_id)
    if not course_enrollment:
        program_enrollment = get_enrollment('program', program, student_id)
        if not program_enrollment:
            frappe.throw(("You are not enrolled in program "+program))
            return
        return student.enroll_in_course(course_name=course, program_enrollment=get_enrollment('program', program, student_id))
    else:
        return frappe.get_doc('Course Enrollment', course_enrollment)

def get_enrollment(master, document, student):
    """Gets enrollment for course or program

    Args:
        master (string): can either be program or course
        document (string): program or course name
        student (string): Student ID

    Returns:
        string: Enrollment Name if exists else returns empty string
    """
    if master == 'program':
        enrollments = frappe.get_all("Program Enrollment", filters={'student':student, 'program': document, 'docstatus': 1})
    if master == 'course':
        enrollments = frappe.get_all("Course Enrollment", filters={'student':student, 'course': document})

    if enrollments:
        return enrollments[0].name
    else:
        return None