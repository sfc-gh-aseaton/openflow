# Lab 03 - Unstructued Data
Openflow has a range of connectors designed to ingest documents from Unstructued sources such as Google Drive, Sharepoint, Box, etc. They are designed for Enterprise use and require appropriate setup of credentials and permissions.

For this lab we will use a pre-built custom flow that uses core NiFi connectivity that can connect to a regular/personal Google Drive account to simulate ingestion from an enterprise unstructured source.

> 💡 Ensure you created the Network rule described in [Lab 00](Lab%2000%20-%20Initial%20Setup.md) to allow access to the Google Services we will use for the lab

## Download flow template

First Download the [Lab 03 Openflow flow design](Lab%2003.json) file to your local PC.

On the Openflow canvas GUI, drag a Processor Group onto your root canvas, on the right of the name input field click the indicated icon to browse for the flow definition. Selected the downloaded JSON from the previous step, confirm/configure the name and click **"Add"**

![](images/img18.png)

Double-click to enter the Process Group, you should find a simple flow consisting of just 3 processors. 

![](images/img18b.png)

The first processor **ListGoogleDrive** connects to Google Drive and gets a file listing, creating one empty flow file for each file in the identified folder using attributes to store metadata about the source file.

The second processor **FetchGoogleDrive** actually retrieves the source file identified by '${drive.id}' - default settings are used to convert all Google Docs, Sheets, Slides into PDFs

Finally the third processor **PutSnowflakeInternalStageFile** is used to PUT the retrieved file into a Snowflake stage `OPENFLOW.LAB3.GDRIVE` which we must now create to be ready to execute. We will also allow task execution for our Openflow runtime role (needed for later)

```
USE ROLE OPENFLOW_RUNTIME;
CREATE SCHEMA OPENFLOW.LAB3;
CREATE STAGE OPENFLOW.LAB3.GDRIVE ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE');

USE ROLE ACCOUNTADMIN;
GRANT EXECUTE TASK ON ACCOUNT TO ROLE OPENFLOW_RUNTIME;

```



As well as the 3 processors, the flow contains the configuration for two controller services. Right click the empty canvas and choose "Controller Services" to view them

| Controller service | Description |
|----------|-------|
| **GCPCredentialsControllerService** | A service to manage Google authentication |
| **SnowflakeConnectionService** | Manages connectivity to Snowflake |

The SnowflakeConnectionService is set to use "Snowflake Managed Token" authentication, which uses an SPCS session token so it requires no configuration. Choose **"Enable"** from the context menu to start the service.

To configure the GCP credentials during the lab you'll be provided with a Service Account JSON containing the keys for access to a shared GDrive folder. Edit the service and paste the contents of the JSON file into the required parameter. Apply and Enable the service

