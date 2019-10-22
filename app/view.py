"""
Main .py file for the views in the backend for the dashboard

@author Zaeem
"""

from flask import url_for, redirect, render_template, flash, g, session, jsonify, request, send_from_directory
from flask import Flask
from app import app
import os, sys
name_to_netid = {
        "Alvaro Lee":"alb433",
        "Bedros Janoyan":"bdj25",
        "Brian Mcdonagh": "bpm74",
        "Bryan Zin": "bz297",
        "Cuyler Crandall":"csc254",
        "Diane Lee": "ddl58",
        "Emily Youtt":"eay9",
        "Jackson Hardin": "jph266",
        "Juliette Bendheim": "jb974",
        "Kyle Harris": "kah289",
        "Matthew Menis": "mnm54",
        "Max Li": "mdl262",
        "Mrinal Thomas": "mt779",
        "Nikki Hart": "njh84",
        "Zaeem Rana": "zmr5"
    } 

@app.route('/')
def index():
    return render_template('/layouts/default.html', content = render_template('./pages/index.html'))

@app.route('/mechanicalCal.html')
def mechanicalCal():
    return render_template('/layouts/default.html', content = render_template('./pages/mechanicalCal.html'))

@app.route('/sandingSubmit.html')
def sandingSubmit():
    return render_template('/layouts/default.html', content = render_template('./pages/sandingSubmit.html'))

@app.route('/sanding.html', methods=['GET', 'POST'])
def sanding():

    if request.method == "POST":
        
        names_checked = request.form.getlist("sandingcheck")
        netids_checked = [ name_to_netid[str(name)] for name in names_checked]

        sys.path.append('./../')
        from sanding_jira import log_hrs
        log_hrs(netids_checked)

        return redirect(url_for('sandingSubmit'))

    return render_template('/layouts/default.html', content = render_template('./pages/sanding.html'))

@app.route('/addParts.html')
def addParts():    
    return render_template('/layouts/default.html', content = render_template('./pages/addParts.html'))


"""
<form method="GET" action="/search" >
    <input type="text" name="make"/>
    <input type="text" name="model"/>
    <input type="submit" value="Submit"/>
</form>

<form method="POST" action="/search_post">
    <input type="text" name="make"/>
    <input type="text" name="model"/>
    <input type="submit" value="Submit"/>
</form>

@app.route("/search")
def do_search():
    make = request.args.get('make')
    model = request.args.get('model')
    return "You search for car make: {0}, and car model: {1}".format(make, model)


# Getting arguements from a POST form
@app.route("/search_post", methods = ['POST'])
def do_post_search():
    make = request.form.get('make')
    model = request.form.get('model')
    return "You search for car make: {0}, and car model: {1}".format(make, model)
"""

# ------------------------------------------------------

# error handling
# most common error codes have been added for now
def http_err(err_code):
	
    err_msg = 'Oups !! Some internal error ocurred. Thanks to contact support.'
	
    if 400 == err_code:
        err_msg = "It seems like you are not allowed to access this link."

    elif 404 == err_code:    
        err_msg  = "The URL you were looking for does not seem to exist."
        err_msg += "<br /> Define the new page in /pages"
    
    elif 500 == err_code:    
        err_msg = "Internal error. Contact the manager about this."

    else:
        err_msg = "Forbidden access."

    return err_msg

@app.errorhandler(401)
def e401(e):
    return http_err( 401) # "It seems like you are not allowed to access this link."

@app.errorhandler(404)
def e404(e):
    return http_err( 404) # "The URL you were looking for does not seem to exist.<br><br>
	                      # If you have typed the link manually, make sure you've spelled the link right."

@app.errorhandler(500)
def e500(e):
    return http_err( 500) # "Internal error. Contact the manager about this."

@app.errorhandler(403)
def e403(e):
    return http_err( 403 ) # "Forbidden access."

@app.errorhandler(410)
def e410(e):
    return http_err( 410) # "The content you were looking for has been deleted."

	