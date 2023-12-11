# Backend

## Setup
The backend requires all the variables of the `.env.template` file to be set in the `.env` file.

The backend can be run with the following command:
```bash
python manage.py runserver
```

## API
The API is available at the `/api` endpoint.

The following endpoints are available:
- `/api/search/`: Retrieve movies based on a query
- `/api/recommend/`: Retrieve recommendations based on a query
