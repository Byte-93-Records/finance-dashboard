#!/bin/bash
set -e

echo "🚀 Finance Dashboard - PDF to Grafana Pipeline"
echo "=============================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Start Docker containers
echo "📦 Step 1: Starting Docker containers..."
docker compose up -d postgres grafana
echo -e "${GREEN}✓ PostgreSQL and Grafana started${NC}"
echo ""

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
for i in {1..30}; do
    if docker compose exec -T postgres pg_isready -U finance > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PostgreSQL is ready${NC}"
        break
    fi
    echo -n "."
    sleep 1
done
echo ""

# Step 2: Process PDFs to CSV
PDF_COUNT=$(find data/pdfs -type f -name "*.pdf" 2>/dev/null | wc -l | tr -d ' ')

if [ "$PDF_COUNT" -eq 0 ]; then
    echo -e "${YELLOW}⚠ No PDFs found in data/pdfs/${NC}"
    echo "Place PDF files in data/pdfs/ and run again"
else
    echo "📄 Step 2: Processing ${PDF_COUNT} PDF(s) to CSV..."
    docker compose run --rm pdf-processor python -m pdf_processor.cli process
    echo -e "${GREEN}✓ PDFs processed to CSV${NC}"
fi
echo ""

# Step 3: Ingest CSVs to PostgreSQL
CSV_COUNT=$(find data/csv -type f -name "*.csv" 2>/dev/null | wc -l | tr -d ' ')

if [ "$CSV_COUNT" -eq 0 ]; then
    echo -e "${YELLOW}⚠ No CSVs found in data/csv/${NC}"
    echo "Either PDFs failed to process or you need to add CSV files manually"
else
    echo "💾 Step 3: Ingesting ${CSV_COUNT} CSV(s) to PostgreSQL..."
    
    # Process each CSV file
    for csv_file in data/csv/*.csv; do
        if [ -f "$csv_file" ]; then
            echo "  Processing: $(basename "$csv_file")"
            docker compose run --rm pdf-processor python ingest.py "/data/csv/$(basename "$csv_file")" 1
        fi
    done
    
    echo -e "${GREEN}✓ CSVs ingested to database${NC}"
fi
echo ""

# Step 4: Verify data
echo "🔍 Step 4: Verifying data in PostgreSQL..."
TRANSACTION_COUNT=$(docker compose exec -T postgres psql -U finance -d finance_db -t -c "SELECT COUNT(*) FROM transactions;" 2>/dev/null | tr -d ' ')

if [ -n "$TRANSACTION_COUNT" ] && [ "$TRANSACTION_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓ Database contains ${TRANSACTION_COUNT} transactions${NC}"
else
    echo -e "${RED}✗ No transactions found in database${NC}"
fi
echo ""

# Step 5: Display access information
echo "=============================================="
echo -e "${GREEN}✅ Pipeline Complete!${NC}"
echo ""
echo "📊 Access Grafana:"
echo "   URL: http://localhost:3000"
echo "   Username: admin"
echo "   Password: admin"
echo ""
echo "🗄️  Access PostgreSQL:"
echo "   docker compose exec postgres psql -U finance -d finance_db"
echo ""
echo "📈 View Recent Transactions:"
docker compose exec -T postgres psql -U finance -d finance_db -c "SELECT transaction_date, description, amount FROM transactions ORDER BY transaction_date DESC LIMIT 5;"
echo ""
echo "=============================================="
