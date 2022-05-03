import configparser

from flask import Flask, render_template, jsonify, request

from mongo_queries import MongoOperations

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


@app.route("/home")
def home_page():
    return render_template("home.html", btn_classes=["selected", "menu_btn", "menu_btn"])


@app.route("/search")
def search_page():
    return render_template("search.html", btn_classes=["menu_btn", "selected", "menu_btn"])


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


if __name__ == "__main__":
    app.run(debug=True)
