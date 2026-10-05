# Lab 00 - Initial Setup

Set up Snowflake roles, permissions and an Openflow SPCS deployment and runtime

**Cheat Sheet:**  
[https://github.com/sfc-gh-aseaton/openflow/blob/main/SPCS%20Setup.sql](https://github.com/sfc-gh-aseaton/openflow/blob/main/SPCS%20Setup.sql)

**Official Docs:**  
[https://docs.snowflake.com/en/user-guide/data-integration/openflow/setup-openflow-spcs](https://docs.snowflake.com/en/user-guide/data-integration/openflow/setup-openflow-spcs)

**Snowsight UI Steps - Create Deployment and Runtime:**

![](images/img1.png)

![](images/img2.png)

![](images/img3.png)

![](images/img4.png)

![](images/img5.png)

**Networking:**

The cheat sheet gives some examples of network rules that allow outbound connectivity from Snowflake SPCS to data sources (SPCS egress is blocked by default). For the labs you need to create these rules:

```sql
CREATE OR REPLACE NETWORK RULE OPENFLOW.OPENFLOW.pg_rule
  MODE = EGRESS
  TYPE = HOST_PORT
  VALUE_LIST = ('2mo2z2j54na6fni3735enmtiti.sfseeurope-aseaton.us-west-2.aws.postgres.snowflake.app:5432');

CREATE OR REPLACE NETWORK RULE OPENFLOW.OPENFLOW.json_rule
  MODE = EGRESS
  TYPE = HOST_PORT
  VALUE_LIST = ('dummyjson.com:443');

CREATE OR REPLACE NETWORK RULE OPENFLOW.OPENFLOW.goog_rule
  MODE = EGRESS
  TYPE = HOST_PORT
  VALUE_LIST = ('drive.google.com:443', 'www.googleapis.com:443',
                'oauth2.googleapis.com:443');

-- ATTENTION!!! Creating/replacing the EAI counts as a drop and recreate - existing grants are lost!

CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION OPENFLOW_EAI
  ALLOWED_NETWORK_RULES = ( OPENFLOW.OPENFLOW.pg_rule,
                            OPENFLOW.OPENFLOW.json_rule,
                            OPENFLOW.OPENFLOW.goog_rule )
  ENABLED = TRUE;

GRANT USAGE ON INTEGRATION OPENFLOW_EAI TO ROLE OPENFLOW_RUNTIME;
GRANT USAGE ON INTEGRATION OPENFLOW_EAI TO ROLE OPENFLOW_ADMIN;
```

> 💡 Make sure `OPENFLOW_EAI` is selected under **External access integrations** on your runtime. If you created the runtime before running the SQL above, add it from the runtime's 3 dot context menu.
