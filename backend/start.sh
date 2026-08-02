#!/bin/bash
source venv/Scripts/activate
cd app
uvicorn main:app --reload