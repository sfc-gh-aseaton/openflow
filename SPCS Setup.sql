-----------------------------------------------------------------------
-- Core Setup
-----------------------------------------------------------------------

-- Set context and create the Openflow Admin role
USE ROLE ACCOUNTADMIN;

-- Create the OPENFLOW_ADMIN role
CREATE ROLE IF NOT EXISTS OPENFLOW_ADMIN;

-- Grant the role to ACCOUNTADMIN and other required users
GRANT ROLE OPENFLOW_ADMIN TO ROLE ACCOUNTADMIN;
GRANT ROLE OPENFLOW_ADMIN TO USER MYUSER;

-- Openflow requires the default role to not be a privileged role
ALTER USER MYUSER SET DEFAULT_ROLE = OPENFLOW_ADMIN;

CREATE DATABASE IF NOT EXISTS OPENFLOW;
CREATE SCHEMA IF NOT EXISTS OPENFLOW.OPENFLOW;

-----------------------------------------------------------------------
-- Grant Privileges
-----------------------------------------------------------------------

-- Grant required Openflow privileges to OPENFLOW_ADMIN role
GRANT CREATE OPENFLOW DATA PLANE INTEGRATION ON ACCOUNT TO ROLE OPENFLOW_ADMIN;
GRANT CREATE OPENFLOW RUNTIME INTEGRATION ON ACCOUNT TO ROLE OPENFLOW_ADMIN;

-- Compute pools is required for Openflow Deployments
GRANT CREATE COMPUTE POOL ON ACCOUNT TO ROLE OPENFLOW_ADMIN;

-- We want the Openflow Admin to create and own the Runtime Roles later on
GRANT CREATE ROLE ON ACCOUNT TO ROLE OPENFLOW_ADMIN;
-- You can revoke this later if you want to

-- We also want the Admin to create and use the event table later
GRANT USAGE ON DATABASE OPENFLOW TO ROLE OPENFLOW_ADMIN;
GRANT USAGE ON SCHEMA OPENFLOW.OPENFLOW TO ROLE OPENFLOW_ADMIN;
GRANT CREATE EVENT TABLE ON SCHEMA OPENFLOW.OPENFLOW TO ROLE OPENFLOW_ADMIN;

-- We also want the Admin to have access to the Warehouse
GRANT USAGE, OPERATE ON WAREHOUSE MY_SUITABLE_WH TO ROLE OPENFLOW_ADMIN;


-----------------------------------------------------------------------
-- * * * * * * * * * * * 
-- Create Openflow Deployment in the GUI using the OPENFLOW_ADMIN Role!!
-- * * * * * * * * * * * 
-----------------------------------------------------------------------


-- Set the context for the session
USE DATABASE OPENFLOW;
USE SCHEMA OPENFLOW;
USE WAREHOUSE MY_SUITABLE_WH;
USE ROLE OPENFLOW_ADMIN;

-- Create Event Table
CREATE EVENT TABLE IF NOT EXISTS OPENFLOW.OPENFLOW.EVENTS COMMENT = 'Event table for Openflow deployment logging and monitoring';

-- List Data Planes
SHOW OPENFLOW DATA PLANE INTEGRATIONS;

-- Swap Data Plane ID into the statement
ALTER OPENFLOW DATA PLANE INTEGRATION OPENFLOW_DATAPLANE_123456789_3054_4AF5_BDF0_4B4306E29EFB
SET EVENT_TABLE = 'OPENFLOW.OPENFLOW.EVENTS';

-----------------------------------------------------------------------
-- Create Runtime Role
-----------------------------------------------------------------------

-- Create runtime role for Openflow operations
USE ROLE OPENFLOW_ADMIN;
-- Create the runtime role
CREATE ROLE IF NOT EXISTS OPENFLOW_RUNTIME;

-- Grant the runtime role to OPENFLOW_ADMIN for management
GRANT ROLE OPENFLOW_RUNTIME TO ROLE OPENFLOW_ADMIN;

-- Grant the runtime role to the current user
GRANT ROLE OPENFLOW_RUNTIME TO USER MYUSER;

-- Grant runtime privileges
USE ROLE ACCOUNTADMIN;

-- Database and schema access for Openflow
GRANT USAGE ON DATABASE OPENFLOW TO ROLE OPENFLOW_RUNTIME;
GRANT USAGE ON SCHEMA OPENFLOW.OPENFLOW TO ROLE OPENFLOW_RUNTIME;

-- Allow creation of schemas in Openflow DB (necessary for CDC connectors)
GRANT CREATE SCHEMA ON DATABASE OPENFLOW TO ROLE OPENFLOW_RUNTIME; 

-- Warehouse usage for runtime operations
GRANT USAGE, OPERATE ON WAREHOUSE MY_SUITABLE_WH TO ROLE OPENFLOW_RUNTIME;

-- Table creation and management privileges
GRANT CREATE TABLE ON SCHEMA OPENFLOW.OPENFLOW TO ROLE OPENFLOW_RUNTIME;
GRANT CREATE VIEW ON SCHEMA OPENFLOW.OPENFLOW TO ROLE OPENFLOW_RUNTIME;
GRANT CREATE STAGE ON SCHEMA OPENFLOW.OPENFLOW TO ROLE OPENFLOW_RUNTIME;

-- Event table access for logging
GRANT INSERT ON EVENT TABLE OPENFLOW.OPENFLOW.EVENTS TO ROLE OPENFLOW_RUNTIME;
GRANT SELECT ON EVENT TABLE OPENFLOW.OPENFLOW.EVENTS TO ROLE OPENFLOW_RUNTIME;

-------------------------------------------------------------------------------------------------------
-- Create Network Rules - SPCS Egress is blocked by default so we must whitelist everything required
-------------------------------------------------------------------------------------------------------

USE ROLE ACCOUNTADMIN;

-- Example Rules (recommended to group them in a single schema for organisation)

CREATE OR REPLACE NETWORK RULE OPENFLOW.OPENFLOW.ALLOW_SHAREPOINT
  MODE = EGRESS
  TYPE = HOST_PORT
  VALUE_LIST = ('*.sharepoint.com:443', 'login.microsoftonline.com:443', 'login.microsoft.com:443', 'www.office.com:443','graph.microsoft.com:443', 'developer.microsoft.com:443');

CREATE OR REPLACE NETWORK RULE OPENFLOW.OPENFLOW.ALLOW_SFDC
  MODE = EGRESS
  TYPE = HOST_PORT
  VALUE_LIST = ('login.salesforce.com:443', '*.salesforce.com:443');

CREATE OR REPLACE NETWORK RULE OPENFLOW.OPENFLOW.ALLOW_SQLSVR
  MODE = EGRESS
  TYPE = HOST_PORT
  VALUE_LIST = ('ali-sql-svr.c50usmosavrd.eu-central-1.rds.amazonaws.com:1433');

CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION OPENFLOW_EAI
   ALLOWED_NETWORK_RULES = ( OPENFLOW.OPENFLOW.ALLOW_SHAREPOINT,
                             OPENFLOW.OPENFLOW.ALLOW_SFDC,
                             OPENFLOW.OPENFLOW.ALLOW_SQLSVR )
   ENABLED = TRUE;

GRANT USAGE ON INTEGRATION OPENFLOW_EAI TO ROLE OPENFLOW_RUNTIME;
GRANT USAGE ON INTEGRATION OPENFLOW_EAI TO ROLE OPENFLOW_ADMIN;

-----------------------------------------------------------------------
-- * * * * * * * * * * * 
-- Create Openflow Runtime in the GUI using the OPENFLOW_ADMIN Role!!
-- Specify the Runtime/Snowflake Role and the EAI
-- * * * * * * * * * * * 
-----------------------------------------------------------------------
