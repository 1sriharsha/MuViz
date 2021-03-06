import configparser

from flask import Flask, render_template, jsonify, request, redirect

from mongo_queries import MongoOperations
import json
app = Flask(__name__)

conf = configparser.ConfigParser()
conf.read("config/application.conf")

mongodb_songs = MongoOperations(conf.get("mongo", "mongo_uri"))
if mongodb_songs.connect(conf.get("mongo", "mongo_db"),
                         conf.get("mongo", "mongo_songs_collection")):
    print("Connection to database successful, continuing application")
else:
    print("Connection unsuccessful, exiting application")
    exit(0)

mongodb_stats = MongoOperations(conf.get("mongo", "mongo_uri"))
if mongodb_stats.connect(conf.get("mongo", "mongo_db"),
                         conf.get("mongo", "mongo_stats_collection")):
    print("Connection to database successful, continuing application")
else:
    print("Connection unsuccessful, exiting application")
    exit(0)

@app.route("/")
def red():
    return redirect("/home")

@app.route("/home")
def home_page():
    return render_template("home.html", btn_classes=["selected", "menu_btn", "menu_btn"])


@app.route("/search")
def search_page():
    return render_template("search.html", btn_classes=["menu_btn", "selected", "menu_btn"])

@app.route("/insert")
def insert_page():
    return render_template("insert.html", btn_classes=["menu_btn", "menu_btn", "selected"])


@app.route("/song")
def song_search():
    if request.args["by"] == "name":
        return jsonify(mongodb_songs.search_song_by_name(request.args["name"]))
    if request.args["by"] == "regex":
        try:
            return jsonify(mongodb_songs.search_song_by_regex(request.args["name"])[0]["name"])
        except Exception as e:
            print(e)
            return jsonify([])

@app.route("/search_by")
def search_by():
    return jsonify(mongodb_songs.exec_query(attribute=request.args["attribute"],
                                            comparision="$" + request.args["comparision"],
                                            value=float(request.args["value"])))


@app.route("/stats")
def stats():
    return jsonify(mongodb_stats.stats())

@app.route("/add_song",methods=["POST"])
def add_song():
    return jsonify(mongodb_songs.insert(json.loads(request.get_data().decode())))

@app.route("/delete_song",methods=["POST"])
def del_song():
    print(json.loads(request.get_data().decode()))
    return jsonify(mongodb_songs.delete(json.loads(request.get_data().decode())["id"]))

@app.route("/update_song",methods=["POST"])
def update_song():
    return jsonify(mongodb_songs.update(json.loads(request.get_data().decode())["id"],json.loads(request.get_data().decode())["values"]))

if __name__ == "__main__":
    app.run(host=conf.get("app", "host"),debug=conf.get("app", "debug"))
