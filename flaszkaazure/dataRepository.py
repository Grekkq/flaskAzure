from abc import ABC, ABCMeta, abstractmethod

from flaszkaazure.models.linkDTO import LinkDTO


class DataRepository(ABC):
    @abstractmethod
    def add_link(self, link: LinkDTO):
        pass

    @abstractmethod
    def get_all_links(self):
        pass

    @abstractmethod
    def get_all_categories(self):
        pass

    @abstractmethod
    def delete_links_by_category(self, category: str):
        pass

    @abstractmethod
    def delete_link(self, link: LinkDTO):
        pass
