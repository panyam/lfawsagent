import boto3, os
from ipdb import set_trace

debug = lambda: set_trace(context=21)

TOOLS = [
    {
        "name": "fetch_ec2_instances",
        "description": "Fetches details of EC2 instances in a specific AWS region.",
        "parameters": {
            "region": "The AWS region to query (e.g., us-east-1).",
            "state": "Optional. Filter instances by state (e.g., running, stopped)."
        }
    },
    {
        "name": "fetch_s3_buckets",
        "description": "Fetches the list of S3 buckets in the account.",
        "parameters": {}
    },
    {
        "name": "fetch_rds_instances",
        "description": "Fetches details of RDS instances in a specific AWS region.",
        "parameters": {
            "region": "The AWS region to query (e.g., us-east-1)."
        }
    },
    {
        "name": "fetch_elastic_ips",
        "description": "Fetches details of Elastic IPs in a specific AWS region.",
        "parameters": {
            "region": "The AWS region to query (e.g., us-east-1)."
        }
    },
    {
        "name": "fetch_security_groups",
        "description": "Fetches details of Security Groups in a specific AWS region.",
        "parameters": {
            "region": "The AWS region to query (e.g., us-east-1)."
        }
    },
    {
        "name": "fetch_elbs",
        "description": "Fetches details of Elastic Load Balancers in a specific AWS region.",
        "parameters": {
            "region": "The AWS region to query (e.g., us-east-1)."
        }
    },
    {
        "name": "fetch_key_pairs",
        "description": "Fetches details of Key Pairs in a specific AWS region.",
        "parameters": {
            "region": "The AWS region to query (e.g., us-east-1)."
        }
    }
]

def call_tool(tool_name, parameters):
    """Call the appropriate tool with the given parameters."""
    if tool_name == "fetch_ec2_instances":
        return fetch_ec2_instances(parameters.get("region"), parameters.get("state"))
    elif tool_name == "fetch_s3_buckets":
        return fetch_s3_buckets()
    elif tool_name == "fetch_rds_instances":
        return fetch_rds_instances(parameters.get("region"))
    elif tool_name == "fetch_elastic_ips":
        return fetch_elastic_ips(parameters.get("region"))
    elif tool_name == "fetch_security_groups":
        return fetch_security_groups(parameters.get("region"))
    elif tool_name == "fetch_elbs":
        return fetch_elbs(parameters.get("region"))
    elif tool_name == "fetch_key_pairs":
        return fetch_key_pairs(parameters.get("region"))
    else:
        raise ValueError(f"Unknown tool: {tool_name}")

def fetch_ec2_instances(region, state=None):
    """Fetch EC2 instances based on region and state filter."""
    ec2 = boto3.client('ec2', region_name=region)
    response = ec2.describe_instances()
    instances = [
        {
            "InstanceId": instance["InstanceId"],
            "State": instance["State"]["Name"],
            "Type": instance["InstanceType"]
        }
        for reservation in response["Reservations"]
        for instance in reservation["Instances"]
        if state is None or instance["State"]["Name"] == state
    ]
    return instances

def fetch_rds_instances(region):
    """Fetch details of RDS instances in a specific AWS region."""
    rds = boto3.client('rds', region_name=region)
    response = rds.describe_db_instances()
    instances = [
        {
            "DBInstanceIdentifier": db["DBInstanceIdentifier"],
            "Engine": db["Engine"],
            "Status": db["DBInstanceStatus"],
            "Region": region
        }
        for db in response.get("DBInstances", [])
    ]
    return instances

def fetch_s3_buckets():
    """Fetch the list of S3 buckets in the account."""
    s3 = boto3.client('s3')
    response = s3.list_buckets()
    buckets = [
        {
            "Name": bucket["Name"],
            "CreationDate": bucket["CreationDate"].strftime("%Y-%m-%d %H:%M:%S")
        }
        for bucket in response.get("Buckets", [])
    ]
    return buckets

def fetch_key_pairs(region):
    """Fetch details of Key Pairs in a specific AWS region."""
    ec2 = boto3.client('ec2', region_name=region)
    response = ec2.describe_key_pairs()
    key_pairs = [
        {
            "KeyName": kp["KeyName"],
            "KeyFingerprint": kp["KeyFingerprint"]
        }
        for kp in response.get("KeyPairs", [])
    ]
    return key_pairs

def fetch_elbs(region):
    """Fetch details of Elastic Load Balancers in a specific AWS region."""
    elb = boto3.client('elb', region_name=region)
    response = elb.describe_load_balancers()
    load_balancers = [
        {
            "LoadBalancerName": lb["LoadBalancerName"],
            "DNSName": lb["DNSName"],
            "CreatedTime": lb["CreatedTime"].strftime("%Y-%m-%d %H:%M:%S"),
            "Instances": len(lb.get("Instances", []))
        }
        for lb in response.get("LoadBalancerDescriptions", [])
    ]
    return load_balancers

def fetch_security_groups(region):
    """Fetch details of Security Groups in a specific AWS region."""
    ec2 = boto3.client('ec2', region_name=region)
    response = ec2.describe_security_groups()
    security_groups = [
        {
            "GroupName": sg["GroupName"],
            "GroupId": sg["GroupId"],
            "Description": sg["Description"],
            "Rules": len(sg.get("IpPermissions", []))
        }
        for sg in response.get("SecurityGroups", [])
    ]
    return security_groups

def fetch_elastic_ips(region):
    """Fetch details of Elastic IPs in a specific AWS region."""
    ec2 = boto3.client('ec2', region_name=region)
    response = ec2.describe_addresses()
    elastic_ips = [
        {
            "PublicIp": address["PublicIp"],
            "InstanceId": address.get("InstanceId", "Not Associated"),
            "AllocationId": address["AllocationId"]
        }
        for address in response.get("Addresses", [])
    ]
    return elastic_ips

#### Auto gen

def list_available_services():
    """Retrieve the list of available AWS services from boto3."""
    session = boto3.Session()
    return session.get_available_services()

def generate_tool_definitions():
    """Generate tool definitions for all supported AWS services and their key operations."""
    print("Generating tool definitions...")
    session = boto3.Session(region_name=os.environ.get("AWS_REGION"))
    def get_method_name(client, operation):
        method_name = [k for k,v in client.meta.method_to_api_mapping.items() if v == operation]
        if method_name: method_name = method_name[0]
        return method_name

    tool_definitions = []
    for service in session.get_available_services():
        try:
            client = session.client(service)
            operations = client.meta.service_model.operation_names
            for operation in operations:
                method_name = get_method_name(client, operation)
                if not method_name: continue
                opmodel = client.meta.service_model.operation_model(operation)
                shape = opmodel.input_shape
                if not shape: continue

                tool_definitions.append({
                    "name": f"{service}_{method_name}",
                    "description": opmodel.documentation,
                    "parameters": shape.members
                })
        except Exception as e:
            print(f"Could not load operations for {service}: {e}")
    return tool_definitions


def call_tool_dyn(tool_name, parameters):
    """Dynamically call a boto3 service operation based on the tool name and parameters."""
    try:
        # Extract the service and operation from the tool name
        service_name, operation_name = tool_name.split("_", 1)

        # Initialize the boto3 client for the service
        client = boto3.client(service_name, region_name=os.environ.get("AWS_REGION"))

        # Call the operation dynamically
        operation = getattr(client, operation_name)
        response = operation(**parameters)
        return response
    except Exception as e:
        raise ValueError(f"Error executing tool '{tool_name}': {str(e)}")
