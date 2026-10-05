# Lab 01 - Database Integration

Before deploying the Postgres CDC connector we need to prepare a few things. First, create the database password as a SECRET in Snowflake:

```sql
USE ROLE OPENFLOW_ADMIN;
CREATE SECRET OPENFLOW.OPENFLOW.poland_pg18
  TYPE = GENERIC_STRING
  SECRET_STRING = 'Warsaw2026!';

GRANT READ ON SECRET OPENFLOW.OPENFLOW.poland_pg18 TO ROLE OPENFLOW_RUNTIME;
```

> 💡 Ensure you created the network rule described in [Lab 00](Lab%2000%20-%20Initial%20Setup.md) to allow access to the Postgres DB we will use for the lab

Now download the latest Postgres JDBC driver:
[https://jdbc.postgresql.org/download/](https://jdbc.postgresql.org/download/)

![](images/img5b.png)

Now let's proceed with the connector deployment from the Openflow Control UI

![](images/img6.png)

Select your runtime and give your connector a name

![](images/img7.png)

Configure the connector with the following values

|Parameter|Value|
|--|--|
|Source Database Connection URL|`jdbc:postgresql://2mo2z2j54na6fni3735enmtiti.sfseeurope-aseaton.us-west-2.aws.postgres.snowflake.app:5432/postgres`|
|Source Database Driver|(upload) the driver jar you downloaded, e.g. `postgresql-42.7.13.jar`|
|Source Database User|`roadshow_ro`|
|Source Database Password|(select secret) `POLAND_PG18`|
|Source Database Publication Name|`openflow_pub`|

![](images/img8.png)

Select all tables in the `tastybytes` schema and click Next. For column-level replication behaviour just accept the defaults and click Next

![](images/img9.png)

For Destination details, specify OPENFLOW as the target database, and choose your Snowflake warehouse. For all other settings you can accept the defaults. Read and understand the options available, but you do not need to change anything

![](images/img10.png)

Tuning and Migration details can all be left as default values. On the final Summary page click **Verify configuration** and, once the validation has completed successfully, choose **Apply**. The connector will now deploy.

![](images/img11.png)

Once the connector has deployed, click the 3 dot context menu and choose **Start**. After the connector has had time to start processing, observe in Snowsight that the schema `OPENFLOW.TASTYBYTES` has been created and populated with tables from the source Postgres database

![](images/img12.png)

Navigate to the Connector Observability dashboard (Ingestion -> Openflow), check the metrics and status, and validate everything is correct. In class we will then start making changes in the source database so you can observe the CDC behaviour

# Lab 01b - Manual flow (Advanced)

Manually build a flow for custom database integration. This is more complicated and requires some experience (and/or exploration!)

**Tips:**
* Start on the Openflow canvas
* Create a Process Group and work inside it
* Create a Parameter Context and add a Parameter to reference an asset - upload the Postgres driver jar
* Create a DBCPConnectionPool controller service, configure and enable it
* You'll also need to create JsonRecordSetWriter and StandardWebClientServiceProvider controller services (enable them with default settings)
* Create a simple flow QueryDatabaseTableRecord → PublishSnowpipeStreaming
* The source table is `tastybytes.order_header`; specify your DB connection pool and record writer
* Try a **Run once** and view the results in the queue, then download the JSON file to help with target table creation
* Create the target table with all columns using the Snowsight UI loader and the JSON file
* Set up the target PublishSnowpipeStreaming processor with `Transfer Strategy = Rows` and `Channel Type = Elastic`
