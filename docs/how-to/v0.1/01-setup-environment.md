# How to Set Up Your Development Environment

**Version:** v0.1  
**Type:** How-To Guide  
**Time:** 10 minutes

## Prerequisites

- Docker Desktop installed
- Git installed
- 2GB free disk space

## Steps

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/finance-dashboard.git
cd finance-dashboard
```

### 2. Create Environment File

```bash
cp .env.example .env
```

Edit `.env` and set:
```bash
DATABASE_URL=postgresql://finance:finance@postgres:5432/finance_db
GF_SECURITY_ADMIN_PASSWORD=grafana123
GF_DATABASE_PASSWORD=finance
PDF_TIMEOUT_SECONDS=300
```

### 3. Start Docker Services

```bash
docker compose up -d postgres grafana
```

Wait 10 seconds for PostgreSQL to initialize.

### 4. Run Database Migrations

```bash
docker compose run --rm pdf-processor alembic upgrade head
```

### 5. Verify Setup

Check PostgreSQL:
```bash
docker compose exec postgres psql -U finance -d finance_db -c "\dt"
```

You should see: `accounts`, `transactions`, `import_logs`, `categories`, `alembic_version`

Check Grafana:
```bash
curl -u admin:grafana123 http://localhost:3000/api/health
```

You should see: `{"commit":"...","database":"ok",...}`

## Troubleshooting

### PostgreSQL won't start
```bash
docker compose logs postgres
docker compose down -v  # WARNING: Deletes data
docker compose up -d postgres
```

### Grafana shows "database not found"
1. Check `GF_DATABASE_PASSWORD` matches in `.env` and `docker-compose.yml`
2. Restart Grafana: `docker compose restart grafana`

### Migrations fail
```bash
# Reset migrations (WARNING: Deletes data)
docker compose exec postgres psql -U finance -d finance_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
docker compose run --rm pdf-processor alembic upgrade head
```

## Next Steps

- [How to Process PDF Statements](02-process-pdf-statements.md)
- [How to Ingest CSV Data](03-ingest-csv-data.md)

---

**Related:**
- [Database Schema Reference](../../reference/v0.1/database-schema.md)
- [Environment Variables Reference](../../reference/v0.1/environment-variables.md)
