import uuid
import flaszkaazure.config as config
from flask import Flask, render_template
from pathlib import Path
import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
from collections import defaultdict


HOST = config.settings["host"]
MASTER_KEY = config.settings["master_key"]
DATABASE_ID = config.settings["database_id"]
CONTAINER_ID = config.settings["container_id"]


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        # DATABASE=Path.joinpath(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

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
            sorted_links[link.category].append(link)

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
        return render_template("home/index.html", links=sorted_links(container))

    @app.route("/base")
    def base():
        links = (
            {
                "Fun": [{"url": "youtube.com", "name": "YT"}],
                "Training": [
                    {"url": "pluarsight", "name": "pluralsight"},
                    {"url": "youtube.com", "name": "YT"},
                ],
            },
        )

        return render_template("home/index.html", links=links)

    @app.route("/hello")
    def hello():
        return render_template("hello.html")

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

    return app
