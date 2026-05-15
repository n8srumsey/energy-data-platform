# Energy Usage and Reliability Data Platform

This project builds a small end-to-end data platform that processes utility-style datasets and exposes simple operational insights. It follows a layered approach with S3 storage, Databricks ETL, Snowflake analytics tables, and a Streamlit interface for basic load and reliability metrics. The goal is to show a working example of data engineering, application integration, and lightweight front-end development in a cloud environment.

## Overview

The platform uses raw time series data for load, weather, and outages stored in S3. Databricks reads the raw files and runs a Bronze, Silver, and Gold pipeline to clean, standardize, and aggregate the data. Databricks exports the curated Gold tables back to S3. Snowflake loads the export files through a stage and exposes the final tables for queries. Streamlit connects to Snowflake and shows usage trends, daily peaks, and simple reliability indicators.

This repository shows practical experience with data processing, structured transformations, cloud storage, warehouse integration, and front-end development. It also shows how separate components fit together to deliver a small data product.

## Architecture

**Storage**  
All raw datasets and exported curated tables are stored in S3. The repository includes example folder layouts for raw and prepared data.

**Compute and ETL**  
Databricks notebooks run the Bronze, Silver, and Gold steps. Bronze loads raw files into Delta tables. Silver standardizes types, fixes common data issues, and aligns timestamps and region formats. Gold builds tables for daily usage, hourly profiles, and outage metrics.

**Data Warehouse**  
Snowflake uses an external stage to read the Gold exports from S3. The data loads into Snowflake tables that serve the Streamlit app. The warehouse supports fast filters, aggregations, and time window queries.

**Frontend**  
Streamlit displays charts and KPIs based on Snowflake queries. The app focuses on clear metrics such as daily demand, hourly load shapes, load factor, and customer outages during selected time windows.

## Key Features

- S3-backed raw and curated data storage
- Databricks Bronze, Silver, and Gold pipeline with Delta Lake
- Export of curated tables to S3 for downstream consumption
- Snowflake warehouse with staged load and optimized tables
- Streamlit interface for interactive queries and simple reporting
- Integration across multiple environments and services
- Clear separation of ingestion, transformation, and presentation

## Skills Demonstrated

- Data pipeline design and implementation with Python and Databricks
- Working with cloud storage on AWS S3
- Query optimization and table design with Snowflake
- Building a data product with Streamlit
- Reading business requirements and shaping data structures for analysis
- Isolating issues and debugging across multiple components
- Writing documentation to support maintainability and onboarding


The structure will be defined as the project is completed.

