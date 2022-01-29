import config
from flask import Flask
from pathlib import Path
import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client

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
            "id": "1",
            "name": "ciekawylink1",
            "link": "google.com",
        }
        container.create_item(body=link_item)

    def read_items(container):
        print("\nReading all items in a container\n")

        # NOTE: Use MaxItemCount on Options to control how many items come back per trip to the server
        #       Important to handle throttles whenever you are doing operations such as this that might
        #       result in a 429 (throttled request)
        item_list = list(container.read_all_items(max_item_count=10))
        items_string = ""
        items_string += f"Found {item_list.__len__()} items\n"

        for doc in item_list:
            items_string += f"Item Id: {doc.get('id')}\n"

        return items_string

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
        return read_items(container)

    @app.route("/hello")
    def hello():
        return "No hej!"

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


if __name__ == "__main__":
    app = create_app()
    app.run()
