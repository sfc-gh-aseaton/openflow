# Lab 00 - Initial Setup

Setup Snowflake roles, permissions and Openflow SPCS deployment

**Cheat Sheet:**  
[https://github.com/sfc-gh-aseaton/openflow/blob/main/SPCS%20Setup.sql](https://github.com/sfc-gh-aseaton/openflow/blob/main/SPCS%20Setup.sql)

**Official Docs:**  
[https://docs.snowflake.com/en/user-guide/data-integration/openflow/setup-openflow-spcs](https://docs.snowflake.com/en/user-guide/data-integration/openflow/setup-openflow-spcs)

**Snowsight UI Steps \- Create Deployment:**

![](images/img1.png)

![](images/img2.png)

![](images/img3.png)

![](images/img4.png)

![](images/img5.png)

**Networking:**

The quickstart cheat sheet gave some examples for allowing outbound connectivity from Snowflake SPCS to data sources. For the labs you need to create these rules:

```
CREATE OR REPLACE NETWORK RULE OPENFLOW.OPENFLOW.pg_rule  
  MODE = EGRESS  
  TYPE = HOST_PORT  
  VALUE_LIST = ('2mo2z2j54na6fni3735enmtiti.sfseeurope-aseaton.us-west-2.aws.postgres.snowflake.app:5432');

CREATE OR REPLACE NETWORK RULE OPENFLOW.OPENFLOW.json_rule  
  MODE = EGRESS  
  TYPE = HOST_PORT  
  VALUE_LIST = ('dummyjson:443');

CREATE OR REPLACE NETWORK RULE goog_rule
  MODE = EGRESS
  TYPE = HOST_PORT
  VALUE_LIST = ('drive.google.com:443', 'www.googleapis.com:443',
  'oauth2.googleapis.com:443', 'www.googleapis.com:443');

--ATTENTION!!! When you create/replace the EAI (this counts as a drop and recreate) - Grants are lost!

CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION OPENFLOW_EAI  
  ALLOWED_NETWORK_RULES = ( OPENFLOW.OPENFLOW.pg_rule,  
                            OPENFLOW.OPENFLOW.json_rule,  
                            OPENFLOW.OPENFLOW.goog_rule )  
   ENABLED = TRUE;

GRANT USAGE ON INTEGRATION OPENFLOW_EAI TO ROLE OPENFLOW_RUNTIME;  
GRANT USAGE ON INTEGRATION OPENFLOW_EAI TO ROLE OPENFLOW_ADMIN;
```
