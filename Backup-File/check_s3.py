import boto3
import os

cf_client = boto3.client('cloudformation', 
                         region_name='us-east-1',
                         aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                         aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))

s3_client = boto3.client('s3',
                        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))

stack_name = 's3-stack-1768721967356'

print("\n🔍 CLOUDFORMATION STACK RESOURCES:")
print("=" * 80)
try:
    resources = cf_client.describe_stack_resources(StackName=stack_name)
    for resource in resources['StackResources']:
        print(f"Type: {resource['ResourceType']}")
        print(f"Logical ID: {resource['LogicalResourceId']}")
        print(f"Physical ID: {resource.get('PhysicalResourceId', 'N/A')}")
        print(f"Status: {resource['ResourceStatus']}")
        print("-" * 80)
except Exception as e:
    print(f"Error getting stack resources: {e}")

print("\n🗄️ ALL S3 BUCKETS IN YOUR ACCOUNT:")
print("=" * 80)
try:
    buckets = s3_client.list_buckets()
    if buckets['Buckets']:
        for bucket in buckets['Buckets']:
            print(f"Bucket: {bucket['Name']}")
            print(f"Created: {bucket['CreationDate']}")
            try:
                location = s3_client.get_bucket_location(Bucket=bucket['Name'])
                region = location['LocationConstraint'] or 'us-east-1'
                print(f"Region: {region}")
            except:
                print(f"Region: Unable to determine")
            print("-" * 80)
    else:
        print("No buckets found!")
except Exception as e:
    print(f"Error listing buckets: {e}")

print("\n📋 CLOUDFORMATION STACK OUTPUTS:")
print("=" * 80)
try:
    stack_info = cf_client.describe_stacks(StackName=stack_name)
    if 'Outputs' in stack_info['Stacks'][0]:
        for output in stack_info['Stacks'][0]['Outputs']:
            print(f"{output['OutputKey']}: {output['OutputValue']}")
    else:
        print("No outputs defined")
except Exception as e:
    print(f"Error getting stack outputs: {e}")
