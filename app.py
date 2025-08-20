# Routes
@app.route("/")
def intro():
    if os.getenv("SKIP_INTRO") == "1":
        return render_template("index.html")
    return render_template("intro.html")

@app.route("/skip-intro")
def skip_intro():
    os.environ["SKIP_INTRO"] = "1"
    return redirect("/home")

@app.route("/home")
def index():
    return render_template("index.html")
