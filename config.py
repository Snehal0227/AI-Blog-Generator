import os
class Config:

    SECRET_KEY = "ai_blog_secret_key"

    SQLALCHEMY_DATABASE_URI = "sqlite:///blog.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_IMAGE = "static/uploads/images"

    UPLOAD_VIDEO = "static/uploads/videos"

    GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"