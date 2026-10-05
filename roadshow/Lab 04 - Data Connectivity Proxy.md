# Lab 04 - Data Connectivity Proxy

Recently GA'd it's now possible for Openflow to connect to data sources on-premise or other locations hidden behind a firewall. The DCP is a local containerized agent which makes an outbound connection to Snowflake, creating a tunnel to allow inbound connections. For full information, check the [official documentation](https://docs.snowflake.com/en/user-guide/data-connectivity-proxy)

First we must setup the network rules which allow DNS mapping from Openflow SPCS to the Proxy

```
-- DCP Network Rule uses new network rule type: DATA_CONNECTIVITY_PROXY_EGRESS

use role accountadmin;
CREATE OR REPLACE NETWORK RULE localport
  MODE = DATA_CONNECTIVITY_PROXY_EGRESS
  TYPE = HOST_PORT
  VALUE_LIST = ('my.internal:8080');    -- map the DNS my.internal to the proxy

DESC NETWORK RULE localport;

-- Package network rule in an EAI and grant USAGE
CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION DCP_EAI
  ALLOWED_NETWORK_RULES = (localport)
  ENABLED = TRUE;

GRANT USAGE ON INTEGRATION DCP_EAI TO ROLE openflow_admin;
GRANT USAGE ON INTEGRATION DCP_EAI TO ROLE openflow_runtime;
```

Now we need to create the DCP proxy object in Snowflake

```
CREATE DATA CONNECTIVITY PROXY IF NOT EXISTS MY_DCP
  EXTERNAL_ACCESS_INTEGRATIONS = (DCP_EAI)
  ENABLED = TRUE;

SHOW DATA CONNECTIVITY PROXIES; -- check creation
```

Initial connectivity is handled via a JWT token - We must create one using the following SQL. We will specify a 90 day validity, copy the output and save to a local file

```
SELECT SYSTEM$GENERATE_DATA_CONNECTIVITY_PROXY_BOOTSTRAP_TOKEN('MY_DCP', 90);
```

# Container Setup

The DCP works as a container which must be run using OCI compliant software such as [Docker](https://www.docker.com/) or [Podman](https://podman.io/). The image is hosted on [dockerhub](https://hub.docker.com/r/snowflakedb/dcp-client)

Update the command below for your container software of choice and make sure to point to the local JWT token file (in this example)

```
docker run --rm -it \
 --name snowflake-dcp-agent \
 --add-host my.internal:host-gateway \
 -v /Users/me/dcp-bootstrap-token:/etc/dcp-agent/secrets/dcp-bootstrap-token:ro \
 -e DCP_METRICS_PORT=9092 \
 -p 9092:9092 \
 snowflakedb/dcp-client:latest
```

Once the agent has started without obvious errors in the output - view the [Prometheus metrics page](http://localhost:9092/metrics) and look for the agent connectivity status line `agent_cp_connected 1`

For this lab we will use a python script to act as a mock HTTP endpoint running on our local machine. Download the [mock_endpoint.py](mock_endpoint.py) script and run it on your machine. It will listen on port 8080 and echo any HTTP requests

Build a simple flow using an InvokeHTTP processor as we did in Lab 02 and route the **Response** relationship so we can view the results

![](images/img22.png)

> Configure the get to use this endpoint:
`http://my.internal:8080/this/is/a/test`

Openflow SPCS captures the DNS request for hostname and port `my.internal:8080` and routes it via DCP as per the network rule we configured above. Execute the HTTP request using **Run once** and observe the connection in the DCP output trace and the mock endpoint output. 

🥳 Congratulations! 🥳 You have connected Openflow running in Snowflake to a local endpoint running on your machine