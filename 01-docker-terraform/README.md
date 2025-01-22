# Data Engineering Zoomcamp - 01. Docker - Terraform

## Introduction
This repository contains the methods and codes to solve the questions of the `First Partial`of the **course `Data Engineering Zoomcamp`cohort-2025**
The repository has the following structure:
```
.
├── data
│   ├── green_tripdata_2019-10.csv
│   └── taxi_zone_lookup.csv
├── docker_commands
├── docker-compose.yaml
├── README.md
├── requirements.txt
├── sql
├── taxi_pg_data
└── upload_data.ipynb

```
* `data`: data folder (.csv files).
    * `green_tripdata_2019-10.csv`: Green taxi data file.
    * `taxi_zone_lookup.csv`: Zones data file.
* `docker_commands`: Docker code used in the analysis and study process.
* `docker-compose.yaml`: File to define and run multi-container Docker applications in this case Postgresql and pgadmin.
* `requirements.txt`: Dependencies of a project's packages.
* `sql`: File with SQL queries used in practice.
* `taxi_pg_data`: folder for data persistence for docker postgreSQL.
* `upload_data.ipynb`: Notebook where the code for reading, transforming and loading data into databases was developed.

## Quiz Answers:

### Question 1. Understanding docker first run 

Run docker with the `python:3.12.8` image in an interactive mode, use the entrypoint `bash`.

What's the version of `pip` in the image?

Steps takend:
```bash
Input
docker run -it --entrypoint bash python:3.12.8
root@3bb0869eca3f:/# pip --version
```
```
Output
pip 24.3.1 from /usr/local/lib/python3.12/site-packages/pip (python 3.12)
```
* ## Answer: 24.3.1

### Question 2. Understanding Docker networking and docker-compose

Given the following `docker-compose.yaml`, what is the `hostname` and `port` that **pgadmin** should use to connect to the postgres database?

```yaml
services:
  db:
    container_name: postgres
    image: postgres:17-alpine
    environment:
      POSTGRES_USER: 'postgres'
      POSTGRES_PASSWORD: 'postgres'
      POSTGRES_DB: 'ny_taxi'
    ports:
      - '5433:5432'
    volumes:
      - vol-pgdata:/var/lib/postgresql/data

  pgadmin:
    container_name: pgadmin
    image: dpage/pgadmin4:latest
    environment:
      PGADMIN_DEFAULT_EMAIL: "pgadmin@pgadmin.com"
      PGADMIN_DEFAULT_PASSWORD: "pgadmin"
    ports:
      - "8080:80"
    volumes:
      - vol-pgadmin_data:/var/lib/pgadmin  

volumes:
  vol-pgdata:
    name: vol-pgdata
  vol-pgadmin_data:
    name: vol-pgadmin_data
```
pgAdmin should use postgres (or localhost if they're on the same machine) as the hostname and 5432 (the internal port of the postgres container) as the port to connect to the database.

The ports section in the docker-compose.yml maps the container's internal port (5432 in this case) to a host port (5433 in this case). This allows you to access the postgres database from the host machine using the mapped port (5433). However, for communication between containers within the Docker network, the internal port (5432) is used.

* ## Answer: postgres:5432

### Question 3. Trip Segmentation Count

During the period of October 1st 2019 (inclusive) and November 1st 2019 (exclusive), how many trips, **respectively**, happened:
1. Up to 1 mile
2. In between 1 (exclusive) and 3 miles (inclusive),
3. In between 3 (exclusive) and 7 miles (inclusive),
4. In between 7 (exclusive) and 10 miles (inclusive),
5. Over 10 miles 

Steps takend:

Query
```sql
SELECT
    SUM(CASE WHEN trip_distance <= 1 THEN 1 ELSE 0 END) AS "Up to 1 mile",
    SUM(CASE WHEN trip_distance > 1 AND trip_distance <= 3 THEN 1 ELSE 0 END) AS "1-3 miles",
    SUM(CASE WHEN trip_distance > 3 AND trip_distance <= 7 THEN 1 ELSE 0 END) AS "3-7 miles",
    SUM(CASE WHEN trip_distance > 7 AND trip_distance <= 10 THEN 1 ELSE 0 END) AS "7-10 miles",
    SUM(CASE WHEN trip_distance > 10 THEN 1 ELSE 0 END) AS "Over 10 miles"
FROM
    green_tripdata_2019_10
WHERE
    (lpep_pickup_datetime >= '2019-10-01' AND lpep_pickup_datetime < '2019-11-01')
	and
	(lpep_dropoff_datetime >= '2019-10-01' AND lpep_dropoff_datetime < '2019-11-01');

```
Output:
![Up to 1 mile: 104802 | 1-3 miles: 198924 | 3-7 miles: 109603 | 7-10 miles: 27678 | Over 10 miles: 35189](<resultado query.png>)

*`Note`*: The query carried out takes as a premise the services opened and closed between the dates October 1st 2019 (inclusive) and November 1st 2019 (exclusive), leaving out of the evaluation those services that opened on October 31st but were closed on November 1st.

* ## Answer: 104,802;  198,924;  109,603;  27,678;  35,189

### Question 4. Longest trip for each day

Which was the pick up day with the longest trip distance?
Use the pick up time for your calculations.

Tip: For every day, we only care about one single trip with the longest distance. 

Steps takend:

Query
```sql
SELECT
	lpep_pickup_datetime
FROM
	green_tripdata_2019_10
WHERE
	trip_distance = (SELECT max(trip_distance)
					 FROM green_tripdata_2019_10)
```
* ## Answer: 2019-10-31

### Question 5. Three biggest pickup zones

Which were the top pickup locations with over 13,000 in
`total_amount` (across all trips) for 2019-10-18?

Consider only `lpep_pickup_datetime` when filtering by date.
 
Steps takend:

Query
```sql
SELECT
	z."Zone" AS "Zona",
	SUM(gt."total_amount") AS total
FROM zones z
LEFT JOIN green_tripdata_2019_10 gt
  ON gt."PULocationID" = z."LocationID"
WHERE
	gt."lpep_pickup_datetime" >= '2019-10-18 00:00:00' 
	AND 
	gt."lpep_pickup_datetime" < '2019-10-19 00:00:00'
GROUP BY z."Zone"
HAVING SUM(gt."total_amount") > 13000
ORDER BY SUM(gt."total_amount") DESC;
```
* ## Answer: East Harlem North, East Harlem South, Morningside Heights

### Question 6. Largest tip

For the passengers picked up in Ocrober 2019 in the zone
name "East Harlem North" which was the drop off zone that had
the largest tip?

Note: it's `tip` , not `trip`

We need the name of the zone, not the ID.


```sql
SELECT
	z."Zone" AS "Zona",
	MAX(gt."tip_amount")
FROM zones z
LEFT JOIN green_tripdata_2019_10 gt
  ON gt."DOLocationID" = z."LocationID"
WHERE
	(gt."lpep_pickup_datetime" >= '2019-10-01' 
	 AND 
	 gt."lpep_pickup_datetime" < '2019-11-01')
	 AND
	 gt."PULocationID" = 74
GROUP BY z."Zone"
ORDER BY MAX(gt."tip_amount") DESC
lIMIT 1;
```
* ## Answer: JFK Airport

### Question 7. Terraform Workflow

Which of the following sequences, **respectively**, describes the workflow for: 
1. Downloading the provider plugins and setting up backend,
2. Generating proposed changes and auto-executing the plan
3. Remove all resources managed by terraform`

* ## Answer: terraform init, terraform apply -auto-aprove, terraform destroy

