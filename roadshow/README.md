# Snowflake Partners Openflow Roadshow

Hands-on labs for building data integration pipelines with [Snowflake Openflow](https://docs.snowflake.com/en/user-guide/data-integration/openflow/about) running on Snowpark Container Services (SPCS). You will set up an Openflow deployment, replicate a Postgres database with a CDC connector, build custom flows on the Openflow canvas, ingest unstructured documents for a RAG pipeline, and reach a private endpoint through the Data Connectivity Proxy.

## Prerequisites

* A Snowflake account where you can use the `ACCOUNTADMIN` role
* A warehouse for Openflow to use
* For Lab 04: [Docker](https://www.docker.com/) or [Podman](https://podman.io/) and Python 3 on your local machine
* Lab-specific credentials (the Lab 03 decryption password) will be provided by your instructor

## Labs

Work through the labs in order — later labs depend on the roles, deployment, runtime and network rules created in Lab 00.

| Lab | Description |
|-----|-------------|
| [Lab 00 - Initial Setup](Lab%2000%20-%20Initial%20Setup.md) | Create roles and permissions, an Openflow deployment and runtime, and the network rules used by the other labs |
| [Lab 01 - Database Integration](Lab%2001%20-%20Database%20Integration.md) | Deploy the PostgreSQL CDC connector to replicate the `tastybytes` schema, plus an optional manual flow (advanced) |
| [Lab 02 - Custom HTTP API](Lab%2002%20-%20Custom%20HTTP%20API.md) | Build a custom flow on the canvas that calls a REST API and streams the results into a table with Snowpipe Streaming |
| [Lab 03 - Unstructured Data](Lab%2003%20-%20Unstructured%20Data.md) | Import a flow that loads Google Drive documents into a stage, then build a Cortex Search service for RAG |
| [Lab 04 - Data Connectivity Proxy](Lab%2004%20-%20Data%20Connectivity%20Proxy.md) | Run the DCP agent locally and connect Openflow in Snowflake to an endpoint on your own machine |

## Supporting files

| File | Used in | Description |
|------|---------|-------------|
| [`SPCS Setup.sql`](../SPCS%20Setup.sql) | Lab 00 | Cheat sheet with the SQL for roles, grants, deployment and runtime setup |
| [`Lab 03.json`](Lab%2003.json) | Lab 03 | Openflow flow definition for the Google Drive ingestion flow |
| [`mock_endpoint.py`](mock_endpoint.py) | Lab 04 | Local HTTP server on port 8080 that echoes request details as JSON |
| [`images/`](images) | All labs | Screenshots referenced by the lab guides |
| [Setup slides (PDF)](../%5BEE%5D%20-%20Partners%20Openflow%20Roadshow%20-%20Setup.pdf) | — | Roadshow setup presentation |

## Useful documentation

* [Set up Openflow - Snowflake Deployment](https://docs.snowflake.com/en/user-guide/data-integration/openflow/setup-openflow-spcs)
* [Data Connectivity Proxy](https://docs.snowflake.com/en/user-guide/data-connectivity-proxy)
* [Snowpipe Streaming Elastic Channels](https://docs.snowflake.com/en/user-guide/snowpipe-streaming/snowpipe-streaming-elastic-channels-overview)
* [Apache NiFi Expression Language Guide](https://nifi.apache.org/docs/nifi-docs/html/expression-language-guide.html)
