#!/bin/bash

# import all variables in .env as environment variables
set -a
source .env
set +a

# .env contains USERNAME, PASSWORD, HOST and DATABASE. Use this information to create a database with postgres
psql -c "CREATE DATABASE $DATABASE;" -U $USERNAME -h $HOST -p $PORT