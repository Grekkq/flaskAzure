from collections import defaultdict

import requests
from bs4 import BeautifulSoup
from flask import Flask, redirect, render_template, request

from flaszkaazure.cosmosDb import CosmosDb
from flaszkaazure.models.linkDTO import LinkDTO


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
            sorted_links[link.category].append(link)
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

    @app.route("/delete_link", methods=["GET", "POST"])
    def delete_link():
        link = LinkDTO(
            request.form.get("name"),
            request.form.get("url"),
            request.form.get("category"),
            request.form.get("id"),
        )
        CosmosDb().delete_link(link)
        return redirect("/")

    @app.route("/add_new_link", methods=["GET", "POST"])
    def add_new_link():
        return render_template(
            "content/add-new-link.html",
            category=request.form.get("category"),
            categories=CosmosDb().get_all_categories(),
        )

    @app.route("/submit_add_new_link", methods=["GET", "POST"])
    def submit_add_new_link():
        new_link = LinkDTO(
            request.form.get("name"),
            request.form.get("url"),
            request.form.get("category"),
        )
        CosmosDb().add_link(new_link)
        return redirect("/")

    @app.route("/get_grade", methods=["GET", "POST"])
    def get_grade():
        plate: str = request.args.get("plate")
        plate = plate.upper()
        base_url: str = "https://tablica-rejestracyjna.pl/"
        # use headers to mimic browser, to hopefully not get banned xd
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
        }
        response = requests.get(base_url + plate, headers=headers)
        if response.status_code != 200:
            return f"Plate {plate} not found in external db"

        content = BeautifulSoup(response.content)
        thumb_up = int(content.find("div", {"id": "cnt1"}).text)
        thumb_down = int(content.find("div", {"id": "cnt-1"}).text)
        return f"+{thumb_up}/-{thumb_down}={thumb_up/thumb_down}"

    return app
