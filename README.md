# Customer Data Platform (CDP) - System Design Documentation

## Project Description

A comprehensive Customer Data Platform that enables businesses to unify, enrich, and activate their customer data for better insights and engagement.

### Key Features
- **Unified Customer Profiles** - Quickly and easily connect all of your customer data into clean, enriched customer profiles
- **Data Enrichment** - Fill the gaps in each profile with intelligent data matching and enhancement
- **Predictive Analytics** - Predict customer behavior using advanced machine learning models
- **AI-Powered Analysis** - Analysis made easy with AI-driven insights and automated recommendations
- **Secure Data Capture** - Enterprise-grade security ensuring safe and compliant data handling

## System Diagram

```
                 ┌──────────────┐    ┌─────────────┐
                 │   Webhooks   │    │  Schedulers │
                 │              │    │             │
                 │ • Real-time  │    │ • BuildKite │
                 │   Events     │    │ • Cron Jobs │
                 │ • User       │    │ • ECS Tasks │
                 │   Actions    │    │             │
                 └──────┬───────┘    └──────┬──────┘
                        │                   │
                        │                   │
                        │            ┌──────▼──────┐
                        │            │ECS Fargate  │
                        │            │             │
                        │            │ • Singer Tap│
                        │            │ • Docker    │
                        │            │   Container │
                        |            └──────┬──────┘
                ┌───────▼─────┐             │
                │ API Gateway │             │
                │             │             │
                │ • Webhook   │             │
                │   Endpoints │             │
                └──────┬──────┘             │
                       │                    │
                ┌──────▼──────┐             │
                │   Lambda    │             │
                │             │             │
                │ • Validate  │             │
                │ • Process   │             │
                └──────┬──────┘             │
                       │                    │
                ┌──────▼──────┐             │
                │     SQS     │             │
                │             │             │
                │ • Buffer    │             │
                │   Events    │             │
                └──────┬──────┘             │
                       │                    │
                ┌──────▼──────┐             │
                │Batch Proc.  │             │
                │  (Lambda)   │             │
                │             │             │
                │ • Aggregate │             │
                │ • 20k Batch │             │
                └──────┬──────┘             │
                       │                    │
                       ┼────────────────────┘
                       │
             ┌─────────▼─────────┐
             │      S3 Raw       │
             │   (Integration)   │
             │                   │
             │ • NDJSON Files    │
             └─────────┬─────────┘
                       │
             ┌─────────▼─────────┐
             │     PySpark       │
             │  Transformation   │
             │                   │
             │ • Data Cleaning   │
             │ • Normalization   │
             │ • Validation      │
             │ • Data Enrichment │
             └─────────┬─────────┘
                       │
             ┌─────────▼─────────┐
             │   S3 Processed    │
             │  (Curated Zone)   │
             │                   │
             │ • Clean Data      │
             │ • Partitioned     │
             │ • Schema Aligned  │
             │ • Enriched Data   │
             └─────────┬─────────┘
                       │
             ┌─────────▼─────────┐
             │    Database       │
             │   (PostgreSQL)    │
             │                   │
             │ • Customer Tables │
             │ • Event Tables    │
             │ • Product Tables  │
             └─────────┬─────────┘
                       │
   ┌───────────────────┼───────────────────┐
   │                   │                   │
┌──▼──────────┐ ┌──────▼───────┐ ┌─────────▼─────────┐
│Segmentation │ │  Analytics   │ │    Reporting      │
│             │ │              │ │                   │
│• Behavioral │ │ • Customer   │ │ • Dashboards      │
│  Segments   │ │   Insights   │ │ • KPIs            │
│• Demographic│ │ • Cohort     │ │ • Business        │
│  Groups     │ │   Analysis   │ │   Intelligence    │
│• ML Models  │ │ • AI-Powered │ │ • Real-time       │
│             │ │   Insights   │ │   Metrics         │
└─────────┬───┘ └──────────────┘ └───────────────────┘
          │
          │
┌─────────▼─────────┐
│    Activation     │
│                   │
│ • Email Service   │
│ • Facebook Ads    │
│ • Google Ads      │
│ • Other Marketing │
│   Platforms       │
└───────────────────┘
```

## Deep Dive: System Components

### S3 Raw (Integration Layer)

The S3 Raw bucket serves as the initial landing zone for all incoming customer data from various sources.

#### Purpose
- **Data Ingestion Hub** - Central repository for raw, unprocessed data
- **Data Preservation** - Maintains original data format for audit and compliance
- **Decoupling** - Separates data collection from processing workflows

#### Data Organization
```
s3://cdp-raw-bucket/
├── acme_corp/
│   ├── salesforce/
│   │   ├── year=2025/
│   │   │   ├── month=01/
│   │   │   │   ├── day=15/
│   │   │   │   │   ├── customer_batch_001.ndjson.gzip (20k records)
│   │   │   │   │   ├── customer_batch_002.ndjson.gzip (20k records)
│   │   │   │   │   └── customer_batch_003.ndjson.gzip (15k records)
│   │   │   │   └── day=16/
│   │   │   │       ├── customer_batch_001.ndjson.gzip
│   │   │   │       └── customer_batch_002.ndjson.gzip
│   ├── shopify/
│   │   ├── year=2025/
│   │   │   ├── month=01/
│   │   │   │   ├── day=15/
│   │   │   │   │   ├── customer_batch_001.ndjson.gzip
│   │   │   │   │   └── customer_batch_002.ndjson.gzip
```

#### File Formats
- **NDJSON.GZIP** - Standardized, compressed, line-by-line processable format

#### Data Sources
- **CRM Systems** - Customer profiles, contact information, sales data
- **E-commerce Platforms** - Orders, products, transaction history
- **Marketing Tools** - Campaign data, email metrics, ad performance
- **Real-time Events** - User interactions, page views, clicks
- **Third-party APIs** - Social media data, enrichment services

#### Retention Policy
- **Raw Data** - 7 years for compliance and historical analysis
- **Partitioning** - By year/month/day for efficient querying
- **Lifecycle Management** - Automatic transition to cheaper storage classes

#### How It Works

**Data Extraction Pipeline:**
1. **Singer.io Taps** - Custom-built data extractors for each provider
   - Implements Singer specification for standardized data extraction
   - Handles API rate limiting and incremental syncs
   - **Batch Processing** - Pushes data in 20k record batches to S3
   - Creates multiple smaller files per day instead of single large file
   - Outputs data in Singer format (JSON records with schema)

2. **BuildKite Scheduling** - Orchestrates data extraction jobs
   - Cron-based scheduling for regular data pulls
   - Parallel execution for multiple customers/providers
   - Retry logic and failure notifications
   - Build pipeline triggers based on data availability

3. **Docker Containerization** - Packaging and deployment
   - Each tap packaged as lightweight Docker container
   - Consistent runtime environment across all extractors
   - Easy versioning and rollback capabilities
   - Isolated execution prevents interference between jobs

4. **ECS Fargate Deployment** - Serverless container execution
   - Auto-scaling based on scheduled workloads
   - No server management overhead
   - Cost-effective pay-per-use model
   - Built-in load balancing and health checks


#### Error Handling & Recovery Strategy

**Key Features:**
- 30-minute ECS timeouts with resume capability
- Exponential backoff for rate limits (429) and server errors (5xx)
- Batch-level recovery - failed batches retry independently
- Singer state files enable resumable operations

**Error Flow:** `Rate Limit → Backoff → Retry | Server Error → 3x Retry → Dead Letter Queue`

#### Performance & Scalability

**Design:**
- **20k Record Batches** - Optimal for memory and parallel processing
- **Auto-scaling** - ECS Fargate scales with workload demand
- **Incremental Loading** - Singer state tracks progress

**Targets:**
- 1M+ records/hour per provider
- 2-hour data availability SLA
- 70-80% compression with gzip

**Limits:**
- 1000 concurrent ECS tasks per region
- 3500+ S3 PUT requests/second per prefix

#### Data Validation & Schema Management

**Schema Validation:**
- **JSON Schema Validation** - Each batch validated against expected schema before S3 upload
- **Field Type Checking** - Validate data types (string, integer, datetime) per field
- **Required Field Validation** - Ensure mandatory fields are present and non-null

**Schema Evolution Handling:**
- **Schema Registry** - Centralized store for provider schema versions
- **Backward Compatibility** - New fields allowed, existing fields cannot be removed
- **Schema Drift Detection** - Alert when incoming data doesn't match expected schema

**Validation Process:**
```
Singer Tap Extract → Schema Validation → Pass: Upload to S3 | Fail: Dead Letter Queue
```

**Dead Letter Queue (DLQ) Usage:**
- **Failed Extractions** - Batches that fail after 3 retry attempts
- **Schema Validation Failures** - Records that don't match expected schema
- **Data Quality Issues** - Records with invalid data types or missing required fields
- **Rate Limit Exhaustion** - Batches that repeatedly hit API rate limits
- **Authentication Failures** - Records from providers with expired/invalid credentials

**DLQ Processing:**
- **Storage Location** - `s3://cdp-dlq-bucket/{customer}/{provider}/{error-type}/`
- **Error Metadata** - Each failed record includes error reason, timestamp, retry count
- **Manual Review** - Engineering team reviews DLQ daily for pattern analysis
- **Reprocessing** - Fixed records can be manually resubmitted to main pipeline
- **Alerting** - Slack notifications when DLQ volume exceeds threshold

**How Reprocessing Works:**
1. **Investigate Issue** - Engineer reviews DLQ records and error metadata
2. **Fix Root Cause** - Update schema, fix credentials, or resolve data quality issues
3. **Prepare Records** - Clean/transform failed records to match expected format
4. **Manual Resubmission** - Use BuildKite pipeline to reprocess specific DLQ batches
5. **Validation** - Reprocessed records go through same validation pipeline
6. **Monitor Results** - Track success rate of reprocessed records

**Validation Failures:**
- Invalid records sent to dead letter queue with error details
- Alerts sent to engineering team for schema mismatches
- Daily reports on validation success rates per provider

#### Webhook Handling

**Webhook Architecture:**
- **API Gateway** - Public endpoint for receiving webhook events
- **Lambda Functions** - Process incoming webhooks and validate payloads
- **SQS Queues** - Buffer webhook events for reliable processing
- **Batch Processing** - Aggregate events into 20k record batches for S3

**Webhook Flow:**
```
Provider Webhook → API Gateway → Lambda → SQS → Batch Processor → S3 Raw
```

**Step-by-Step Process:**

1. **Provider Webhook** → **API Gateway**
   - Shopify/Stripe/Salesforce sends real-time event (order created, payment completed, etc.)
   - API Gateway receives the HTTP POST request at public endpoint

2. **API Gateway** → **Lambda**
   - API Gateway forwards the webhook payload to Lambda function
   - Lambda function starts processing the webhook

3. **Lambda Processing:**
   - **Auth Check** - Validates webhook signature (HMAC/JWT) to ensure it's from real provider
   - **Validate** - Checks payload format and required fields
   - **Extract Metadata** - Determines customer, provider, event type from headers/payload

4. **Lambda** → **SQS**
   - Lambda sends validated webhook event to SQS queue
   - SQS acts as a buffer - holds events until ready for batch processing

5. **SQS** → **Batch Processor**
   - Separate Lambda function reads events from SQS
   - **Aggregate** - Collects events until reaching 20k records OR timeout (5 minutes)

6. **Batch Processor** → **S3 Raw**
   - **Store NDJSON** - Converts batch to NDJSON.gzip format
   - Uploads to S3 using same folder structure as Singer taps

**Why This Design?**
- **Immediate Response** - Webhook providers get instant 200 OK response
- **Reliable Processing** - SQS ensures no events are lost if Lambda fails
- **Batch Efficiency** - Groups individual webhook events into efficient 20k record files
- **Consistent Format** - Webhook data stored same way as batch extractions
- **Scalable** - Can handle thousands of webhook events per second



**Webhook Security:**
- **Signature Validation** - Verify webhook signatures from providers (HMAC, JWT)
- **Rate Limiting** - API Gateway throttling to prevent abuse
- **IP Whitelisting** - Restrict webhook sources to known provider IPs
- **Authentication** - Custom headers or tokens for customer identification

**Webhook Providers:**
- **Shopify** - Order events, customer updates, inventory changes
- **Stripe** - Payment events, subscription changes, dispute notifications
- **Salesforce** - Lead updates, opportunity changes, account modifications
- **Custom APIs** - User actions, application events, system notifications

**Error Handling:**
- **Validation Failures** - Invalid webhooks sent to DLQ with error details
- **Processing Errors** - Failed batch processing retried with exponential backoff
- **Dead Letter Queue** - Persistent failures stored for manual review
- **Monitoring** - CloudWatch metrics for webhook success rates and latency

**Benefits:**
- **Real-time Data** - Near-instant data availability (vs daily batch jobs)
- **Event-driven** - Capture user actions as they happen
- **Scalable** - SQS buffering handles traffic spikes
- **Consistent Format** - Same NDJSON.gzip format as batch extractions
- **Reliable** - SQS ensures no webhook events are lost

### Schedulers (Batch Data Extraction)

The Schedulers component orchestrates regular batch data extraction from various data sources using Singer.io taps and AWS infrastructure.

#### Purpose
- **Scheduled Data Extraction** - Automated data pulls from CRM, e-commerce, and marketing platforms
- **Batch Processing** - Large-scale data ingestion in scheduled intervals
- **Orchestration** - Coordinated execution across multiple customers and providers
- **Reliability** - Robust error handling and retry mechanisms

#### Architecture Overview

**Core Components:**
- **BuildKite** - CI/CD pipeline orchestration and scheduling
- **ECS Fargate** - Serverless container execution platform
- **Singer.io Taps** - Standardized data extraction tools
- **Docker Containers** - Packaged extraction environments
- **S3 Raw** - Destination for extracted data

#### How Singer.io Taps Work

**Singer Specification:**
- **Open Source Standard** - Community-driven data extraction framework
- **JSON-based Output** - Structured data format with schema definitions
- **Incremental Sync** - State-based tracking for efficient updates
- **Stream Processing** - Record-by-record data extraction

**Singer Components:**
1. **Taps** - Extract data from source systems (Salesforce, Shopify, etc.)
2. **Targets** - Load data into destination systems (S3, databases)
3. **State Files** - Track extraction progress for incremental syncs
4. **Schema Discovery** - Automatic detection of source data structures

**Singer Data Flow:**
```
Source API → Singer Tap → JSON Records → Schema Validation → S3 Target
```

**Example Singer Output:**
```json
{"type": "SCHEMA", "stream": "customers", "schema": {...}}
{"type": "RECORD", "stream": "customers", "record": {"id": 123, "name": "John"}}
{"type": "STATE", "value": {"bookmarks": {"customers": {"last_updated": "2025-01-15"}}}}
```

#### AWS Services Integration

**BuildKite (Orchestration):**
- **Pipeline Definition** - YAML-based job configuration
- **Cron Scheduling** - Time-based trigger execution
- **Agent Management** - Distributed build agent coordination
- **Retry Logic** - Failed job re-execution with exponential backoff
- **Notifications** - Slack/email alerts for job status

**ECS Fargate (Container Execution):**
- **Serverless Containers** - No EC2 instance management required
- **Auto Scaling** - Dynamic task scaling based on workload
- **Resource Allocation** - Per-task CPU and memory configuration
- **Networking** - VPC integration with security group controls
- **Service Discovery** - Internal service communication

**Docker Containerization:**
- **Singer Tap Images** - Pre-built containers for each data source
- **Environment Isolation** - Separate runtime environments per customer
- **Version Control** - Tagged images for rollback capabilities
- **Secret Management** - AWS Secrets Manager integration

#### Execution Workflow

**Step-by-Step Process:**

1. **BuildKite Trigger**
   - Cron schedule activates (e.g., daily at 2 AM UTC)
   - Pipeline reads customer/provider configuration
   - Generates ECS task definitions for each extraction job

2. **ECS Task Launch**
   - Fargate provisions container resources
   - Downloads Singer tap Docker image
   - Injects customer credentials from AWS Secrets Manager
   - Starts container with tap-specific configuration

3. **Singer Tap Execution**
   - Tap connects to source API (Salesforce, Shopify, etc.)
   - Reads previous state file from S3 for incremental sync
   - Extracts data records with schema validation
   - Batches records into 20k chunks for S3 upload

4. **Data Upload**
   - Records formatted as NDJSON.gzip
   - Uploaded to S3 with partitioned folder structure
   - State file updated with latest extraction timestamp
   - Task completion logged to CloudWatch

**Execution Flow Diagram:**
```
BuildKite Cron → ECS Task Definition → Fargate Container → Singer Tap → S3 Raw
     (2 AM)         (Task Config)      (Docker Run)    (Extract)   (NDJSON)
```

#### Scheduling Configuration

**Frequency Patterns:**
- **Daily Extraction** - Most common for CRM and e-commerce data
- **Hourly Sync** - High-frequency sources like advertising platforms
- **Weekly Jobs** - Large datasets or rate-limited APIs
- **Custom Schedules** - Customer-specific requirements

**Example BuildKite Pipeline:**
```yaml
steps:
  - label: "Salesforce Extraction - Acme Corp"
    command: |
      aws ecs run-task \
        --cluster cdp-extraction \
        --task-definition salesforce-tap:latest \
        --launch-type FARGATE \
        --network-configuration "awsvpcConfiguration={subnets=[subnet-abc123],securityGroups=[sg-def456]}"
    env:
      CUSTOMER_ID: acme_corp
      PROVIDER: salesforce
      S3_BUCKET: cdp-raw-bucket
    retry:
      automatic:
        - exit_status: "*"
          limit: 3
```

#### Performance & Scaling

**Resource Management:**
- **CPU Allocation** - 0.25-4 vCPU per task based on data volume
- **Memory Limits** - 512MB-30GB depending on extraction complexity
- **Concurrent Tasks** - Up to 1000 tasks per region
- **Network Bandwidth** - 10 Gbps max per task

**Optimization Strategies:**
- **Parallel Extraction** - Multiple customers processed simultaneously
- **Incremental Loading** - Only extract changed records since last run
- **Compression** - GZIP reduces storage and transfer costs by 70-80%
- **Batch Sizing** - 20k records optimal for memory usage and S3 performance

#### Error Handling & Monitoring

**Error Types & Responses:**
- **API Rate Limits** - Exponential backoff with jitter (30s, 60s, 120s)
- **Authentication Failures** - Alert engineering team, pause extraction
- **Network Timeouts** - Retry with increased timeout (up to 30 minutes)
- **Data Validation Errors** - Send invalid records to Dead Letter Queue

**Monitoring & Alerting:**
- **CloudWatch Metrics** - Task success/failure rates, duration, resource usage
- **Custom Dashboards** - Real-time extraction status across all customers
- **Slack Notifications** - Failed jobs, high error rates, SLA breaches
- **Daily Reports** - Extraction summary with record counts and timing

**Recovery Procedures:**
- **Failed Tasks** - Automatic retry up to 3 attempts
- **Partial Failures** - Resume from last successful state
- **Data Corruption** - Rollback to previous state, re-extract affected period
- **Infrastructure Issues** - Failover to secondary AWS region

#### Benefits of This Architecture

**Operational Advantages:**
- **Serverless** - No infrastructure management overhead
- **Cost Effective** - Pay only for actual extraction time
- **Scalable** - Handle hundreds of customers and data sources
- **Reliable** - Built-in retry and error handling mechanisms
- **Standardized** - Singer specification ensures consistent data format

**Developer Benefits:**
- **Easy Onboarding** - New data sources follow Singer patterns
- **Version Control** - Docker images provide consistent environments
- **Debugging** - Detailed logs in CloudWatch for troubleshooting
- **Testing** - Local Docker execution for development
- **Monitoring** - Comprehensive metrics and alerting

### PySpark Transformation (Data Processing Engine)

The PySpark Transformation layer serves as the core data processing engine that converts raw, unstructured data from S3 Raw into clean, enriched, and analytics-ready datasets.

#### Purpose
- **Data Quality** - Cleanse, validate, and standardize incoming data
- **Data Enrichment** - Enhance records with additional context and insights
- **Schema Alignment** - Normalize data formats across different sources
- **Performance Optimization** - Partition and optimize data for downstream analytics

#### Architecture Overview

**Core Components:**
- **AWS Glue/EMR** - Managed Spark execution environment
- **PySpark Jobs** - Data transformation logic and workflows
- **Apache Iceberg** - Modern table format for ACID transactions
- **Data Catalog** - Centralized metadata and schema registry
- **S3 Processed** - Curated data lake for analytics workloads

#### Processing Modes

The transformation engine supports two distinct processing modes to handle different data scenarios and business requirements.

##### 1. Incremental Mode (Default)

**Purpose:** Process only new or changed data since the last transformation run.

**Characteristics:**
- **Daily Processing** - Runs every night after data extraction
- **Delta Detection** - Identifies new files in S3 Raw since last run
- **Fast Processing** - Processes only changed data (typically last 1-7 days)
- **Low Latency** - Data available in 2-4 hours after ingestion
- **Cost Efficient** - Processes minimal data volumes

**How It Works:**
```
S3 Raw → Delta Detection → PySpark Transform → S3 Processed → Database Update
  ↓           ↓                 ↓                ↓               ↓
New Files   Last Run      Process Delta     Merge/Upsert    Incremental
Since T-1   Timestamp     Data Only         Tables          Refresh
```

**Incremental Processing Logic:**
1. **State Tracking** - Read last successful run timestamp from state file
2. **Delta Detection** - Scan S3 Raw for files newer than last run
3. **Partition Processing** - Process only affected date partitions
4. **Merge Strategy** - Upsert new/changed records into existing tables
5. **State Update** - Update state file with current run timestamp

**Example Incremental Run:**
```python
# Read state from previous run
last_run = read_state("s3://cdp-state/acme_corp/last_transform_run.json")
# last_run = "2025-01-14T23:00:00Z"

# Find new files since last run
new_files = spark.read.parquet("s3://cdp-raw/acme_corp/") \
    .filter(col("file_timestamp") > last_run) \
    .select("file_path").collect()

# Process only new data
for file in new_files:
    df = spark.read.json(file.file_path)
    clean_df = transform_data(df)
    
    # Merge into existing table
    existing_table = spark.read.parquet("s3://cdp-processed/acme_corp/customers/")
    merged_df = merge_upsert(existing_table, clean_df, key="customer_id")
    
    # Write back to processed zone
    merged_df.write.mode("overwrite").parquet("s3://cdp-processed/acme_corp/customers/")
```

**Benefits:**
- **Speed** - 10-100x faster than full reprocessing
- **Cost** - Processes only changed data, reducing compute costs
- **Freshness** - Near real-time data availability
- **Resources** - Minimal cluster size and runtime

**Use Cases:**
- **Daily Operations** - Regular nightly data processing
- **Real-time Analytics** - Fresh data for dashboards and reports
- **Event Processing** - User actions, transactions, behavioral data
- **Operational Reporting** - Daily/weekly business metrics

##### 2. Historic Mode (On-Demand)

**Purpose:** Reprocess entire historical dataset for backfills, migrations, or major schema changes.

**Characteristics:**
- **Full Reprocessing** - Processes all available historical data
- **Complete Rebuild** - Recreates entire curated dataset from scratch
- **High Throughput** - Uses large Spark clusters for parallel processing
- **Long Running** - Can take 6-24 hours depending on data volume
- **Resource Intensive** - Requires significant compute and memory

**How It Works:**
```
S3 Raw → Full Scan → Parallel Processing → Complete Rebuild → Database Reload
  ↓         ↓              ↓                    ↓               ↓
All Files  Years of     Large Cluster      Replace All     Full Table
History    Data         Processing         Tables          Refresh
```

**Historic Processing Logic:**
1. **Full Scan** - Read all files from S3 Raw (all dates/customers)
2. **Cluster Scaling** - Provision large EMR cluster (50-200 nodes)
3. **Parallel Processing** - Process multiple customers/dates simultaneously
4. **Complete Rebuild** - Recreate all tables from scratch
5. **Atomic Replacement** - Replace production tables atomically

**Example Historic Run:**
```python
# Read ALL historical data
all_data = spark.read.json("s3://cdp-raw/*/*/*/*/")  # All customers, all dates

# Process in parallel by customer
customers = all_data.select("customer_id").distinct().collect()

def process_customer(customer_id):
    # Read all data for this customer
    customer_data = all_data.filter(col("customer_id") == customer_id)
    
    # Apply all transformations
    clean_data = transform_data(customer_data)
    enrich_data = enrich_customer_profiles(clean_data)
    final_data = apply_business_rules(enrich_data)
    
    # Write to new table location
    final_data.write.mode("overwrite") \
        .parquet(f"s3://cdp-processed-new/{customer_id}/customers/")

# Process all customers in parallel
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=10) as executor:
    executor.map(process_customer, [c.customer_id for c in customers])

# Atomically replace production tables
replace_production_tables("s3://cdp-processed-new/", "s3://cdp-processed/")
```

**Benefits:**
- **Completeness** - Ensures all historical data is properly processed
- **Consistency** - Uniform application of latest business rules
- **Recovery** - Rebuilds data after corruption or major errors
- **Migration** - Supports major schema or logic changes

**Use Cases:**
- **Initial Setup** - First-time customer onboarding
- **Schema Migration** - Major changes to data structure
- **Data Recovery** - Recovering from data corruption
- **Algorithm Updates** - Applying new enrichment logic to all data
- **Compliance** - Reprocessing for regulatory requirements

#### Transformation Pipeline

**Data Processing Steps:**

1. **Data Ingestion**
   ```python
   # Read raw NDJSON data from S3
   raw_df = spark.read.option("multiline", "false") \
       .json("s3://cdp-raw/acme_corp/salesforce/2025/01/15/")
   ```

2. **Schema Validation**
   ```python
   # Validate against expected schema
   expected_schema = load_schema("salesforce_customer_v2.json")
   validated_df = validate_schema(raw_df, expected_schema)
   ```

3. **Data Cleaning**
   ```python
   # Remove duplicates, fix data types, handle nulls
   clean_df = raw_df \
       .dropDuplicates(["customer_id", "email"]) \
       .withColumn("created_date", to_timestamp("created_date")) \
       .fillna({"country": "Unknown", "revenue": 0})
   ```

4. **Data Normalization**
   ```python
   # Standardize formats across providers
   normalized_df = clean_df \
       .withColumn("email", lower(col("email"))) \
       .withColumn("phone", regexp_replace(col("phone"), "[^0-9]", "")) \
       .withColumn("country", map_country_codes(col("country")))
   ```

5. **Data Enrichment**
   ```python
   # Add derived fields and external data
   enriched_df = normalized_df \
       .withColumn("customer_segment", calculate_segment(col("revenue"))) \
       .withColumn("geo_location", geocode_address(col("address"))) \
       .join(external_company_data, "domain", "left")
   ```

6. **Quality Validation**
   ```python
   # Apply data quality rules
   quality_checks = [
       ("email_format", col("email").rlike(r"^[^@]+@[^@]+\.[^@]+$")),
       ("revenue_positive", col("revenue") >= 0),
       ("required_fields", col("customer_id").isNotNull())
   ]
   
   validated_df = apply_quality_checks(enriched_df, quality_checks)
   ```

7. **Output Partitioning**
   ```python
   # Partition for optimal query performance
   final_df.write \
       .partitionBy("year", "month", "customer_segment") \
       .mode("overwrite") \
       .parquet("s3://cdp-processed/acme_corp/customers/")
   ```

#### Execution Environment

**AWS Glue (Serverless):**
- **Auto-scaling** - Automatically provisions compute resources
- **Pay-per-use** - Only pay for actual processing time
- **Managed Service** - No cluster management overhead
- **Integration** - Native S3 and Glue Catalog integration

**Amazon EMR (Managed Clusters):**
- **High Performance** - Optimized Spark clusters for large workloads
- **Customization** - Full control over cluster configuration
- **Cost Optimization** - Spot instances for batch processing
- **Scaling** - Dynamic cluster resizing based on workload

**Resource Allocation:**

**Incremental Mode:**
- **Cluster Size** - 2-5 nodes (small cluster)
- **Instance Types** - m5.xlarge to m5.2xlarge
- **Memory** - 8-16 GB per executor
- **Runtime** - 30 minutes to 2 hours
- **Cost** - $10-50 per run

**Historic Mode:**
- **Cluster Size** - 20-200 nodes (large cluster)
- **Instance Types** - r5.4xlarge to r5.8xlarge (memory-optimized)
- **Memory** - 32-64 GB per executor
- **Runtime** - 4-24 hours
- **Cost** - $500-5000 per run

#### Data Quality Framework

**Quality Dimensions:**
- **Completeness** - Required fields are populated
- **Accuracy** - Data values are correct and valid
- **Consistency** - Data formats are standardized
- **Timeliness** - Data is processed within SLA
- **Uniqueness** - No duplicate records exist

**Quality Rules Engine:**
```python
quality_rules = {
    "customers": [
        {"rule": "email_unique", "check": "count(email) = count(distinct email)"},
        {"rule": "revenue_range", "check": "revenue between 0 and 1000000"},
        {"rule": "required_fields", "check": "customer_id is not null"},
        {"rule": "email_format", "check": "email matches '^[^@]+@[^@]+\\.[^@]+$'"}
    ],
    "orders": [
        {"rule": "order_total_positive", "check": "order_total > 0"},
        {"rule": "order_date_valid", "check": "order_date >= '2020-01-01'"},
        {"rule": "customer_exists", "check": "customer_id in (select customer_id from customers)"}
    ]
}
```

**Quality Reporting:**
- **Quality Score** - Percentage of records passing all quality checks
- **Rule Violations** - Detailed breakdown of failed quality rules
- **Trend Analysis** - Quality metrics over time
- **Alerting** - Notifications when quality scores drop below threshold

#### Performance Optimization

**Partitioning Strategy:**
```
s3://cdp-processed/acme_corp/customers/
├── year=2025/
│   ├── month=01/
│   │   ├── segment=enterprise/
│   │   ├── segment=mid_market/
│   │   └── segment=smb/
│   └── month=02/
│       ├── segment=enterprise/
│       ├── segment=mid_market/
│       └── segment=smb/
```

**File Optimization:**
- **File Size** - Target 128-512 MB per file for optimal S3 performance
- **Compression** - Snappy compression for balance of speed and size
- **Format** - Parquet for columnar analytics workloads
- **Compaction** - Regular file compaction to prevent small file problems

**Caching Strategy:**
- **Broadcast Joins** - Cache small dimension tables in memory
- **Checkpointing** - Persist intermediate results for complex transformations
- **Dynamic Allocation** - Adjust executor count based on workload

#### Monitoring & Observability

**Metrics Tracking:**
- **Processing Time** - Duration of each transformation job
- **Data Volume** - Records processed per run
- **Error Rates** - Failed records and transformation errors
- **Resource Utilization** - CPU, memory, and network usage

**Alerting Rules:**
- **Job Failures** - Alert on transformation job failures
- **SLA Breaches** - Alert when processing exceeds time limits
- **Quality Degradation** - Alert when data quality scores drop
- **Resource Limits** - Alert on high memory or CPU usage

**Logging Strategy:**
- **Structured Logs** - JSON-formatted logs for easy parsing
- **Correlation IDs** - Track records through entire pipeline
- **Error Context** - Detailed error information for debugging
- **Performance Metrics** - Execution times and resource usage

#### Benefits of This Architecture

**Technical Advantages:**
- **Flexibility** - Support both incremental and full reprocessing
- **Scalability** - Handle terabytes of data with auto-scaling
- **Reliability** - Built-in retry logic and error handling
- **Performance** - Optimized for both speed and cost efficiency

**Business Benefits:**
- **Fresh Data** - Near real-time data availability for analytics
- **Data Quality** - Automated quality checks and validation
- **Cost Control** - Efficient incremental processing reduces costs
- **Compliance** - Audit trails and data lineage tracking




