from flask import Flask, render_template, url_for, request, redirect, flash
import csv, os, re
from sqlalchemy import text
from dotenv import load_dotenv
from models import db, Comment

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-me")

if not app.config["SQLALCHEMY_DATABASE_URI"]:
    raise RuntimeError("DATABASE_URL is not set")


db.init_app(app)
with app.app_context():
    db.create_all()

CONTACTS_FILE = os.path.join(BASE_DIR, "database.csv")
print("Using database file at:", CONTACTS_FILE)

def write_to_csv(data):
    with open(CONTACTS_FILE, mode='a') as database:
        name = data["name"]
        email = data["email"]
        subject = data["subject"]
        message = data["message"]
        csv_writer = csv.writer(database, delimiter=',',
                                quotechar=' ', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow([name, email, subject, message])

@app.route('/submit_form', methods=['POST', 'GET'])
def submit_form():
    if request.method == 'POST':
        try:
            data = request.form.to_dict()
            write_to_csv(data)
            print(data)
            return redirect('thankyou.html')
        except:
            return 'Unable to save to database'
    else:
        return 'Error in Sending. Please try again.'

@app.route('/')
def my_home():
    return render_template("index.html")


@app.route('/events/<page_name>')
def event_page(page_name):
    template_path = f"events/{page_name}.html"
    slug = page_name
    comments = get_thread_comments(thread=slug)
    return render_template(template_path, thread=slug, comments=comments)


@app.route('/<string:page_name>')
def html_page(page_name):
    return render_template(page_name)

URL_RE = re.compile(r'^https?://', re.IGNORECASE)

def get_thread_comments(thread: str):
    """Return a structure: roots, replies_by_parent for rendering."""
    items = (Comment.query
             .filter_by(thread=thread, is_approved=True)
             .order_by(Comment.created_at.asc())
             .all())
    roots = [c for c in items if c.parent_id is None]
    replies_by_parent = {}
    for c in items:
        if c.parent_id:
            replies_by_parent.setdefault(c.parent_id, []).append(c)
    return {"roots": roots, "replies": replies_by_parent}

@app.post("/comments/<thread>")
def post_comment(thread):
    if request.form.get("website"):
        flash("Thanks!")
        return redirect(request.referrer or url_for('html_page', page_name='index.html'))

    name = (request.form.get("name") or "").strip()
    text = (request.form.get("comment") or "").strip()
    social = (request.form.get("social") or request.form.get("website") or "").strip() 
    parent_id = request.form.get("parent_id") or None
    parent_id = int(parent_id) if parent_id and parent_id.isdigit() else None

    if not name or not text:
        flash("Name and comment are required.")
        return redirect(request.referrer or url_for('html_page', page_name='index.html'))

    if social and not URL_RE.match(social):
        social = "https://" + social

    c = Comment(thread=thread, parent_id=parent_id, name=name[:80],
                social_url=social[:255] if social else None, text=text)
    db.session.add(c)
    db.session.commit()
    flash("Comment posted!")

    return redirect((request.referrer or url_for('html_page', page_name='index.html')) + "#blog-comments")


@app.route("/show-comments")
def show_comments():
    rows = db.session.execute(
        text("SELECT * FROM comments ORDER BY id DESC")
    ).fetchall()
    return "<pre>" + "\n".join(map(str, rows)) + "</pre>"

@app.route("/db-debug")
def db_debug():
    uri = app.config["SQLALCHEMY_DATABASE_URI"]
    search_path = db.session.execute(text("SHOW search_path")).scalar()
    current_schema = db.session.execute(text("SELECT current_schema()")).scalar()
    tbl = Comment.__table__
    full = f'{(tbl.schema + ".") if tbl.schema else ""}{tbl.name}'
    return (
        "<pre>"
        f"URI: {uri}\n"
        f"search_path: {search_path}\n"
        f"current_schema(): {current_schema}\n"
        f"Comment table: {full}\n"
        "</pre>"
    )