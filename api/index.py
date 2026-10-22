import sys
import os

# Ensure the project root directory is on Python search path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app import app

# Ensure Flask locates templates and static folders relative to ROOT_DIR on Vercel
templates_dir = os.path.join(ROOT_DIR, "templates")
static_dir = os.path.join(ROOT_DIR, "static")

if os.path.isdir(templates_dir):
    app.template_folder = templates_dir
if os.path.isdir(static_dir):
    app.static_folder = static_dir
