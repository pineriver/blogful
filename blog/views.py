from flask import render_template

from . import app
from .database import session, Entry

PAGINATE_BY = 10

@app.route("/")
@app.route("/page/<int:page>")
def entries(page=1):
    # Zero-indexed page
    page_index = page - 1
    
    count = session.query(Entry).count()
    
    start = page_index * PAGINATE_BY
    end = start + PAGINATE_BY
    
    total_pages = (count - 1) // PAGINATE_BY + 1
    has_next = page_index < total_pages - 1
    has_prev = page_index > 0 
    
    entries = session.query(Entry)
    entries = entries.order_by(Entry.datetime.desc())
    entries = entries[start:end]
    
    return render_template("entries.html", 
        entries=entries, 
        has_next=has_next, 
        has_prev=has_prev,
        page=page, 
        total_pages=total_pages
    )
    


@app.route("/entry/add", methods=["GET"])

def add_entry():
    return render_template("add_entry.html")
    
from flask import request, redirect, url_for
from flask_login import current_user

@app.route("/entry/add", methods=["POST"])

def add_entry_post():
    entry = Entry(
        title=request.form["title"],
        content=request.form["content"],
        author=current_user
    )
    session.add(entry)
    session.commit()
    return redirect(url_for("entries"))
    
@app.route('/entry/<int:entry_id>')
def entry(entry_id):
    entry = session.query(Entry).filter(Entry.id==entry_id).first()
    return render_template('entry_view.html', entry=entry)
    
@app.route("/entry/<int:entry_id>/edit", methods=["GET"])
def edit_entry_get(entry_id):
    entry = session.query(Entry).filter(Entry.id==entry_id).first()
    title = entry.title
    content = entry.content
    return render_template("entry_edit.html",
        title=title, 
        content=content, 
        entry=entry)
        
@app.route("/entry/<int:entry_id>/delete", methods=["GET"])
def delete_entry(entry_id):
    entry = session.query(Entry).filter(Entry.id==entry_id).delete()
    session.commit()
    return redirect(url_for("entries"))
    

@app.route("/login", methods=["GET"])
def login_get():
    return render_template("login.html")
    
    
from flask import flash
from flask_login import login_user
from werkzeug.security import check_password_hash
from .database import User

@app.route("/login", methods=["POST"])
def login_post():
    email = request.form["email"]
    password = request.form["password"]
    user = session.query(User).filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        flash("Incorrect username or password", "danger")
        return redirect(url_for("login_get"))
        
    login_user(user)
    return redirect(request.args.get('next') or url_for("entries"))
    
    