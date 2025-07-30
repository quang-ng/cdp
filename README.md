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
                       │
             ┌─────────│────────┐
             │                  │
   ┌─────────▼──────┐    ┌──────▼─────────┐
   │  Database      │    │ Elasticsearch  │
   │ (PostgreSQL)   │    │ (Search &      │
   │                │    │  Analytics)    │
   │ • Customer     │    │                │
   │   Tables       │    │                │
   │ • Event Tables │    │                │
   │ • Product      │    │                │
   │   Tables       │    │                │
   └──────┬─────────┘    └────────────────┘
          │                        │
          │                        │
   ┌──────▼──────┐                 │
   │    API      │                 │
   │ (Enrichment │                 │
   │   & Query)  │                 │
   └─────────────┘                 │
                                   │
                                   │
   ┌───────────────────────────────▼──────────┐
   │ Segmentation   Analytics   Reporting     │
   │                                          │            
   │ • Behavioral Segments                    │
   │ • Demographic Groups                     │
   │ • ML Models                              │
   │ • Customer Insights                      │
   │ • Cohort Analysis                        │
   │ • AI-Powered Insights                    │
   │ • Dashboards                             │
   │ • KPIs                                   │
   │ • Business Intelligence                  │
   │ • Real-time Metrics                      │
   └─────────┬────────────────────────────────┘
             │
             ▼
   ┌───────────────────────┐
   │    Activation         │
   │                       │
   │ • Email Service       │
   │ • Facebook Ads        │
   │ • Google Ads          │
   │ • Other Marketing     │
   │   Platforms           │
   └───────────────────────┘
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
│   │   │   │   │   ├── order_20250115T010000.ndjson.gzip (5k records)
│   │   │   │   │   ├── product_20250115T010000.ndjson.gzip (500 records)
│   │   │   │   │   ├── customer_batch_002.ndjson.gzip (20k records)
│   │   │   │   │   ├── order_20250115T020000.ndjson.gzip (4.5k records)
│   │   │   │   │   ├── product_20250115T020000.ndjson.gzip (480 records)
│   │   │   │   │   └── customer_batch_003.ndjson.gzip (15k records)
│   │   │   │   └── day=16/
│   │   │   │       ├── customer_batch_001.ndjson.gzip
│   │   │   │       ├── order_20250116T010000.ndjson.gzip
│   │   │   │       └── product_20250116T010000.ndjson.gzip
│   ├── shopify/
│   │   ├── year=2025/
│   │   │   ├── month=01/
│   │   │   │   ├── day=15/
│   │   │   │   │   ├── customer_batch_001.ndjson.gzip
│   │   │   │   │   ├── order_20250115T030000.ndjson.gzip
│   │   │   │   │   ├── product_20250115T030000.ndjson.gzip
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
2. **Schema Validation**
3. **Data Cleaning**
4. **Data Normalization**
5. **Data Enrichment**
6. **Quality Validation**
7. **Output Partitioning**: parquet files


#### Infrastructure Setup for PySpark on ECS Fargate

Running PySpark on ECS Fargate provides greater control, cost efficiency, and seamless integration with the existing CDP infrastructure.

##### Why ECS Fargate for PySpark?

**Advantages:**
- **Consistency** - Same infrastructure as data extraction pipeline
- **Cost Control** - Pay only for actual compute time, no cluster overhead
- **Flexibility** - Custom Spark configurations and Python dependencies
- **Integration** - Native integration with existing ECS services and monitoring
- **Scalability** - Independent scaling per transformation job

**Architecture Overview:**
```
BuildKite Scheduler → ECS Task Definition → Fargate Container → PySpark Job → S3 Processed
      (Cron)            (Job Config)        (Spark Runtime)    (Transform)   (Output)
```

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


### S3 Processed → Database: Data Loading Flow

The following diagram illustrates how curated data moves from S3 Processed to the Database in both Incremental and Historic modes:

```
           Incremental Mode (Default)                  Historic Mode (Full Reload)
┌───────────────────────────────┐                ┌───────────────────────────────┐
│   S3 Processed (Curated)      │                │   S3 Processed (Curated)      │
│   (New/Changed Partitions)    │                │   (All Partitions)            │
└──────────────┬────────────────┘                └──────────────┬────────────────┘
               │                                             │
               │                                             │
      Delta Detection & State Tracking               Full Scan of All Data
               │                                             │
               ▼                                             ▼
        Data Extraction                              Data Extraction
               │                                             │
               ▼                                             ▼
   Transformation/Mapping (if needed)           Transformation/Mapping (if needed)
               │                                             │
               ▼                                             ▼
        Upsert/Merge into DB                        Truncate & Bulk Load
               │                                             │
               ▼                                             ▼
   Update State for Next Run                        Integrity Checks & State Reset
```

**Incremental Mode:**
- Detects and loads only new or changed data since the last run.
- Uses upsert/merge logic to keep database in sync with minimal lag.
- Fast, cost-efficient, and suitable for daily operations.

**Historic Mode:**
- Loads all curated data, typically after schema changes or for backfills.
- Truncates and reloads entire tables for full consistency.
- Resource-intensive, used for migrations or recovery.


### Activation Pipeline: Simple Data Flow

1. **Segment Selection**
   - Query the database or data warehouse for users matching your criteria (e.g., bought > $50).
   - Always export the results to S3 as Parquet files (columnar format), regardless of segment size.

2. **Audience Export**
   - The list of users (emails, IDs) is always written to S3 as Parquet files.
   - For large segments, split into multiple files for efficient processing.

3. **Channel Integration**
   - The activation service reads the audience from S3 or receives it via API.
   - Upload the list to your email or ad platform using their bulk import features.

4. **Personalization**
   - Join user details (like name) in batch before export, so all personalization data is included in the Parquet file. Avoid per-user database queries (no N+1 problem).
   - Use templates stored in your email/ad platform.

5. **Send & Monitor**
   - The platform sends the campaign to users.
   - Track delivery, opens, clicks, and conversions.
   - Export these results back to your CDP for analytics.

6. **Feedback Loop**
   - Store campaign results in your analytics tables or data warehouse.
   - Use this data for future targeting and reporting.

**For all segments:**
- Always use S3 for storage and process in batches if needed.
- Store all segment and audience data in Parquet files for efficient analytics and processing.
- Use the bulk import and reporting features of your marketing platforms.