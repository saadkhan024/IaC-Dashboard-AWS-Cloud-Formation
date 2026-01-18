from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import boto3
import json
import uuid
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Fix: Properly read DEMO_MODE environment variable
demo_mode_env = os.getenv('DEMO_MODE', 'True')
DEMO_MODE = demo_mode_env.lower() in ['true', '1', 'yes', 't']

print("=" * 60)
print(f"DEMO_MODE environment variable: {demo_mode_env}")
print(f"Running in: {'DEMO MODE' if DEMO_MODE else 'PRODUCTION MODE'}")
print(f"AWS_ACCESS_KEY_ID present: {bool(os.getenv('AWS_ACCESS_KEY_ID'))}")
print("=" * 60)

# In-memory storage for demo mode
stacks_db = []
logs_db = []

# CloudFormation Templates - AWS AUTO-GENERATES UNIQUE NAMES
TEMPLATES = {
    'ec2': {
        'AWSTemplateFormatVersion': '2010-09-09',
        'Description': 'EC2 Instance - Free Tier Eligible',
        'Mappings': {
            'RegionMap': {
                'us-east-1': {'AMI': 'ami-0453ec754f44f9a4a'},
                'us-east-2': {'AMI': 'ami-0490fddec0cbeb88b'},
                'us-west-1': {'AMI': 'ami-0da424eb883458071'},
                'us-west-2': {'AMI': 'ami-0688ba7eeeeefe3cd'},
                'eu-west-1': {'AMI': 'ami-0d71ea30463e0ff8d'},
                'ap-south-1': {'AMI': 'ami-0f58b397bc5c1f2e8'}
            }
        },
        'Resources': {
            'InstanceSecurityGroup': {
                'Type': 'AWS::EC2::SecurityGroup',
                'Properties': {
                    'GroupDescription': 'Enable SSH and HTTP',
                    'SecurityGroupIngress': [
                        {
                            'IpProtocol': 'tcp',
                            'FromPort': 22,
                            'ToPort': 22,
                            'CidrIp': '0.0.0.0/0'
                        },
                        {
                            'IpProtocol': 'tcp',
                            'FromPort': 80,
                            'ToPort': 80,
                            'CidrIp': '0.0.0.0/0'
                        }
                    ],
                    'Tags': [
                        {'Key': 'Name', 'Value': 'IaC-Dashboard-SG'},
                        {'Key': 'ManagedBy', 'Value': 'IaC-Dashboard'}
                    ]
                }
            },
            'MyEC2Instance': {
                'Type': 'AWS::EC2::Instance',
                'Properties': {
                    'ImageId': {'Fn::FindInMap': ['RegionMap', {'Ref': 'AWS::Region'}, 'AMI']},
                    'InstanceType': 't3.micro',
                    'SecurityGroups': [{'Ref': 'InstanceSecurityGroup'}],
                    'Tags': [
                        {'Key': 'Name', 'Value': 'IaC-Dashboard-Instance'},
                        {'Key': 'ManagedBy', 'Value': 'IaC-Dashboard'}
                    ]
                }
            }
        },
        'Outputs': {
            'InstanceId': {
                'Description': 'EC2 Instance ID',
                'Value': {'Ref': 'MyEC2Instance'}
            },
            'PublicIP': {
                'Description': 'Public IP Address',
                'Value': {'Fn::GetAtt': ['MyEC2Instance', 'PublicIp']}
            },
            'AvailabilityZone': {
                'Description': 'Availability Zone',
                'Value': {'Fn::GetAtt': ['MyEC2Instance', 'AvailabilityZone']}
            }
        }
    },
    's3': {
        'AWSTemplateFormatVersion': '2010-09-09',
        'Description': 'S3 Bucket with Versioning - AWS auto-generates unique name',
        'Resources': {
            'MyS3Bucket': {
                'Type': 'AWS::S3::Bucket',
                'Properties': {
                    'VersioningConfiguration': {
                        'Status': 'Enabled'
                    },
                    'PublicAccessBlockConfiguration': {
                        'BlockPublicAcls': True,
                        'BlockPublicPolicy': True,
                        'IgnorePublicAcls': True,
                        'RestrictPublicBuckets': True
                    },
                    'Tags': [
                        {'Key': 'ManagedBy', 'Value': 'IaC-Dashboard'},
                        {'Key': 'Name', 'Value': 'IaC-Dashboard-Bucket'}
                    ]
                }
            }
        },
        'Outputs': {
            'BucketName': {
                'Description': 'S3 Bucket Name (AWS Auto-generated)',
                'Value': {'Ref': 'MyS3Bucket'}
            },
            'BucketArn': {
                'Description': 'S3 Bucket ARN',
                'Value': {'Fn::GetAtt': ['MyS3Bucket', 'Arn']}
            }
        }
    },
    'lambda': {
        'AWSTemplateFormatVersion': '2010-09-09',
        'Description': 'Lambda Function with Execution Role - AWS auto-generates unique names',
        'Resources': {
            'LambdaExecutionRole': {
                'Type': 'AWS::IAM::Role',
                'Properties': {
                    'AssumeRolePolicyDocument': {
                        'Version': '2012-10-17',
                        'Statement': [
                            {
                                'Effect': 'Allow',
                                'Principal': {
                                    'Service': 'lambda.amazonaws.com'
                                },
                                'Action': 'sts:AssumeRole'
                            }
                        ]
                    },
                    'ManagedPolicyArns': [
                        'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
                    ],
                    'Tags': [
                        {'Key': 'ManagedBy', 'Value': 'IaC-Dashboard'}
                    ]
                }
            },
            'MyLambdaFunction': {
                'Type': 'AWS::Lambda::Function',
                'DependsOn': 'LambdaExecutionRole',
                'Properties': {
                    'Runtime': 'python3.12',
                    'Handler': 'index.lambda_handler',
                    'Role': {'Fn::GetAtt': ['LambdaExecutionRole', 'Arn']},
                    'Code': {
                        'ZipFile': 'def lambda_handler(event, context):\n    return {\n        "statusCode": 200,\n        "body": "Hello from IaC Dashboard!"\n    }'
                    },
                    'Timeout': 30,
                    'MemorySize': 128,
                    'Tags': [
                        {'Key': 'ManagedBy', 'Value': 'IaC-Dashboard'}
                    ]
                }
            }
        },
        'Outputs': {
            'FunctionArn': {
                'Description': 'Lambda Function ARN',
                'Value': {'Fn::GetAtt': ['MyLambdaFunction', 'Arn']}
            },
            'FunctionName': {
                'Description': 'Lambda Function Name (AWS Auto-generated)',
                'Value': {'Ref': 'MyLambdaFunction'}
            },
            'RoleArn': {
                'Description': 'Lambda Execution Role ARN',
                'Value': {'Fn::GetAtt': ['LambdaExecutionRole', 'Arn']}
            }
        }
    },
    'rds': {
        'AWSTemplateFormatVersion': '2010-09-09',
        'Description': 'RDS MySQL Database Instance - AWS auto-generates unique name',
        'Resources': {
            'DBSecurityGroup': {
                'Type': 'AWS::EC2::SecurityGroup',
                'Properties': {
                    'GroupDescription': 'Security group for RDS instance',
                    'SecurityGroupIngress': [
                        {
                            'IpProtocol': 'tcp',
                            'FromPort': 3306,
                            'ToPort': 3306,
                            'CidrIp': '0.0.0.0/0'
                        }
                    ],
                    'Tags': [
                        {'Key': 'Name', 'Value': 'IaC-Dashboard-RDS-SG'},
                        {'Key': 'ManagedBy', 'Value': 'IaC-Dashboard'}
                    ]
                }
            },
            'MyRDSInstance': {
                'Type': 'AWS::RDS::DBInstance',
                'Properties': {
                    'Engine': 'mysql',
                    'EngineVersion': '8.0.35',
                    'DBInstanceClass': 'db.t3.micro',
                    'AllocatedStorage': '20',
                    'StorageType': 'gp2',
                    'MasterUsername': 'admin',
                    'MasterUserPassword': 'AdminPassword123!',
                    'VPCSecurityGroups': [{'Fn::GetAtt': ['DBSecurityGroup', 'GroupId']}],
                    'PubliclyAccessible': False,
                    'BackupRetentionPeriod': 0,
                    'Tags': [
                        {'Key': 'ManagedBy', 'Value': 'IaC-Dashboard'}
                    ]
                }
            }
        },
        'Outputs': {
            'DBInstanceIdentifier': {
                'Description': 'Database Instance Identifier (AWS Auto-generated)',
                'Value': {'Ref': 'MyRDSInstance'}
            },
            'DBEndpoint': {
                'Description': 'Database Endpoint',
                'Value': {'Fn::GetAtt': ['MyRDSInstance', 'Endpoint.Address']}
            },
            'DBPort': {
                'Description': 'Database Port',
                'Value': {'Fn::GetAtt': ['MyRDSInstance', 'Endpoint.Port']}
            }
        }
    }
}

class CloudFormationManager:
    def __init__(self, demo_mode=True):
        self.demo_mode = demo_mode
        if not demo_mode:
            try:
                self.client = boto3.client('cloudformation', region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'))
                print("✅ AWS CloudFormation client initialized")
            except Exception as e:
                print(f"❌ Failed to initialize AWS client: {e}")
                self.demo_mode = True

    def create_stack(self, stack_name, service_type):
        if service_type not in TEMPLATES:
            return {'error': f'Unknown service type: {service_type}'}, 400

        template = TEMPLATES[service_type]

        if self.demo_mode:
            stack = {
                'StackId': f'arn:aws:cloudformation:us-east-1:123456789012:stack/{stack_name}/{uuid.uuid4()}',
                'StackName': stack_name,
                'Status': 'CREATE_COMPLETE',
                'ServiceType': service_type.upper(),
                'CreationTime': datetime.now().isoformat(),
                'Region': 'us-east-1',
                'Template': template
            }
            stacks_db.append(stack)
            logs_db.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'success',
                'message': f'Stack "{stack_name}" created (DEMO MODE - not real)'
            })
            return {'stack': stack, 'message': 'Stack created (Demo Mode)'}, 200
        else:
            try:
                print(f"🚀 Creating REAL CloudFormation stack: {stack_name}")
                response = self.client.create_stack(
                    StackName=stack_name,
                    TemplateBody=json.dumps(template),
                    Capabilities=['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM']
                )
                print(f"✅ Stack created: {response['StackId']}")

                # Add to logs for production mode too
                logs_db.append({
                    'timestamp': datetime.now().isoformat(),
                    'type': 'success',
                    'message': f'Stack "{stack_name}" created successfully in AWS'
                })

                return {'stack_id': response['StackId'], 'message': 'Real stack creation initiated!'}, 200
            except Exception as e:
                print(f"❌ Error creating stack: {e}")
                logs_db.append({
                    'timestamp': datetime.now().isoformat(),
                    'type': 'error',
                    'message': f'Failed to create stack "{stack_name}": {str(e)}'
                })
                return {'error': str(e)}, 500

    def delete_stack(self, stack_name):
        """Delete a CloudFormation stack"""
        if self.demo_mode:
            for i, stack in enumerate(stacks_db):
                if stack['StackName'] == stack_name:
                    stacks_db.pop(i)
                    logs_db.append({
                        'timestamp': datetime.now().isoformat(),
                        'type': 'warning',
                        'message': f'Stack "{stack_name}" deleted (DEMO MODE)'
                    })
                    return {'message': 'Stack deleted (Demo Mode)'}, 200
            return {'error': 'Stack not found'}, 404
        else:
            try:
                print(f"🗑️ Deleting REAL CloudFormation stack: {stack_name}")
                self.client.delete_stack(StackName=stack_name)
                logs_db.append({
                    'timestamp': datetime.now().isoformat(),
                    'type': 'warning',
                    'message': f'Stack "{stack_name}" deletion initiated'
                })
                return {'message': 'Stack deletion initiated'}, 200
            except Exception as e:
                print(f"❌ Error deleting stack: {e}")
                return {'error': str(e)}, 500

    def list_stacks(self):
        if self.demo_mode:
            return {'stacks': stacks_db}, 200
        else:
            try:
                response = self.client.list_stacks(
                    StackStatusFilter=['CREATE_COMPLETE', 'UPDATE_COMPLETE', 'CREATE_IN_PROGRESS']
                )
                return {'stacks': response['StackSummaries']}, 200
            except Exception as e:
                return {'error': str(e)}, 500

# Initialize manager
cfn_manager = CloudFormationManager(demo_mode=DEMO_MODE)

@app.route('/')
def index():
    try:
        return send_file('static/index.html')
    except:
        return "Dashboard not found", 404

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'demo_mode': DEMO_MODE,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/stacks', methods=['GET'])
def list_stacks():
    result, status = cfn_manager.list_stacks()
    return jsonify(result), status

@app.route('/api/stacks/create', methods=['POST'])
def create_stack():
    data = request.json
    stack_name = data.get('stackName', f'stack-{uuid.uuid4().hex[:8]}')
    service_type = data.get('serviceType', 'ec2').lower()
    result, status = cfn_manager.create_stack(stack_name, service_type)
    return jsonify(result), status

@app.route('/api/stacks/delete/<stack_name>', methods=['DELETE'])
def delete_stack(stack_name):
    """Delete a stack"""
    result, status = cfn_manager.delete_stack(stack_name)
    return jsonify(result), status

@app.route('/api/logs', methods=['GET'])
def get_logs():
    return jsonify({'logs': logs_db[-20:]})

@app.route('/api/costs', methods=['GET'])
def get_costs():
    """Get cost analysis"""
    if DEMO_MODE:
        num_stacks = len(stacks_db)
    else:
        # Count real stacks
        result, _ = cfn_manager.list_stacks()
        num_stacks = len(result.get('stacks', []))

    current_cost = num_stacks * 12.50
    projected_cost = current_cost * 1.8
    budget = 500.0

    return jsonify({
        'current': round(current_cost, 2),
        'projected': round(projected_cost, 2),
        'budget': budget,
        'remaining': round(budget - current_cost, 2)
    })

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get infrastructure metrics - FIXED to work in production mode"""
    counts = {'ec2': 0, 's3': 0, 'lambda': 0, 'rds': 0}

    if DEMO_MODE:
        # Demo mode - count from in-memory database
        for stack in stacks_db:
            stype = stack.get('ServiceType', 'EC2').lower()
            if stype in counts:
                counts[stype] += 1
    else:
        # Production mode - count from real CloudFormation stacks
        try:
            result, _ = cfn_manager.list_stacks()
            stacks = result.get('stacks', [])

            print(f"📊 Counting metrics from {len(stacks)} CloudFormation stacks")

            for stack in stacks:
                stack_name = stack.get('StackName', '').lower()

                # Determine service type from stack name
                if 'ec2' in stack_name or 'instance' in stack_name:
                    counts['ec2'] += 1
                    print(f"  ✅ EC2 stack found: {stack.get('StackName')}")
                elif 's3' in stack_name or 'bucket' in stack_name:
                    counts['s3'] += 1
                    print(f"  ✅ S3 stack found: {stack.get('StackName')}")
                elif 'lambda' in stack_name or 'function' in stack_name:
                    counts['lambda'] += 1
                    print(f"  ✅ Lambda stack found: {stack.get('StackName')}")
                elif 'rds' in stack_name or 'database' in stack_name or 'db' in stack_name:
                    counts['rds'] += 1
                    print(f"  ✅ RDS stack found: {stack.get('StackName')}")

            print(f"📊 Final counts: {counts}")

        except Exception as e:
            print(f"❌ Error getting metrics: {e}")

    return jsonify(counts)

if __name__ == '__main__':
    if DEMO_MODE:
        print("🎮 Running in DEMO MODE - No real AWS resources will be created")
        # Add demo data
        cfn_manager.create_stack('demo-web-stack', 'ec2')
        cfn_manager.create_stack('demo-storage-stack', 's3')
    else:
        print("🚀 Running in PRODUCTION MODE - Real AWS resources will be created!")

    app.run(host='0.0.0.0', port=5000, debug=True)
