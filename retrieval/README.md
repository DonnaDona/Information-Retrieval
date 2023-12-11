# Retrieval Module

This folder contains the file that create and interact with the index.

## Folder structure

- **indexer.py**: Functions to create the index and save it to disk.
- **loader.py**: Functions to load the data from the database and save it to disk.
- **retriever.py**: Functions to interact with the index and retrieve the results. This file is used by the Django API.
- **main.py**: This file is the entry point for the index creation.

## Create the index
A prerequisite to create the index is to have the environment variables for the database connection.
This module uses, like all the other modules, the `.env` file in the root folder of the project.

To create the index, run the following command:
```bash
python main.py
```
from the `retrieval` folder.

Running the command will start loading data from the database and index it, storing the index in the `index` folder.

The progress of the index creation will be printed on the console.

