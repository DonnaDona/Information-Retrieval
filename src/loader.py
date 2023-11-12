import json


def load_crawled_data(file_path):
    with open(file_path, 'r') as file:
        crawled_data = json.load(file)
    return crawled_data
