# 🐳 Project 2: Two-Tier App with Docker Compose

> **Level:** Beginner | **Duration:** 3–5 Days | **Difficulty:** 2/10  
> Part of the [10-Project DevOps · AIOps · MLOps Roadmap](https://github.com/YOUR_USERNAME/devops-aiops-mlops-roadmap)

---

## 📌 Overview

Your **first multi-container app** — connect a Python Flask web application to a MySQL database. Both services run as separate Docker containers that communicate over a private Docker network, orchestrated by a single `docker-compose.yml` file.

---

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Your Laptop                               │
│                                                                  │
│   Browser / curl ──► localhost:5000                              │
│                           │                                      │
│                           ▼  Port Mapping (-p 5000:5000)         │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                  Docker Compose Network: app-net           │  │
│  │                                                            │  │
│  │   ┌─────────────────────┐      ┌──────────────────────┐   │  │
│  │   │   flask container   │      │   mysql container    │   │  │
│  │   │                     │      │                      │   │  │
│  │   │  Python Flask app   │─────►│  MySQL 8.0 database  │   │  │
│  │   │  port: 5000         │      │  port: 3306          │   │  │
│  │   │                     │      │                      │   │  │
│  │   │  GET /       → 200  │      │  database: myapp     │   │  │
│  │   │  GET /health → 200  │      │  user:     root      │   │  │
│  │   └─────────────────────┘      └──────────┬───────────┘   │  │
│  │                                            │               │  │
│  │                                   ┌────────▼────────┐      │  │
│  │                                   │  Docker Volume  │      │  │
│  │                                   │    db_data      │      │  │
│  │                                   │ (data persists  │      │  │
│  │                                   │  across restart)│      │  │
│  │                                   └─────────────────┘      │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│   flask-mysql-app/                                               │
│     ├── app.py              (Flask application)                  │
│     ├── requirements.txt    (Python packages)                    │
│     ├── Dockerfile          (builds the Flask image)            │
│     └── docker-compose.yml  (runs both containers together)     │
└─────────────────────────────────────────────────────────────────┘

  Startup order:
  [1] mysql starts → healthcheck passes
  [2] flask starts (depends_on: mysql healthy)
  [3] flask retries DB connection up to 10x (30s wait total)
```

---

## 🧠 What You Learn

| Concept | Description |
|---|---|
| `Docker Compose` | Define and run multi-container apps with one YAML file |
| `Multi-container` | Why apps split into separate services (app vs database) |
| `Networking` | Containers talk to each other by **service name**, not IP |
| `Environment variables` | Pass config (passwords, hostnames) without hardcoding |
| `Volumes` | Persist database data so it survives container restarts |
| `depends_on` | Control startup order — MySQL must be ready before Flask |
| `Healthcheck` | Docker waits for MySQL to *actually* be ready, not just started |

---

## 🚀 Step-by-Step Build

### Prerequisites
- Docker installed (from Project 1)
- Docker Compose v2: `docker compose version`

---

### Step 1 — Create Project Structure

```bash
mkdir flask-mysql-app
cd flask-mysql-app

# Files you will create:
# app.py            — Flask application
# requirements.txt  — Python packages
# Dockerfile        — How to build Flask container
# docker-compose.yml — Run both containers together
```

---

### Step 2 — Write the Flask App (`app.py`)

```python
from flask import Flask
import mysql.connector
import os
import time

app = Flask(__name__)

# UPDATED: Matches the environment keys and defaults in your docker-compose.yml
DB_HOST = os.environ.get("MYSQL_HOST", "mysql")
DB_USER = os.environ.get("MYSQL_USER", "root")
DB_PASSWORD = os.environ.get("MYSQL_PASSWORD", "root")
DB_NAME = os.environ.get("MYSQL_DB", "myapp")

def get_db_connection():
    """Attempts to connect to MySQL with a retry loop because MySQL takes time to boot up."""
    retries = 5
    while True:
        try:
            conn = mysql.connector.connect(
                host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
            )
            return conn
        except mysql.connector.Error as err:
            if retries == 0:
                raise err
            retries -= 1
            print("Database not ready yet. Retrying in 2 seconds...")
            time.sleep(2)

def init_db():
    """Creates a simple hits table if it doesn't exist yet."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS page_views (
            id INT AUTO_INCREMENT PRIMARY KEY,
            view_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    conn.commit()
    cursor.close()
    conn.close()

@app.route("/")
def hello():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO page_views () VALUES ()")
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM page_views")
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return f"<h1>Hello DevOps World!</h1><p>This page has been viewed {count} times.</p>"

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
```

---

### Step 3 — Write `requirements.txt`

```
flask
mysql-connector-python
```

---

### Step 4 — Write the `Dockerfile`

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .
EXPOSE 5000
CMD ["python", "app.py"]
```

---

### Step 5 — Write `docker-compose.yml`

```yaml
version: "3.8"
services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: myapp
    volumes:
      - db_data:/var/lib/mysql
    networks:
      - app-net
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-uroot", "-proot"]
      interval: 10s
      retries: 5

  flask:
    build: .
    ports:
      - "5000:5000"
    environment:
      MYSQL_HOST: mysql
      MYSQL_USER: root
      MYSQL_PASSWORD: root
      MYSQL_DB: myapp
    networks:
      - app-net
    depends_on:
      mysql:
        condition: service_healthy

volumes:
  db_data:
networks:
  app-net:
```

---

### Step 6 — Start Everything

```bash
# Start all containers with one command
docker compose up -d

# Check both containers are running
docker compose ps

# Test the app
curl http://localhost:5000/
curl http://localhost:5000/health

# See live logs from both containers
docker compose logs -f

# Stop everything
docker compose down
```

---

## ✅ Expected Output

```json
// GET http://localhost:5000/
{"db": "connected", "status": "ok"}

// GET http://localhost:5000/health
{"status": "healthy"}
```

---

## 📁 Final Project Structure

```
flask-mysql-app/
├── app.py               ← Flask application
├── requirements.txt     ← Python packages
├── Dockerfile           ← Builds the Flask image
├── docker-compose.yml   ← Orchestrates both containers
└── README.md            ← This file
```

---

## 🔧 Tools Used

![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![Docker Compose](https://img.shields.io/badge/Docker_Compose-2496ED?style=flat&logo=docker&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=flat&logo=flask&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=flat&logo=mysql&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)

---

## 🔍 Key Concept: Container Networking

In Docker Compose, containers on the same network talk to each other **by service name**:

```python
# This works because Docker DNS resolves "mysql" → container IP
MYSQL_HOST: mysql    # NOT localhost, NOT an IP address
```

This is why `localhost` would FAIL — Flask and MySQL are in **separate containers**.

---

## ➡️ Next Step

You can now run a multi-container app. Move to **[Project 3 — CI/CD Pipeline with Jenkins](../project-03-jenkins-cicd/)** to automate deployment — every git push deploys automatically.

---

## 📚 Full 10-Project Roadmap

| # | Project | Level |
|---|---------|-------|
| **1** | Static Website with Docker | Beginner |
| **2** | **Two-Tier App with Docker Compose** ← *You are here* | Beginner |
| 3 | CI/CD Pipeline with Jenkins | Beginner |
| 4 | Kubernetes on Local Cluster (Minikube) | Intermediate |
| 5 | Monitoring Stack: Prometheus + Grafana | Intermediate |
| 6 | AI Log Analyzer (AIOps Entry) | Intermediate |
| 7 | Predictive Anomaly Detection (AIOps Advanced) | Advanced |
| 8 | Deploy an ML Model as an API | Advanced |
| 9 | MLflow: Model Versioning & Experiment Tracking | Pro |
| 10 | Full Production System — All Three Combined | Pro |