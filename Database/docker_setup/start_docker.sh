#!/bin/bash

docker run --name alina -e POSTGRES_DB=alina_database -e POSTGRES_USER=data_team -e POSTGRES_PASSWORD=databaseteamforpresident -p 5432:5432 -d pgvector/pgvector:0.8.0-pg17
