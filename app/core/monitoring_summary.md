# Monitoring and Logging Summary

## Overview

This project includes structured logging and latency tracking for a production-style Enterprise AI Knowledge Assistant.

The goal of monitoring is to make the RAG system easier to debug, measure, and explain.

---

## Logging

The application uses Python logging with both console and file-based log handlers.

Logs are written to:

```text
logs/app.log