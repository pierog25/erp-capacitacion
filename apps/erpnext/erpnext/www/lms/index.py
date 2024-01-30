from __future__ import unicode_literals
import erpnext.education.utils as utils
import frappe

no_cache = 1

def get_context(context):
	context.education_settings = frappe.get_single("Education Settings")
	if not context.education_settings.enable_lms:
		frappe.local.flags.redirect_location = '/'
		raise frappe.Redirect
	context.featured_programs = get_featured_programs()

	context.user_email = frappe.db.get_value("User",{
		"name": frappe.session.user,
	},"email")

	context.designation = frappe.db.get_value("Employee",{
		"user_id": context.user_email,
		"status": "Active"
	},"designation")

	if context.designation == '' or context.designation is None:

		number_document = context.user_email.split("@")[0]

		context.number_document = (None,number_document)[number_document.isnumeric()]

		context.designation = frappe.db.get_value("Student",{
			"student_email_id": context.user_email
		},"puesto")

		if (context.designation == '' or context.designation is None) and (number_document is not None):
			context.designation = frappe.db.get_value("Student",{
				"dni": number_document
			},"puesto")

	if context.designation == '' or context.designation is None:
		context.designation = "ENCARGADO DE AGENCIA"
	# 	frappe.local.flags.redirect_location = '/app'
	# 	raise frappe.Redirect
	filters=[]
	if context.user_email != "carmen@shalom.com.pe":
		filters.append(["Puesto Curso","designation","=",context.designation])
	courses = frappe.db.get_all("Course",
								filters=filters, as_list=False)
	courses_program = {}
	for course in courses:
		programs = frappe.db.get_all("Program",
									 filters=[["Program Course","course","=",course.name]], as_list=False)
		if len(programs) > 0:
			courses_program[course.name] = programs[0].name
	courses_data = [frappe.get_doc("Course", course.name) for course in courses]
	courses_end = []
	for course_item in courses_data:
		if course_item.name in courses_program:
			course_end = {
				"name": course_item.name,
				"owner": course_item.owner,
				"creation": course_item.creation,
				"modified": course_item.modified,
				"modified_by": course_item.modified_by,
				"idx": course_item.idx,
				"docstatus": course_item.docstatus,
				"course_name": course_item.course_name,
				"department": course_item.department,
				"hero_image": course_item.hero_image,
				"doctype": course_item.doctype,
				"topics": course_item.topics,
				"designation": course_item.designation,
				"assessment_criteria": course_item.assessment_criteria,
				"program": courses_program[course_item.name],
			}
			courses_end.append(course_end)
	context.courses = courses_end

def get_featured_programs():
	return utils.get_portal_programs() or []