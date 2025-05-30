#!/bin/bash

# Start the RQ worker in the background
rq worker --url redis://host.docker.internal &

# Start FastAPI (uvicorn)
exec uvicorn main:app --host 0.0.0.0 --port 8000
