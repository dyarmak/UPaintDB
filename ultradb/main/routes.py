from flask import Blueprint, render_template, request
from ultradb.models import Post
from sqlalchemy import desc

main_bp = Blueprint('main_bp', __name__)

@main_bp.route("/")
@main_bp.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts)


# Basic about page, shows my intentions for the site going forward
@main_bp.route("/about")
def about():
    return render_template('about.html', title='About')