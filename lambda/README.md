# Automated Threat Response

This AWS Lambda function provides an automated response to **SSH brute-force attacks** detected by Amazon GuardDuty.

When GuardDuty generates a finding (`UnauthorizedAccess:EC2/SSHBruteForce`), an EventBridge rule triggers this function.

## Function Behavior

- Extracts the attacker's IP address from the GuardDuty finding.
- Dynamically creates a **Network ACL deny rule** to block port 22 (SSH) from that IP.
- Sends an alert via **Amazon SNS** with details of the attack.

## Requirements

To operate correctly, this function requires:

- **Amazon EventBridge** rule configured to trigger on GuardDuty findings.
- **Amazon SNS** topic to notify the security team by email.
- **A Network ACL (NACL)** associated with the target VPC to apply the deny rule.

> ⚠️ **Note:** Update the `nacl_id` and `SNS Topic ARN` in the script to match your environment.
