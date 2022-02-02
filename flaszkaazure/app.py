import dataclasses
import sys
import uuid
from collections import defaultdict

import azure.cosmos.cosmos_client as cosmos_client
from flask import Flask, redirect, render_template, request

import flaszkaazure.config as config
from flaszkaazure.cosmosDb import CosmosDb
from flaszkaazure.models.linkDTO import LinkDTO

HOST = config.settings["host"]
MASTER_KEY = config.settings["master_key"]
DATABASE_ID = config.settings["database_id"]
CONTAINER_ID = config.settings["container_id"]


def create_app(test_config=None):
    app = Flask(__name__)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("content/page-404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("content/page-500.html"), 500

    def sorted_links():
        links = CosmosDb().get_all_links()
        sorted_links = defaultdict(list)
        for link in links:
            sorted_links[link.get("category")].append(link)
        return sorted_links

    @app.route("/")
    def home():
        return render_template("content/index.html", links=sorted_links())

    @app.route("/deactivations.html")
    def deactivations():
        return render_template("content/deactivations.html")

    @app.route("/delete_category", methods=["GET", "POST"])
    def delete_category():
        CosmosDb().delete_links_by_category(request.form.get("category"))
        return redirect("/")

    @app.route("/add_new_link", methods=["GET", "POST"])
    def add_new_link():
        # TODO: Dynamically populate categories
        return render_template(
            "content/add-new-link.html",
            category=request.form.get("category"),
            categories=CosmosDb().get_all_categories(),
        )

    @app.route("/submit_add_new_link", methods=["GET", "POST"])
    def submit_add_new_link():
        link = LinkDTO(
            request.form.get("name"),
            request.form.get("url"),
            request.form.get("category"),
        )
        CosmosDb().add_link(link)
        return redirect("/")

    return app
