from flask import Blueprint, render_template, request, flash, jsonify

from flask_login import login_required, current_user


views = Blueprint('views', __name__) 
# blueprint allows u to use URL so you dont have to put urls in one file 
#-> check authen

@views.route('/', methods=['GET', 'POST']) # http methods = gets and post  
@login_required
def home():
    return render_template("home.html", user=current_user) # return the html from home 
