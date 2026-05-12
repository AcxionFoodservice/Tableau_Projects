# Tableau Cloud Connection Guide

This document covers how the scripts in this repo connect to Tableau Cloud and query usage data.

---

## Credentials

Authentication uses a **Personal Access Token (PAT)** — not username/password. The account (`dcox@kisales.com`) uses SSO, which blocks password-based REST API access.

### Creating a PAT

1. Log into Tableau Cloud: `https://us-east-1.online.tableau.com/#/site/einstein/home`
2. Click your **profile icon** (top-right) → **My Account Settings**
3. Scroll to **Personal Access Tokens** → click **Create a new token**
4. Give it a name (e.g., `claude-api`) and copy the secret — it is only shown once

### Local development

Create a `.env` file in the repo root (git-ignored):

```
TABLEAU_PAT_NAME=your-pat-name
TABLEAU_PAT_SECRET=your-pat-secret
```

Then install `python-dotenv` and call `load_dotenv()` before running any script.

### GitHub Actions

Store the token as repository secrets:

| Secret name          | Value                        |
|----------------------|------------------------------|
| `TABLEAU_PAT_NAME`   | The name you gave the PAT    |
| `TABLEAU_PAT_SECRET` | The secret string            |

Navigate to **Settings → Secrets and variables → Actions → New repository secret**.

---

## Site details

| Property         | Value                                  |
|------------------|----------------------------------------|
| Server URL       | `https://us-east-1.online.tableau.com` |
| Site content URL | `einstein`                             |
| Site ID          | `35367310-317e-40a8-8bd8-1b9f19988cd9` |
| REST API version | `3.19`                                 |

---

## How authentication works

`scripts/tableau_connect.py` posts an XML sign-in request using the PAT and returns a session token. Every subsequent REST API call passes that token in the `x-tableau-auth` header.

```python
from scripts.tableau_connect import get_token, get_paged, get_one

token = get_token()

# Paginated list endpoint (handles 100-item pages automatically)
workbooks = get_paged(token, "workbooks", "workbook")

# Single resource endpoint
root = get_one(token, f"workbooks/{workbook_id}/permissions")
```

---

## 90-day usage data — Admin Insights TS Events

The standard Tableau REST API does not provide date-filtered unique-viewer counts per workbook. The accurate source is the **Admin Insights "TS Events"** published datasource, which logs every view access event with a timestamp and actor username.

### How it works

1. The script downloads TS Events as a `.tdsx` (zip) file via the datasource content endpoint
2. Unzips it to extract the `.hyper` file inside
3. Queries the Hyper file using `tableauhyperapi` directly in Python — no Tableau Server connection needed at query time

**TS Events datasource ID:** `a2cfcec3-cfb9-426c-ae88-f27cb8675216`

### Key columns in TS Events

| Column               | Description                                      |
|----------------------|--------------------------------------------------|
| `event_name`         | Type of event (see below)                        |
| `event_date`         | UTC timestamp of the event                       |
| `actor_user_name`    | Email/username of the person who triggered it    |
| `workbook_name`      | Name of the workbook involved                    |
| `item_project_name`  | Project the workbook belongs to                  |
| `item_type`          | `View`, `Workbook`, `Data Source`, etc.          |
| `item_luid`          | Stable unique ID of the item                     |

### Useful event names

| Event name                  | Meaning                              |
|-----------------------------|--------------------------------------|
| `Access View`               | User loaded a view (most common)     |
| `Access Authoring View`     | User opened a view in edit/authoring mode |
| `Login`                     | User logged into the site            |
| `Publish Workbook`          | Workbook was published/updated       |
| `Download Workbook`         | User downloaded the workbook         |

> **Note:** The extract covers a rolling ~90-day window. Admin Insights refreshes daily.

### Hyper SQL caveats

- `STRING_AGG` is **not supported** — aggregate user lists in Python after fetching `DISTINCT` rows
- Table reference syntax: `"public"."Extract"` (schema + table, both double-quoted)

---

## Pagination

All Tableau REST API list endpoints cap at **100 items per page**. The `get_paged()` helper in `tableau_connect.py` handles this automatically by reading `<pagination totalAvailable="N">` from each response and looping until all items are fetched.

---

## Permission ID resolution

The workbook permissions endpoint returns raw UUIDs for users and groups, not display names. The report script resolves these by fetching the full user and group lists first and building lookup dicts before calling the permissions endpoints.

---

## Known limitations

| Limitation | Detail |
|---|---|
| SSO blocks password auth | Must use PAT — username/password returns 401 |
| No date-filtered unique viewers in REST API | Use Admin Insights TS Events extract instead |
| `recentlyViewed=true` is not 90 days | Reflects Tableau session history (~30 days), not a fixed window |
| Metadata API has no usage fields | The GraphQL Metadata API covers schema/lineage only, not view events |
