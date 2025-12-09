Here’s a complete README you can drop straight into `README.md` and tweak. I’ll assume the project name is **ChainRisk Sentinel** (you can change it globally if you like).

---

# ChainRisk Sentinel

ChainRisk Sentinel is an on-chain wallet risk & anomaly monitor.

It periodically ingests Ethereum transactions for selected wallets from the Etherscan API, scores each transaction using simple rule-based risk logic (large transfers, bursts of activity, risky counterparties), stores everything in PostgreSQL, and exposes a FastAPI-powered JSON API plus a lightweight HTML dashboard for browsing transactions and alerts.

The whole system is dockerized and can be run either with Docker Compose (recommended) or directly on your local machine.


## Prerequisites

### For Docker / Docker Compose (recommended)

* [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed
* Docker Compose (bundled with recent Docker Desktop versions)

### For Local (no Docker) setup

* Python 3.11+
* PostgreSQL 14+ installed and running on your machine
* `pip` for installing project dependencies

---

## Environment Variables

The project reads configuration from environment variables. In development, you typically define them in a `.env` file.

### Required variables

* `DATABASE_URL`
  PostgreSQL connection string. Pattern:

  ```text
  postgresql://<user>:<password>@<host>:<port>/<dbname>
  ```

* `ETHERSCAN_API_KEY`
  API key obtained from Etherscan (free accounts get a key from the user dashboard).

* `MONITORED_ADDRESSES`
  Comma-separated list of Ethereum addresses you want to monitor (mainnet):

  ```env
  MONITORED_ADDRESSES=0xAddress1,0xAddress2,0xAddress3
  ```

* `POLL_INTERVAL_SECONDS`
  How often the ingestor polls Etherscan for each address (e.g. `60` for every 60 seconds).

---

## Quick Start with Docker Compose (recommended)

This is the easiest way to run everything.

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/chainrisk-sentinel.git
cd chainrisk-sentinel
```

### 2. Create a `.env` file (for Docker)

In the project root (same folder as `docker-compose.yml`), create `.env`:

```env
# Etherscan API key (required)
ETHERSCAN_API_KEY=YOUR_REAL_API_KEY_HERE

# Comma-separated Ethereum addresses to monitor
MONITORED_ADDRESSES=0xC36442b4a4522E871399CD717aBDD847Ab11FE88,0x3f5CE5FBFe3E9af3971dD833D26BA9b5C936f0bE,0x564286362092D8e7936f0549571a803B203aAceD

# Polling interval in seconds
POLL_INTERVAL_SECONDS=60
```

> **Note:** In Docker, `DATABASE_URL` is set inside `docker-compose.yml` and uses `db` as the host (the Postgres service name), so you don’t need to define it manually for the containers.

### 3. Start the stack

```bash
docker-compose up --build
```

This will:

* Pull the Postgres image
* Build an image for the app
* Start three services:

  * `db` (PostgreSQL)
  * `api` (FastAPI + dashboard)
  * `ingestor` (Etherscan → Postgres worker)

### 4. Open the dashboard

Once you see logs like:

```text
api_1       | Uvicorn running on http://0.0.0.0:8000
ingestor_1  | Starting ingestion loop for: [...]
db_1        | database system is ready to accept connections
```

Open:

* Dashboard: [http://localhost:8000/](http://localhost:8000/)
* Raw JSON: [http://localhost:8000/transactions](http://localhost:8000/transactions)
* Health check: [http://localhost:8000/health](http://localhost:8000/health)

You should see:

* In the terminal: `ingestor` logs like
  `Stored tx 0x... for 0x... with risk LOW/MEDIUM`
* In the browser: transactions populate the table, and risk badges show LOW/MEDIUM/HIGH labels.

### 5. Stopping everything

Press `Ctrl + C` in the terminal running `docker-compose up`, then clean up:

```bash
docker-compose down
```

To start again later:

```bash
docker-compose up
```

(Use `--build` again only if you changed Python code or `requirements.txt`.)

---

## Local Setup (without Docker)

If you prefer to run everything directly on your machine:

### 1. Clone the repo

```bash
git clone https://github.com/<your-username>/chainrisk-sentinel.git
cd chainrisk-sentinel
```

### 2. Set up Python environment

Optional but recommended:

```bash
python -m venv venv
source venv/bin/activate   # on Linux/macOS
venv\Scripts\activate      # on Windows
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Start PostgreSQL and create a database

Make sure PostgreSQL is running locally, then create a database named `onchain_monitor`:

* Using `psql`:

  ```bash
  psql -U postgres -h localhost -p 5432
  CREATE DATABASE onchain_monitor;
  \q
  ```

Or create it via a GUI (pgAdmin) with the same name.

### 4. Create `.env` for local development

In the project root:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/onchain_monitor
ETHERSCAN_API_KEY=YOUR_REAL_API_KEY_HERE
MONITORED_ADDRESSES=0xC36442b4a4522E871399CD717aBDD847Ab11FE88,0x3f5CE5FBFe3E9af3971dD833D26BA9b5C936f0bE,0x564286362092D8e7936f0549571a803B203aAceD
POLL_INTERVAL_SECONDS=60
```

> ⚠️ Replace `YOUR_PASSWORD` with your actual Postgres password.

Make sure `app/config.py` calls `load_dotenv()` so these values are picked up:

```python
from dotenv import load_dotenv
load_dotenv()
```

### 5. Run the ingestor

In one terminal:

```bash
python -m app.ingestion
```

You should see logs like:

```text
Starting ingestion loop for: ['0xC36442b4...', '0x3f5CE5F...', '0x56428636...']
[ingestor] Stored tx 0x... for 0xC36442b4... with risk LOW
...
```

### 6. Run the API and dashboard

In another terminal (same env):

```bash
uvicorn app.main:app --reload
```

Then open:

* [http://127.0.0.1:8000/](http://127.0.0.1:8000/) → HTML dashboard
* [http://127.0.0.1:8000/transactions](http://127.0.0.1:8000/transactions) → JSON
* [http://127.0.0.1:8000/alerts](http://127.0.0.1:8000/alerts) → JSON alerts

---
