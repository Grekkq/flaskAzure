import sys
import uuid
import flaszkaazure.config as config
from flask import Flask, render_template
import azure.cosmos.cosmos_client as cosmos_client
from collections import defaultdict
from flask import request, redirect


HOST = config.settings["host"]
MASTER_KEY = config.settings["master_key"]
DATABASE_ID = config.settings["database_id"]
CONTAINER_ID = config.settings["container_id"]


def create_app(test_config=None):
    app = Flask(__name__)

    def create_items(container):
        print("\nCreating item\n")
        link_item = {
            "id": f"{uuid.uuid4()}",
            "name": "ciekawylink2",
            "url": "google.com",
            "category": "generic",
        }
        container.create_item(body=link_item)
        link_item = {
            "id": f"{uuid.uuid4()}",
            "name": "YT",
            "url": "youtube.com",
            "category": "fun",
        }
        container.create_item(body=link_item)

    def sorted_links(container):
        # NOTE: Use MaxItemCount on Options to control how many items come back per trip to the server
        #       Important to handle throttles whenever you are doing operations such as this that might
        #       result in a 429 (throttled request)
        links = list(container.read_all_items(max_item_count=10))
        print(f"Found {links.__len__()} links total\n")

        sorted_links = defaultdict(list)
        for link in links:
            sorted_links[link.get("category")].append(link)

        return sorted_links

    @app.route("/")
    def home():
        client = cosmos_client.CosmosClient(
            HOST,
            {"masterKey": MASTER_KEY},
            user_agent="CosmosDBPythonQuickstart",
            user_agent_overwrite=True,
        )
        db = client.get_database_client(DATABASE_ID)
        container = db.get_container_client(CONTAINER_ID)
        sorted = sorted_links(container)
        print("home page")
        return render_template("content/index.html", links=sorted)

    @app.route("/deactivations.html")
    def deactivations():
        return render_template("content/deactivations.html")

    @app.route("/delete_category", methods=["GET", "POST"])
    def delete_category():
        print(f"remove {request.form.get('category')}")
        return redirect("/")

    @app.route("/add_new_link", methods=["GET", "POST"])
    def add_new_link():
        # TODO: Dynamically populate categories
        return render_template(
            "content/add-new-link.html",
            category=request.form.get("category"),
            categories=["Fun", "Training", "internal"],
        )

    @app.route("/submit_add_new_link", methods=["GET", "POST"])
    def submit_add_new_link():
        # TODO: save user data to db
        print(
            f"add {request.form.get('category')} {request.form.get('name')} {request.form.get('url')}",
            file=sys.stderr,
        )
        return redirect("/")

    @app.route("/createItem")
    def create_item():
        client = cosmos_client.CosmosClient(
            HOST,
            {"masterKey": MASTER_KEY},
            user_agent="CosmosDBPythonQuickstart",
            user_agent_overwrite=True,
        )
        db = client.get_database_client(DATABASE_ID)
        container = db.get_container_client(CONTAINER_ID)
        create_items(container)
        return "Created!"

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("content/page-404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("content/page-500.html"), 500

    return app
