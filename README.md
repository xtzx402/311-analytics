# NYC 311 Analytics Platform

A full-stack analytics platform for exploring NYC 311 service request data, 
powered by FastAPI, PostgreSQL, Vue.js, and an AI assistant via MCP.

## Features
- Query and filter 311 complaints by type, borough, date range
- Interactive map visualization with Leaflet
- Statistical dashboard with charts
- AI-powered natural language queries via MCP

## Tech Stack
| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + SQLAlchemy |
| Database | PostgreSQL |
| Frontend | Vue.js + Leaflet + Chart.js |
| AI | Claude/GPT + MCP Server |
| DevOps | Docker + GitHub Actions |

## Architecture
User (Vue.js)
↓ HTTP
FastAPI Backend
↓
PostgreSQL
↓
MCP Server 
↓
LLM


## Getting Started
(coming soon)