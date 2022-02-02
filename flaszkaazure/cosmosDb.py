import dataclasses
import azure.cosmos.cosmos_client as cosmos_client

import flaszkaazure.config as config
from flaszkaazure.dataRepository import DataRepository
from flaszkaazure.models.linkDTO import LinkDTO

HOST = config.settings["host"]
MASTER_KEY = config.settings["master_key"]
DATABASE_ID = config.settings["database_id"]
CONTAINER_ID = config.settings["container_id"]


class CosmosDb(DataRepository):
    instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = super(DataRepository, cls).__new__(cls, *args, **kwargs)
            client = cosmos_client.CosmosClient(
                HOST,
                {"masterKey": MASTER_KEY},
                user_agent="CosmosDBPythonQuickstart",
                user_agent_overwrite=True,
            )
            cls.db = client.get_database_client(DATABASE_ID)
            cls.link_container = cls.db.get_container_client(CONTAINER_ID)
        return cls.instance

    def add_link(self, link: LinkDTO):
        self.link_container.create_item(body=dataclasses.asdict(link))

    def delete_link(self, link: LinkDTO):
        self.link_container.delete_item(link.id, link.category)

    def delete_links_by_category(self, category: str):
        for link in self.get_all_links():
            link = LinkDTO(
                link.get("name"), link.get("url"), link.get("category"), link.get("id")
            )
            if link.category == category:
                self.delete_link(link)

    def get_all_links(self):
        # NOTE: Use MaxItemCount on Options to control how many items come back per trip to the server
        #       Important to handle throttles whenever you are doing operations such as this that might
        #       result in a 429 (throttled request)
        return list(self.link_container.read_all_items(max_item_count=10))

    def get_all_categories(self):
        query_result = self.link_container.query_items(
            "SELECT DISTINCT c.category FROM c",
            enable_cross_partition_query=True,
        )
        categories = [item.get("category") for item in query_result]
        return categories
