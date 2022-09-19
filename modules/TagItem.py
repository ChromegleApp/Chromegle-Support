import json
import time

import config


class TagItem:

    path = config.DATA_PATH

    def __init__(self, name):
        """
        Load a tag
        """

        data: dict = self.__load_data()
        item_path: dict = data['tags'][name]

        self.raw_data = item_path

        # Object Data
        self.name = item_path['name']
        self.label = item_path['label']
        self.message = item_path['message']
        self.owner = item_path['owner_id']
        self.create_time = item_path['create_time']
        self.embed = item_path['embed_bool']

    @staticmethod
    def __load_data():
        """
        Load the data file into a dict
        """

        with open(TagItem.path) as file:
            return json.loads(file.read())

    @staticmethod
    def __write_data(data: dict):
        """
        Write the data file from a dict
        """

        with open(TagItem.path, 'w') as file:
            file.write(json.dumps(data, indent=4))

    @staticmethod
    def update_embed_bool(name: str, val: bool):
        data: dict = TagItem.__load_data()
        data['tags'][name]['embed_bool'] = val
        TagItem.__write_data(data)

    @staticmethod
    def write_tag(name: str, message: str, owner_id: int, embed: bool):
        """
        Generate a tag from specified params
        """
        data: dict = TagItem.__load_data()
        name = name.lower()

        data['tags'][name]: dict = {
            'name': name,
            'label': name,
            'message': message,
            'owner_id': owner_id,
            'embed_bool': embed,
            'create_time': time.time()
        }

        TagItem.__write_data(data)

    @staticmethod
    def remove_tag(name: str):
        """
        Remove a tag given its name
        """

        data: dict = TagItem.__load_data()
        del data['tags'][name]
        TagItem.__write_data(data)

    @staticmethod
    def get_tags():
        """
        Get all tags
        """

        return [TagItem(tag) for tag in TagItem.__load_data()['tags'].keys()]
