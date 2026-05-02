# Project Overview

This project is a fintech CMS and reconciliation platform.

Purpose:

* reconciliation
* settlement monitoring
* fraud monitoring
* transaction dashboards
* operational management

Architecture:

* FastAPI backend
* React + Vite frontend
* Docker Compose deployment
* Oracle database backend

Important:

* This project does NOT implement the jPOS switch itself.
* The jPOS switch exists in a separate external project.
* This CMS reads transaction and settlement data from Oracle databases populated by external systems.

Future Scope:

* Oracle optimization
* reconciliation engine improvements
* reporting
* fraud analytics
* monitoring dashboards

Guidelines:

* maintain modular architecture
* avoid breaking APIs
* optimize for scalability
* keep Docker compatibility
* prefer enterprise patterns
