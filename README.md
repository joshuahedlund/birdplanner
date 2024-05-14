This is a project to help plan a birding trip by analyzing data from eBird and recommending hotspots based on various criteria. It is a work in progress.

Required packages:
flask
flask_sqlalchemy
pandas
pymysql
requests

Requried config.py file:
EBIRD_API_KEY = "{YOUR_KEY_HERE}"
DATABASE_URI = 'mysql+pymysql://root@localhost:3306/birdplanner'