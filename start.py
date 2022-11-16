import os
import webbrowser

webbrowser.open("http://localhost:8000")

os.system(f"pip install -r requirements.txt")
os.system(f"python manage.py migrate")
os.system(f"python manage.py runserver")
input('Press ENTER to exit')