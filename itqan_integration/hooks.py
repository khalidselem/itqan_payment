from . import __version__ as app_version

app_name = "itqan_integration"
app_title = "Itqan"
app_publisher = "Jenan Alfahham"
app_description = "Itqan Integration "
app_email = "jenan_fh95@hotmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/itqan_integration/css/itqan_integration.css"
# app_include_js = "/assets/itqan_integration/js/itqan_integration.js"

# include js, css files in header of web template
# web_include_css = "/assets/itqan_integration/css/itqan_integration.css"
# web_include_js = "/assets/itqan_integration/js/itqan_integration.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "itqan_integration/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {"Sales Invoice" : "public/js/doctype/sales_invoice.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "itqan_integration.utils.jinja_methods",
#	"filters": "itqan_integration.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "itqan_integration.install.before_install"
# after_install = "itqan_integration.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "itqan_integration.uninstall.before_uninstall"
# after_uninstall = "itqan_integration.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "itqan_integration.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
	"Sales Invoice": "itqan_integration.overrides.doctype.sales_invoice.CustomSalesInvoice"
}

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"itqan_integration.tasks.all"
#	],
#	"daily": [
#		"itqan_integration.tasks.daily"
#	],
#	"hourly": [
#		"itqan_integration.tasks.hourly"
#	],
#	"weekly": [
#		"itqan_integration.tasks.weekly"
#	],
#	"monthly": [
#		"itqan_integration.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "itqan_integration.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "itqan_integration.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "itqan_integration.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["itqan_integration.utils.before_request"]
# after_request = ["itqan_integration.utils.after_request"]

# Job Events
# ----------
# before_job = ["itqan_integration.utils.before_job"]
# after_job = ["itqan_integration.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"itqan_integration.auth.validate"
# ]
