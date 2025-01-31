#!/bin/sh
uvicorn src.api.prediction_service:app --reload --host 0.0.0.0 --port 8000 &
uvicorn src.api.performance_service:app --reload --host 0.0.0.0 --port 8001 &
wait