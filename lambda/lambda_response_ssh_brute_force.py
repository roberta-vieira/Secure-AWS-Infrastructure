import boto3                    # Library that allows communication with AWS Services

ec2 = boto3.client('ec2')       # Client so the code is able to communicate with EC2 instance
sns = boto3.client('sns')       # Client so the code is able to communicate with SNS

# Finds an available rule number on our Network ACL
def find_available_rule_number(nacl_id):
    response = ec2.describe_network_acls(NetworkAclIds=[nacl_id])
    existing_rules = set(
        entry['RuleNumber']
        for acl in response['NetworkAcls']
        for entry in acl['Entries']
    )
    for num in range(100, 32766):       # Skips low system-reserved rule numbers
        if num not in existing_rules:
            return num
    raise Exception("No available Network ACL rule numbers.") 

# Function that AWS runs automatically when the Lambda is triggered
def lambda_handler(event, context):

    # Save useful information from the Guard Duty finding
    finding = event['detail']
    type_of_attack = finding.get('type', 'Unknown')
    description = finding.get('description', 'No description')
    instance_id = finding.get('resource', {}).get('instanceDetails', {}).get('instanceId', 'N/A')

    # Extract threat actor's IP address from finding
    action = finding.get('service', {}).get('action', {})
    threat_ip = (
        action.get('networkConnectionAction', {}) or
        action.get('portProbeAction', {})
    ).get('remoteIpDetails', {}).get('ipAddressV4', 'Unknown')

    # Try to block IP address via Netwrok ACL
    try: 
        nacl_id = 'acl-0411cf3f66eabcb0d'
        rule_number = find_available_rule_number(nacl_id)

        ec2.create_network_acl_entry(
            NetworkAclId=nacl_id,
            RuleNumber=rule_number,
            Protocol='6',  # TCP
            RuleAction='deny',
            Egress=False,
            CidrBlock=f'{threat_ip}/32',
            PortRange={'From': 22, 'To': 22}
        )

        block_status = f'✅ IP address {threat_ip} successfully blocked on port 22 via NACL {nacl_id} (rule {rule_number}).'
    except Exception as e:
        block_status = f'❌ Failed to block IP address {threat_ip}: {str(e)}'


    # Create the message to send to SNS
    message = f"""🚨 GuardDuty Alert:
Type: {type_of_attack}
Resource: {finding.get('resource', {}).get('instanceDetails', {}).get('instanceId', 'N/A')}
Description: {description}
Instance ID: {instance_id}
Threat actor's IP address: {threat_ip}

{block_status}
    """

    sns.publish(
        TopicArn='arn:aws:sns:eu-west-3:027165077285:SecurityAlerts',
        Message=message,
        Subject='GuardDuty Alert - Potential Threat Detected'
    )
    
