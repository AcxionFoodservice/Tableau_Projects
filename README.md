# Tableau Replacements

Python tooling for Tableau Cloud administration and reporting, complementing the [Salesforce-Data-Transformation](https://github.com/AcxionFoodservice/Salesforce-Data-Transformation) pipeline.

---

## Usage Report

Generates an Excel workbook summarising Tableau Cloud workbook usage across all projects.

### What it produces

An `.xlsx` file with three sheets:

| Sheet | Contents |
|---|---|
| **Summary** | KPI cards, top-15 workbooks by 90-day users, per-project activity table |
| **All Workbooks** | One row per workbook — project, all-time views, 90-day unique users, permission groups, permission users, 90-day user list |
| **By Project** | One row per top-level project — workbook count, active/inactive split, % active, top workbook |

**90-day data source:** Admin Insights TS Events extract (exact counts, not estimates). The window is the rolling 90 days available in the extract at time of run.

---

## Running on demand via GitHub Actions

1. Go to the **Actions** tab in this repository
2. Select **Generate Tableau Usage Report** from the left sidebar
3. Click **Run workflow**
4. Optionally enter a custom output filename (default: `tableau_usage_report_YYYY-MM-DD`)
5. Click **Run workflow** — the job takes ~5 minutes
6. When complete, open the finished run and download the `.xlsx` from the **Artifacts** section

> **Required secrets** (set once under Settings → Secrets and variables → Actions):
> - `TABLEAU_PAT_NAME` — the name of the Personal Access Token
> - `TABLEAU_PAT_SECRET` — the PAT secret string

---

## Running locally

```bash
# 1. Clone and install
git clone https://github.com/AcxionFoodservice/Tableau_Replacements.git
cd Tableau_Replacements
pip install -r requirements.txt

# 2. Set credentials
cp .env.example .env
# Edit .env with your TABLEAU_PAT_NAME and TABLEAU_PAT_SECRET

# 3. Run
python scripts/generate_usage_report.py

# Optional: specify output filename
python scripts/generate_usage_report.py --output my_report.xlsx
```

---

## Repository layout

```
scripts/
  tableau_connect.py          # Auth helper — get_token(), get_paged(), get_one()
  generate_usage_report.py    # Main script: fetches data, builds Excel

.github/workflows/
  generate_usage_report.yml   # workflow_dispatch trigger for on-demand runs

docs/
  Tableau_Connection_Guide.md # Full connection, auth, and API reference

requirements.txt
.env.example
```

---

## Tableau Cloud site details

| Property | Value |
|---|---|
| Server | `https://us-east-1.online.tableau.com` |
| Site | `einstein` |
| API version | `3.19` |
| Auth method | Personal Access Token (PAT) — SSO blocks password auth |

See [docs/Tableau_Connection_Guide.md](docs/Tableau_Connection_Guide.md) for full details on authentication, the TS Events datasource, pagination, and known limitations.
