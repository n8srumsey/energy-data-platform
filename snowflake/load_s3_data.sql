
USE WAREHOUSE WH_I
USER ROLE SYSADMIN

-- =====================================================================
-- 1. Select database and schema
-- =====================================================================
USE DATABASE energy_data;
USE SCHEMA gold;

-- =====================================================================
-- 2. Stage + file format
--    Assumes you already have a working external stage, but this keeps
--    the definition in one place. Replace <STORAGE_INTEGRATION_NAME>.
-- =====================================================================

CREATE OR REPLACE STAGE s3_export_stage
  STORAGE_INTEGRATION = s3_export_int
  URL = 's3://energy-data-platform-project/export/'
  FILE_FORMAT = (TYPE = PARQUET);
  
CREATE OR REPLACE FILE FORMAT parquet_ff
  TYPE = PARQUET;

LIST @s3_export_stage;

-- =====================================================================
-- 3. Helper: pattern for creating & loading a table
--    For each folder under s3://.../export/<table_name>/:
--      1) CREATE OR REPLACE TABLE ... USING TEMPLATE (INFER_SCHEMA(...))
--      2) TRUNCATE + COPY INTO for full reload
-- =====================================================================

-- ---------------------------------------------------------------------
-- daily_region_usage
-- ---------------------------------------------------------------------
CREATE OR REPLACE TABLE energy_data.gold.daily_region_usage
USING TEMPLATE (
  SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*))
  FROM TABLE(
    INFER_SCHEMA(
      LOCATION => '@s3_export_stage/daily_region_usage/',
      FILE_FORMAT => 'parquet_ff'
    )
  )
);

TRUNCATE TABLE IF EXISTS energy_data.gold.daily_region_usage;

COPY INTO energy_data.gold.daily_region_usage
FROM @s3_export_stage/daily_region_usage/
FILE_FORMAT = (FORMAT_NAME = 'parquet_ff')
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
PATTERN = '.*\\.parquet'
ON_ERROR = 'ABORT_STATEMENT'
FORCE = TRUE;

-- ---------------------------------------------------------------------
-- hourly_region_usage
-- ---------------------------------------------------------------------
CREATE OR REPLACE TABLE energy_data.gold.hourly_region_usage
USING TEMPLATE (
  SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*))
  FROM TABLE(
    INFER_SCHEMA(
      LOCATION => '@s3_export_stage/hourly_region_usage/',
      FILE_FORMAT => 'parquet_ff'
    )
  )
);

TRUNCATE TABLE IF EXISTS energy_data.gold.hourly_region_usage;

COPY INTO energy_data.gold.hourly_region_usage
FROM @s3_export_stage/hourly_region_usage/
FILE_FORMAT = (FORMAT_NAME = 'parquet_ff')
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
PATTERN = '.*\\.parquet'
ON_ERROR = 'ABORT_STATEMENT'
FORCE = TRUE;

-- ---------------------------------------------------------------------
-- hourly_load_profile_by_segment
-- ---------------------------------------------------------------------
CREATE OR REPLACE TABLE energy_data.gold.hourly_load_profile_by_segment
USING TEMPLATE (
  SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*))
  FROM TABLE(
    INFER_SCHEMA(
      LOCATION => '@s3_export_stage/hourly_load_profile_by_segment/',
      FILE_FORMAT => 'parquet_ff'
    )
  )
);

TRUNCATE TABLE IF EXISTS energy_data.gold.hourly_load_profile_by_segment;

COPY INTO energy_data.gold.hourly_load_profile_by_segment
FROM @s3_export_stage/hourly_load_profile_by_segment/
FILE_FORMAT = (FORMAT_NAME = 'parquet_ff')
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
PATTERN = '.*\\.parquet'
ON_ERROR = 'ABORT_STATEMENT'
FORCE = TRUE;

-- ---------------------------------------------------------------------
-- hourly_load_profile_by_season
-- ---------------------------------------------------------------------
CREATE OR REPLACE TABLE energy_data.gold.hourly_load_profile_by_season
USING TEMPLATE (
  SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*))
  FROM TABLE(
    INFER_SCHEMA(
      LOCATION => '@s3_export_stage/hourly_load_profile_by_season/',
      FILE_FORMAT => 'parquet_ff'
    )
  )
);

TRUNCATE TABLE IF EXISTS energy_data.gold.hourly_load_profile_by_season;

COPY INTO energy_data.gold.hourly_load_profile_by_season
FROM @s3_export_stage/hourly_load_profile_by_season/
FILE_FORMAT = (FORMAT_NAME = 'parquet_ff')
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
PATTERN = '.*\\.parquet'
ON_ERROR = 'ABORT_STATEMENT'
FORCE = TRUE;

-- ---------------------------------------------------------------------
-- temp_bin_load_stats
-- ---------------------------------------------------------------------
CREATE OR REPLACE TABLE energy_data.gold.temp_bin_load_stats
USING TEMPLATE (
  SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*))
  FROM TABLE(
    INFER_SCHEMA(
      LOCATION => '@s3_export_stage/temp_bin_load_stats/',
      FILE_FORMAT => 'parquet_ff'
    )
  )
);

TRUNCATE TABLE IF EXISTS energy_data.gold.temp_bin_load_stats;

COPY INTO energy_data.gold.temp_bin_load_stats
FROM @s3_export_stage/temp_bin_load_stats/
FILE_FORMAT = (FORMAT_NAME = 'parquet_ff')
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
PATTERN = '.*\\.parquet'
ON_ERROR = 'ABORT_STATEMENT'
FORCE = TRUE;

-- ---------------------------------------------------------------------
-- solar_impact_on_load
-- ---------------------------------------------------------------------
CREATE OR REPLACE TABLE energy_data.gold.solar_impact_on_load
USING TEMPLATE (
  SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*))
  FROM TABLE(
    INFER_SCHEMA(
      LOCATION => '@s3_export_stage/solar_impact_on_load/',
      FILE_FORMAT => 'parquet_ff'
    )
  )
);

TRUNCATE TABLE IF EXISTS energy_data.gold.solar_impact_on_load;

COPY INTO energy_data.gold.solar_impact_on_load
FROM @s3_export_stage/solar_impact_on_load/
FILE_FORMAT = (FORMAT_NAME = 'parquet_ff')
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
PATTERN = '.*\\.parquet'
ON_ERROR = 'ABORT_STATEMENT'
FORCE = TRUE;

-- ---------------------------------------------------------------------
-- extreme_event_days
-- ---------------------------------------------------------------------
CREATE OR REPLACE TABLE energy_data.gold.extreme_event_days
USING TEMPLATE (
  SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*))
  FROM TABLE(
    INFER_SCHEMA(
      LOCATION => '@s3_export_stage/extreme_event_days/',
      FILE_FORMAT => 'parquet_ff'
    )
  )
);

TRUNCATE TABLE IF EXISTS energy_data.gold.extreme_event_days;

COPY INTO energy_data.gold.extreme_event_days
FROM @s3_export_stage/extreme_event_days/
FILE_FORMAT = (FORMAT_NAME = 'parquet_ff')
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
PATTERN = '.*\\.parquet'
ON_ERROR = 'ABORT_STATEMENT'
FORCE = TRUE;

-- ---------------------------------------------------------------------
-- data_coverage_summary
-- ---------------------------------------------------------------------
CREATE OR REPLACE TABLE energy_data.gold.data_coverage_summary
USING TEMPLATE (
  SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*))
  FROM TABLE(
    INFER_SCHEMA(
      LOCATION => '@s3_export_stage/data_coverage_summary/',
      FILE_FORMAT => 'parquet_ff'
    )
  )
);

TRUNCATE TABLE IF EXISTS energy_data.gold.data_coverage_summary;

COPY INTO energy_data.gold.data_coverage_summary
FROM @s3_export_stage/data_coverage_summary/
FILE_FORMAT = (FORMAT_NAME = 'parquet_ff')
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
PATTERN = '.*\\.parquet'
ON_ERROR = 'ABORT_STATEMENT'
FORCE = TRUE;

-- ---------------------------------------------------------------------
-- dim_date
-- ---------------------------------------------------------------------
CREATE OR REPLACE TABLE energy_data.gold.dim_date
USING TEMPLATE (
  SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*))
  FROM TABLE(
    INFER_SCHEMA(
      LOCATION => '@s3_export_stage/dim_date/',
      FILE_FORMAT => 'parquet_ff'
    )
  )
);

TRUNCATE TABLE IF EXISTS energy_data.gold.dim_date;

COPY INTO energy_data.gold.dim_date
FROM @s3_export_stage/dim_date/
FILE_FORMAT = (FORMAT_NAME = 'parquet_ff')
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
PATTERN = '.*\\.parquet'
ON_ERROR = 'ABORT_STATEMENT'
FORCE = TRUE;

-- ---------------------------------------------------------------------
-- dim_month_season
-- ---------------------------------------------------------------------
CREATE OR REPLACE TABLE energy_data.gold.dim_month_season
USING TEMPLATE (
  SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*))
  FROM TABLE(
    INFER_SCHEMA(
      LOCATION => '@s3_export_stage/dim_month_season/',
      FILE_FORMAT => 'parquet_ff'
    )
  )
);

TRUNCATE TABLE IF EXISTS energy_data.gold.dim_month_season;

COPY INTO energy_data.gold.dim_month_season
FROM @s3_export_stage/dim_month_season/
FILE_FORMAT = (FORMAT_NAME = 'parquet_ff')
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
PATTERN = '.*\\.parquet'
ON_ERROR = 'ABORT_STATEMENT'
FORCE = TRUE;

-- ---------------------------------------------------------------------
-- dim_region_substation
-- ---------------------------------------------------------------------
CREATE OR REPLACE TABLE energy_data.gold.dim_region_substation
USING TEMPLATE (
  SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*))
  FROM TABLE(
    INFER_SCHEMA(
      LOCATION => '@s3_export_stage/dim_region_substation/',
      FILE_FORMAT => 'parquet_ff'
    )
  )
);

TRUNCATE TABLE IF EXISTS energy_data.gold.dim_region_substation;

COPY INTO energy_data.gold.dim_region_substation
FROM @s3_export_stage/dim_region_substation/
FILE_FORMAT = (FORMAT_NAME = 'parquet_ff')
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
PATTERN = '.*\\.parquet'
ON_ERROR = 'ABORT_STATEMENT'
FORCE = TRUE;

-- ---------------------------------------------------------------------
-- dim_station
-- ---------------------------------------------------------------------
CREATE OR REPLACE TABLE energy_data.gold.dim_station
USING TEMPLATE (
  SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*))
  FROM TABLE(
    INFER_SCHEMA(
      LOCATION => '@s3_export_stage/dim_station/',
      FILE_FORMAT => 'parquet_ff'
    )
  )
);

TRUNCATE TABLE IF EXISTS energy_data.gold.dim_station;

COPY INTO energy_data.gold.dim_station
FROM @s3_export_stage/dim_station/
FILE_FORMAT = (FORMAT_NAME = 'parquet_ff')
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
PATTERN = '.*\\.parquet'
ON_ERROR = 'ABORT_STATEMENT'
FORCE = TRUE;

-- ---------------------------------------------------------------------
-- dim_solar_site
-- ---------------------------------------------------------------------
CREATE OR REPLACE TABLE energy_data.gold.dim_solar_site
USING TEMPLATE (
  SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*))
  FROM TABLE(
    INFER_SCHEMA(
      LOCATION => '@s3_export_stage/dim_solar_site/',
      FILE_FORMAT => 'parquet_ff')
  )
);

TRUNCATE TABLE IF EXISTS energy_data.gold.dim_solar_site;

COPY INTO energy_data.gold.dim_solar_site
FROM @s3_export_stage/dim_solar_site/
FILE_FORMAT = (FORMAT_NAME = 'parquet_ff')
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
PATTERN = '.*\\.parquet'
ON_ERROR = 'ABORT_STATEMENT'
FORCE = TRUE;

-- =====================================================================
-- End of core load script
-- =====================================================================
