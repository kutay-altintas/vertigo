# Vertigo Games – Data Engineer Case

This repository contains my solution to the Vertigo Games Data Engineer case study, covering
API development, cloud deployment, data modeling, and business-oriented visualization.

## Repository Structure

├── app/                 # Flask application  
├── Dockerfile 
├── docker-compose.yml
├── data/  
│   ├── daily_metrics.sql  
│   ├── daily_metrics.csv  
│   └── DailyMetrics.twb 
└── README.md

# Database & API

## Deployment 

The app is deployed as a containerized service on **Google Cloud Run**.

**Base URL:** https://vertigo-589707809820.europe-west6.run.app

## Database

The application uses a **PostgreSQL** database hosted on **Google Cloud SQL**
in the `europe-west6` region.

The database is accessed securely via environment variables (`DATABASE_URL`) and is not exposed directly to clients.

## Dockerization & Local Run Instructions

The API is packaged as a Docker container so it can be run locally or deployed to Cloud Run with the same image.

The container uses gunicorn to serve the Flask app and listens on port 8080.

### 1. Prerequisites
- Docker installed (Docker Desktop or equivalent)
- (Optional) Docker Compose installed
- Access to a PostgreSQL database on Cloud SQL for cloud access.

    (If you don't have a valid `DATABASE_URL`, the application runs on **SQLite** on local)

### 2. Environment configuration

Create a `.env` file in the project root:

```bash
# Example: PostgreSQL (SQLAlchemy style)
DATABASE_URL=postgresql+psycopg2://vertigo_app:YOUR_PASSWORD@HOST:5432/clans
```
This value is read by the application inside the container.

For local development convenience, the application falls back to **SQLite** if `DATABASE_URL` is not provided. Cloud deployments use **Cloud SQL** exclusively.

### 3. Run with Docker Compose
From the project root (where the `Dockerfile` lives):

```bash
docker compose up --build
```
This will:
- Build the api image from the local Dockerfile
- Inject environment variables from .env
- Expose the API on http://localhost:8080


## API Endpoints

The app supports all expected API endpoints:
- Listing all clans
- Creating a new clan
- Searching a clan by its name
- Deleting an existing clan

### 1. `GET /api/clans`

#### Purpose
Retrieve a list of all clans stored in the system.

#### Method
`GET`

**Path**: 
```
/api/clans
```
 
#### Request
No request body

#### Response - 200 OK

```json
[
  {
    "id": "d041087d-1f13-423f-af7b-be361a7863b5",
    "name": "ShadowReavers",
    "region": "JP",
    "created_at": "2024-07-19T01:44:33Z"
  },
  {
    "id": "93f477f4-9f50-4082-a9eb-52423a6a8027",
    "name": "NightWolves",
    "region": "US",
    "created_at": "2024-07-20T14:12:01Z"
  }
]
```

#### Notes
- `created_at`is stored and returned in UTC.
- Results are unordered

### 2. `POST /api/clans`

#### Purpose
Create a new clan.

#### Method
`POST`

#### Path
```bash
/api/clans
```
 
#### Request – JSON body
```json
{
  "name": "IronLegion",
  "region": "TR"
}
```

#### Validation Rules

- `name` : required, non-empty string
- `region` : required, 2-character country/region code


#### Response – 201 Created
```json
{
  "id": "1370299a-43e1-4d28-ab78-89b86fddb903",
  "name": "Shadowlands",
  "region": "TR",
  "created_at": "2024-07-21T09:30:45Z"
}
```
#### Possible errors
- `400 Bad Request` – missing or invalid fields


### 3. `GET /api/clans/search?name={query}`

#### Purpose
Search for clans whose names **contain** the given query string.

#### Path
`/api/clans/search

#### Query parameters
- `name` (required): search string with minimum 3 characters

#### Example request
```bash
/api/clans/search?name=Sha
```

#### Search behavior
- Case insensitive
- Partial match(`contains` rule)
- Requires at least 3 characters

#### Response – 200 OK
```json
[
  {
    "id": "2928383f-2765-4264-a35f-fc68d0eb1a36",
    "name": "ShadowReavers",
    "region": "JP",
    "created_at": "2024-07-19T01:44:33Z"
  }
]
```
#### Possible Errors 
- `400 Bad Request` – query string shorter than 3 characters

### 4. `DELETE /api/clans/{id}`

#### Path
```bash
/api/clans/{id}
```

#### Path parameters
- `id`: uuid clan identifier

#### Example request
```
/api/clans/91329e6f-c178-4a5d-be71-246c858f1544
```

#### Response – 204 No Content
No response body is returned upon successful deletion.

#### Possible errors
- `404 Not Found` – clan with given `id` does not exist.

## Notes & Assumptions
- Clan names are not required to be unique unless otherwise specified.
- Deletions are permanent.
- All timestamps are generated server-side and stored in UTC.
- The API is intentionally simple and unauthenticated, as per the scope of the assignment.


# DBT Model & Visualization

The given dataset is stored at **Google Big Query** and queried at there.

**Tableau Public** is used for dashboard creation. Since the free edition does not support direct connectivity to **Google Big Query**, the dataset is exported manually, which can be found at:

```
data/daily_metrics.csv
```

The **dbt model** can be found at:
```
data/daily_metrics.sql
```

## Initial Data Quality & Sanity Checks

- `total_session_count` and `total_session_duration` is verified to be nonnegative across the data.
    <details>
        <summary>SQL and Results</summary>

    ```sql
    SELECT
    COUNT(*) AS bad_rows
    FROM `mimetic-maxim-479612-j9.vertigo_analytics.raw_daily_metrics`
    WHERE total_session_count < 0
    OR total_session_duration < 0;
    ```
    | bad_rows |
    | -----------: |
    | 0 |

    </details>

- It was confirmed that there are no null values for `user_id`, `event_date` and `platform` columns. There are roughly ~17k null `country` rows, which could be attributed to inconsistencies in location services and usage of VPN.
    <details>
        <summary>SQL and Results</summary>

    ```sql
    SELECT
    COUNTIF(user_id IS NULL) user_id_null,
    COUNTIF(event_date IS NULL) AS event_date_null,
    COUNTIF(platform IS NULL) AS platform_null,
    COUNTIF(country IS NULL) AS country_null
    FROM `mimetic-maxim-479612-j9.vertigo_analytics.raw_daily_metrics`
    ```

    | user_id_null| 	event_date_null| 	platform_null| 	country_null| 
    | ----------- | ----------- | ----------- | ----------- |
    | 0| 	0| 	0| 	16884| 

    </details>

- A logical check is carried out to confirm that `victory_count` + `defeat_count` = `match_end_count`, and all values are nonnegative. 
    <details>
        <summary>SQL and Results</summary>
    
    ```sql
    SELECT
    COUNT(*) AS inconsistent_rows
    FROM `mimetic-maxim-479612-j9.vertigo_analytics.raw_daily_metrics`
    WHERE match_end_count != victory_count + defeat_count OR victory_count < 0 OR defeat_count < 0;
    ```

    |inconsistent_rows|
    | ----------- |
    |0|

    </details>
- Duplicate rows for users for the same date is checked. And plenty of duplicate records with exactly two duplicates were found. To investigate further whether these were caused by an upstream error or something similar, the subjected rows were investigated visually. The seemingly duplicate results were the results of users using our application with ios and android platforms respectively on the same day. Hence, it was confirmed that the data is correct and no duplicates exist when platforms are taken into consideration.
    <details>
        <summary>SQL and Results</summary>
    
    ```sql
    SELECT
    user_id,
    event_date,
    COUNT(*) AS records
    FROM `mimetic-maxim-479612-j9.vertigo_analytics.raw_daily_metrics`
    GROUP BY user_id, event_date
    HAVING COUNT(*) > 1
    ORDER BY records ASC;
    ```
    |user_id|	event_date|	records|
    | ---- | ---- | ---- | 
    | BE0BAFC0238679DB|	2024-02-16|	2|
    |523BDED262834DA4|	2024-03-01|	2|
    |10824EC576E6CA5F|	2024-03-02|	2|
    |60C695003E756CA|	2024-02-23|	2|
    |2394D6A6505B1693|	2024-03-01|	2|
    |...|...|...|

    ```sql
    WITH dup_groups AS (
    SELECT
        user_id,
        event_date,
        COUNT(*) AS records,
        COUNT(DISTINCT TO_JSON_STRING(STRUCT(
        country,
        platform,
        total_session_count,
        total_session_duration,
        match_start_count,
        match_end_count,
        victory_count,
        defeat_count,
        server_connection_error,
        iap_revenue,
        ad_revenue
        ))) AS distinct_payloads
    FROM `mimetic-maxim-479612-j9.vertigo_analytics.raw_daily_metrics`
    GROUP BY user_id, event_date
    HAVING COUNT(*) = 2
    )

    SELECT
    t.*
    FROM `mimetic-maxim-479612-j9.vertigo_analytics.raw_daily_metrics` t
    JOIN dup_groups g
    ON t.user_id = g.user_id
    AND t.event_date = g.event_date
    WHERE g.distinct_payloads > 1
    ORDER BY t.user_id, t.event_date
    LIMIT 200;
    ```

    ```sql
    SELECT
    user_id,
    event_date,
    platform, 
    COUNT(*) AS records
    FROM `mimetic-maxim-479612-j9.vertigo_analytics.raw_daily_metrics`
    GROUP BY user_id, event_date, platform
    HAVING COUNT(*) > 1
    ORDER BY records ASC;
    ```
    </details>
- The data spans 1-month period from 15.02.2024 to 15.03.2024.
    <details>
        <summary>SQL and Results</summary>

    ```sql
    SELECT
    COUNT(*) AS row_count,
    MIN(event_date) AS min_date,
    MAX(event_date) AS max_date
    FROM `mimetic-maxim-479612-j9.vertigo_analytics.raw_daily_metrics`
    ```

    | row_count | 	min_date | 	max_date | 
    | --- | --- | --- 
    | 6864230 | 	2024-02-15 | 	2024-03-15 | 

    </details>

- Revenue outliers are checked if absurdly high values are present. It was confirmed that the max `iap_revenue` value is just above 2000, and values are consistent and normal across dates.
    <details>
        <summary>SQL and Results</summary>

    ```sql
    SELECT
    event_date,
    MAX(iap_revenue) AS max_iap,
    AVG(iap_revenue) AS avg_iap
    FROM `mimetic-maxim-479612-j9.vertigo_analytics.raw_daily_metrics`
    GROUP BY event_date
    ORDER BY max_iap DESC
    LIMIT 10;
    ```

    | event_date| 	max_iap| 	avg_iap| 
    | ----------- | ----------- | ----------- |
    | 2024-03-01| 	2790.2350127187774| 	0.16285013992884731| 
    | 2024-02-15| 	2180.2635519616647| 	0.1337401314767675| 
    | 2024-02-29| 	1867.5823393136952| 	0.14149786004333559| 
    | 2024-02-19| 	1670.0346302709313| 	0.11245107617496522| 
    | 2024-03-07| 	1566.1854891970941| 	0.12317659334070614| 
    | 2024-03-10| 	1450.5303349397454| 	0.13822874106758026| 
    | 2024-02-17| 	1433.3243519965513|  	0.13773000547660777| 
    | 2024-03-05| 	1338.9183932979281| 	0.12193937019727048| 
    | 2024-03-09| 	1258.9044281300869| 	0.13449908026254223| 
    | 2024-03-12 | 	1241.8597220003196| 	0.10732290004398819| 
    </details>

- For the given 1 month period, daily active users is calculated to detect if days with unusually high or low activity is present, which could indicate some sort of server failure. Daily Active Users is stable and fluctuates reasonably across dates.
    <details>
        <summary>SQL and Results</summary>

    ```sql
    SELECT
    event_date,
    COUNT(DISTINCT user_id) AS dau
    FROM `mimetic-maxim-479612-j9.vertigo_analytics.raw_daily_metrics`
    GROUP BY event_date
    ORDER BY event_date ASC;
    ```

    | event_date | 	dau | 
    | ----- | 	----- | 
    | 2024-02-16 | 	240102 | 
    | 2024-02-17 | 	269279 | 
    | 2024-02-18 | 	271815 | 
    | 2024-02-19 | 	231962 | 
    | 2024-02-20 | 	223997 | 
    | 2024-02-21 | 	221572 | 
    | 2024-02-22 | 	222141 | 
    | 2024-02-23 | 	228946 | 
    | 2024-02-24 | 	254551 | 
    | 2024-02-25 | 	252618 | 
    | 2024-02-26 | 	210037 | 
    | 2024-02-27 | 	207500 | 
    | 2024-02-28 | 	205931 | 
    | 2024-02-29 | 	206622 | 
    | 2024-03-01 | 	217995 | 
    | 2024-03-02 | 	244348 | 
    | 2024-03-03 | 	247770 | 
    | 2024-03-04 | 	204264 | 
    | 2024-03-05 | 	202495 | 
    | 2024-03-06 | 	201443 | 
    | 2024-03-07 | 	206682 | 
    | 2024-03-08 | 	224203 | 
    | 2024-03-09 | 	252822 | 
    | 2024-03-10 | 	254867 | 
    | 2024-03-11 | 	216575 | 
    | 2024-03-12 | 	225261 | 
    | 2024-03-13 | 	227321 | 
    | 2024-03-14 | 	227072 | 
    | 2024-03-15 | 	234737 | 
    </details>


The preliminary checks confirmed that there aren't any major problems and inconsistencies with the dataset. Hence, the data is not modified in any means, and the entire dataset is used.

### DBT Model

Although dbt was not executed directly, the model follows dbt conventions and is written as a standalone SQL transformation compatible with dbt.

The following query is used:
```sql
WITH base AS (
  SELECT
    event_date,
    country,
    platform,
    COUNT(DISTINCT user_id) AS dau,
    SUM(iap_revenue) AS total_iap_revenue,
    SUM(ad_revenue) AS total_ad_revenue,
    SUM(match_start_count) AS matches_started,
    SUM(match_end_count) AS matches_ended,
    SUM(victory_count) AS victories,
    SUM(defeat_count) AS defeats,
    SUM(server_connection_error) AS server_errors
  FROM `mimetic-maxim-479612-j9.vertigo_analytics.raw_daily_metrics`
  GROUP BY event_date, country, platform
)

SELECT
  event_date,
  country,
  platform,
  dau,
  total_iap_revenue,
  total_ad_revenue,
  SAFE_DIVIDE(total_iap_revenue + total_ad_revenue, dau) AS arpdau,
  matches_started,
  SAFE_DIVIDE(matches_started, dau) AS match_per_dau,
  SAFE_DIVIDE(victories, matches_ended) AS win_ratio,
  SAFE_DIVIDE(defeats, matches_ended) AS defeat_ratio,
  SAFE_DIVIDE(server_errors, dau) AS server_error_per_dau
FROM base;
```

## Dashboards & Visualization

The dashboard contains 3 sections, serving different purposes. The Tableau file can be found at:
```bash
data/DailyMetrics.twb
```

### Key Findings

- Daily Active Users exhibit clear weekly seasonality, with consistent peaks on weekends.
- iOS users generate higher in-app purchase revenue compared to Android users, while ad revenue is similar across platforms.
- Revenue contribution varies significantly by region, highlighting opportunities for targeted monetization strategies.


### Daily Active Users (DAU) Over Time

!["DAU over time"](./data/DAU.png)

The weekends are highlighted with orange color, and it is evident that **DAU** peaks on weekends. This seasonality is expected and normal, and expected to continue year-round.

### Average Revenue per Daily Active User (ARPDAU) by Regions

!["Average Revenue Per Daily Active User"](./data/Region.png)

This graph suggests us that players located at South Korea, Iceland, Australia, Gabon, Mozambique, North America and Europe generate quite a lot of revenue. This can help us for targeted ad strategies, and make case-studies of countries to translate the successful monetization into others.

### Platform Metrics

!["Revenue by platform"](./data/Platform.png)

This side-by-side comparison of **Android** and **IOS** users suggests that **IOS** users are more likely to generate revenue with in-app-purchases. Meanwhile, ad revenues for both platforms are at similar figures. 
