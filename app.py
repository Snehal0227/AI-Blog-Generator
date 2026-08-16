from groq import Groq
from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from urllib.parse import quote
from models import db, User, Blog, Visitor
import os
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__)

# ==========================
# APP CONFIG
# ==========================

app.config["SECRET_KEY"] = "ai_blog_generator_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ==========================
# GROQ
# ==========================

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# ==========================
# UPLOAD FOLDER
# ==========================

UPLOAD_FOLDER = "static/uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)



# ==========================
# HOME
# ==========================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ==========================
# FEATURES
# ==========================

@app.route("/features")
def features():

    return render_template(
        "features.html"
    )


# ==========================
# CONTACT
# ==========================

@app.route(
    "/contact",
    methods=["GET", "POST"]
)
def contact():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        subject = request.form.get("subject")
        message = request.form.get("message")

        print("Name:", name)
        print("Email:", email)
        print("Subject:", subject)
        print("Message:", message)

        return render_template(
            "contact.html",
            success="Your message has been sent successfully! 😊"
        )

    return render_template(
        "contact.html"
    )


# ==========================
# LOGIN
# ==========================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(
            email=email,
            password=password
        ).first()

        if user:

            session["user_id"] = user.id

            flash(
                "Login Successful"
            )

            return redirect(
                "/dashboard"
            )

        else:

            flash(
                "Invalid Email or Password"
            )

    return render_template(
        "login.html"
    )


# ==========================
# REGISTER
# ==========================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        fullname = request.form.get(
            "fullname"
        )

        email = request.form.get(
            "email"
        )

        password = request.form.get(
            "password"
        )

        confirm_password = request.form.get(
            "confirm_password"
        )

        if password != confirm_password:

            flash(
                "Password and Confirm Password do not match"
            )

            return redirect(
                "/register"
            )

        check_user = User.query.filter_by(
            email=email
        ).first()

        if check_user:

            flash(
                "Email already exists"
            )

            return redirect(
                "/register"
            )

        user = User(
            fullname=fullname,
            email=email,
            password=password
        )

        db.session.add(user)
        db.session.commit()

        flash(
            "Registration Successful"
        )

        return redirect(
            "/login"
        )

    return render_template(
        "register.html"
    )


# ==========================
# DASHBOARD
# ==========================

@app.route("/dashboard")
def dashboard():

    total_blogs = Blog.query.count()

    ai_blogs = Blog.query.filter(
        Blog.category.ilike("%AI%")
    ).count()

    categories = db.session.query(
        Blog.category
    ).filter(
        Blog.category.isnot(None),
        Blog.category != ""
    ).distinct().count()

    recent_blogs = Blog.query.order_by(
        Blog.created_at.desc()
    ).limit(5).all()

    return render_template(
        "dashboard.html",
        total_blogs=total_blogs,
        ai_blogs=ai_blogs,
        categories=categories,
        recent_blogs=recent_blogs
    )


# ==========================
# AI BLOG GENERATION
# ==========================

@app.route(
    "/generate_ai",
    methods=["POST"]
)
def generate_ai():

    title = request.form["title"]

    keywords = request.form.get(
        "keywords",
        ""
    )

    length = request.form.get(
        "length",
        "Medium (1000 Words)"
    )

    prompt = f"""
Write a professional blog on the topic:
{title}

Use these keywords:
{keywords}

The blog should have:
- Introduction
- Main Content
- Conclusion

Blog Length:
{length}
"""

    try:

        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        blog_content = (
            response
            .choices[0]
            .message
            .content
        )

        image_url = (
            "https://loremflickr.com/800/500/"
            + quote(title)
            + "?random=1"
        )

        fallback_path = (
            "/static/images/fallback-cover.jpg"
        )

        return {
            "content": blog_content,
            "ai_image": image_url,
            "fallback_image": fallback_path
        }

    except Exception as e:

        print(
            "AI ERROR:",
            e
        )

        return {
            "content": "",
            "ai_image": "/static/images/fallback-cover.jpg",
            "fallback_image": "/static/images/fallback-cover.jpg",
            "error": str(e)
        }


# ==========================
# CREATE BLOG
# ==========================

@app.route(
    "/create_blog",
    methods=["GET", "POST"]
)
def create_blog():

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        category = request.form.get(
            "category",
            ""
        )

        content = request.form.get(
            "content",
            ""
        )

        filename = ""

        # AI IMAGE

        ai_image_url = request.form.get(
            "ai_image_url",
            ""
        )

        if ai_image_url:

            try:

                response = requests.get(
                    ai_image_url,
                    timeout=10
                )

                if response.status_code == 200:

                    filename = secure_filename(
                        title.replace(
                            " ",
                            "_"
                        ) + "_ai.jpg"
                    )

                    image_path = os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        filename
                    )

                    with open(
                        image_path,
                        "wb"
                    ) as f:

                        f.write(
                            response.content
                        )

            except Exception as e:

                print(
                    "AI IMAGE ERROR:",
                    e
                )

        # USER IMAGE

        if "image" in request.files:

            image = request.files.get(
                "image"
            )

            if image and image.filename:

                filename = secure_filename(
                    image.filename
                )

                image_path = os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )

                image.save(
                    image_path
                )

        # SAVE BLOG

        blog = Blog(

            title=title,

            category=category,

            content=content,

            image=filename,

            ai_image=filename,

            user_id=1
        )

        db.session.add(blog)

        db.session.commit()

        flash(
            "Blog Created Successfully"
        )

        return redirect(
            url_for("myblogs")
        )

    return render_template(
        "create_blog.html"
    )


# ==========================
# MY BLOGS
# ==========================

@app.route("/myblogs")
def myblogs():

    search = request.args.get(
        "search",
        ""
    )

    if search:

        blogs = Blog.query.filter(
            Blog.title.contains(search)
        ).all()

    else:

        blogs = Blog.query.order_by(
            Blog.id.desc()
        ).all()

    return render_template(
        "myblogs.html",
        blogs=blogs,
        search=search
    )


# ==========================
# VIEW BLOG
# ==========================

@app.route(
    "/blog/<int:blog_id>"
)
def view_blog(blog_id):

    blog = Blog.query.get_or_404(
        blog_id
    )

    blog.views +=1
    db.session.commit()

    return render_template(
        "blog.html",
        blog=blog
    )
# ==========================
# ANALYTICS
# ==========================

@app.route("/analytics")
def analytics():

    # --------------------------
    # CONTENT INSIGHTS
    # --------------------------

    total_blogs = Blog.query.count()

    ai_blogs = Blog.query.filter(
        Blog.category.ilike("%AI%")
    ).count()

    categories = db.session.query(
        Blog.category
    ).filter(
        Blog.category.isnot(None),
        Blog.category != ""
    ).distinct().count()


    # --------------------------
    # BEST PERFORMING BLOGS
    # --------------------------

    best_blogs = Blog.query.order_by(
        Blog.views.desc()
    ).limit(4).all()


    # --------------------------
    # TOP BLOG
    # --------------------------

    top_blog = Blog.query.order_by(
        Blog.views.desc()
    ).first()


    # --------------------------
    # TOTAL VIEWS
    # --------------------------

    total_views = db.session.query(
        db.func.coalesce(
            db.func.sum(Blog.views), 0
        )
    ).scalar()


    # --------------------------
    # AUDIENCE
    # --------------------------

    total_audience = Visitor.query.count()

    new_visitors = Visitor.query.filter_by(
        is_new=True
    ).count()

    returning_visitors = Visitor.query.filter_by(
        is_new=False
    ).count()


    # --------------------------
    # TOP LOCATION
    # --------------------------

    top_location = db.session.query(
        Visitor.location,
        db.func.count(Visitor.id)
    ).filter(
        Visitor.location.isnot(None),
        Visitor.location != ""
    ).group_by(
        Visitor.location
    ).order_by(
        db.func.count(Visitor.id).desc()
    ).first()


    # --------------------------
    # MAIN DEVICE
    # --------------------------

    main_device = db.session.query(
        Visitor.device,
        db.func.count(Visitor.id)
    ).filter(
        Visitor.device.isnot(None),
        Visitor.device != ""
    ).group_by(
        Visitor.device
    ).order_by(
        db.func.count(Visitor.id).desc()
    ).first()


    # --------------------------
    # CATEGORY PERFORMANCE
    # --------------------------

    category_data = db.session.query(
        Blog.category,
        db.func.count(Blog.id)
    ).filter(
        Blog.category.isnot(None),
        Blog.category != ""
    ).group_by(
        Blog.category
    ).order_by(
        db.func.count(Blog.id).desc()
    ).all()


    return render_template(
        "analytics.html",

        total_blogs=total_blogs,
        ai_blogs=ai_blogs,
        categories=categories,

        total_views=total_views,
        top_blog=top_blog,
        best_blogs=best_blogs,

        total_audience=total_audience,
        new_visitors=new_visitors,
        returning_visitors=returning_visitors,

        top_location=top_location,
        main_device=main_device,

        category_data=category_data
    )

# ==========================
# AI GENERATE PAGE
# ==========================

@app.route("/ai_generate")
def ai_generate():

    return render_template(
        "ai_generate.html"
    )


# ==========================
# PROFILE
# ==========================

@app.route(
    "/profile",
    methods=["GET", "POST"]
)
def profile():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        bio = request.form["bio"]

        print("Name:", name)
        print("Email:", email)
        print("Bio:", bio)

        flash(
            "Profile Updated Successfully!"
        )

        return redirect(
            url_for("profile")
        )

    return render_template(
        "profile.html"
    )


# ==========================
# SETTINGS
# ==========================

@app.route(
    "/settings",
    methods=["GET", "POST"]
)
def settings():

    if request.method == "POST":

        password = request.form.get(
            "password"
        )

        notifications = request.form.get(
            "notifications"
        )

        dark_mode = request.form.get(
            "dark_mode"
        )

        language = request.form.get(
            "language"
        )

        print(
            "Password:",
            password
        )

        print(
            "Notifications:",
            notifications
        )

        print(
            "Dark Mode:",
            dark_mode
        )

        print(
            "Language:",
            language
        )

        flash(
            "Settings Saved Successfully!"
        )

        return redirect(
            url_for("settings")
        )

    return render_template(
        "settings.html"
    )


# ==========================
# EDIT BLOG
# ==========================

@app.route(
    "/edit_blog/<int:id>",
    methods=["GET", "POST"]
)
def edit_blog(id):

    blog = Blog.query.get_or_404(id)

    if request.method == "POST":

        blog.title = request.form[
            "title"
        ]

        blog.category = request.form[
            "category"
        ]

        blog.content = request.form[
            "content"
        ]

        image = request.files.get(
            "image"
        )

        if image and image.filename != "":

            filename = secure_filename(
                image.filename
            )

            image.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

            blog.image = filename

        db.session.commit()

        flash(
            "Blog Updated Successfully"
        )

        return redirect(
            "/myblogs"
        )

    return render_template(
        "edit_blog.html",
        blog=blog
    )


# ==========================
# DELETE BLOG
# ==========================

@app.route(
    "/delete_blog/<int:id>"
)
def delete_blog(id):

    blog = Blog.query.get_or_404(
        id
    )

    db.session.delete(blog)

    db.session.commit()

    flash(
        "Blog Deleted Successfully"
    )

    return redirect(
        "/myblogs"
    )


# ==========================
# LOGOUT
# ==========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# ==========================
# CREATE DATABASE
# ==========================

with app.app_context():

    db.create_all()


# ==========================
# RUN
# ==========================

if __name__ == "__main__":

    app.run(
        debug=True
    )