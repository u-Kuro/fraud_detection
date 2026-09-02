# Create Postgres in RDS
resource "aws_db_instance" "postgres" {
  identifier            = "rds"
  engine                = "postgres"
  instance_class        = "db.t3.micro"
  allocated_storage     = 20
  max_allocated_storage = 20
  engine_version        = "15" # Fixed to alpine, can only use major version in MiniStack
  username              = var.rds_postgres_admin_username
  password              = var.rds_postgres_admin_password
  db_name               = "main"
  skip_final_snapshot   = true
}
# Allow snapshots/backup in RDS
resource "aws_iam_role_policy" "rds" {
  role = var.iam_rds_role_name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "s3:*"
        Resource = [
          var.s3_postgres_bucket_arn,
          "${var.s3_postgres_bucket_arn}/*"
        ]
      }
    ]
  })

  depends_on = [
    aws_db_instance.postgres # Waits until postgres is fully functional
  ]
}
# Get MiniStack's Postgres container configurations
data "external" "postgres_configuration" {
  program = ["powershell", "-File", "${path.module}/scripts/get-postgres-configurations.ps1"]

  query = {
    main_network_name     = var.main_network_name
    postgres_container_ip = aws_db_instance.postgres.address
  }

  depends_on = [aws_db_instance.postgres]
}
# {
#    "DBInstance": {
#        "DBInstanceIdentifier": "test",
#        "DBInstanceClass": "db.t3.micro",
#        "Engine": "postgres",
#        "DBInstanceStatus": "creating",
#        "MasterUsername": "admin",
#        "DBName": "mydb",
#        "Endpoint": {
#            "Address": "172.19.0.4",
#            "Port": 5432,
#            "HostedZoneId": "Z2R2ITUGPM61AM"
#        },
#        "AllocatedStorage": 20,
#        "InstanceCreateTime": "2026-08-19T07:13:12.850000+00:00",
#        "PreferredBackupWindow": "03:00-04:00",
#        "BackupRetentionPeriod": 1,
#        "DBSecurityGroups": [],
#        "VpcSecurityGroups": [],
#        "DBParameterGroups": [
#            {
#                "DBParameterGroupName": "default.postgres15",
#                "ParameterApplyStatus": "in-sync"
#            }
#        ],
#        "AvailabilityZone": "us-east-1a",
#        "DBSubnetGroup": {
#            "DBSubnetGroupName": "default",
#            "DBSubnetGroupDescription": "default",
#            "VpcId": "vpc-00000000",
#            "SubnetGroupStatus": "Complete",
#            "Subnets": [],
#            "DBSubnetGroupArn": "arn:aws:rds:us-east-1:000000000000:subgrp:default"
#        },
#        "PreferredMaintenanceWindow": "sun:05:00-sun:06:00",
#        "PendingModifiedValues": {},
#        "LatestRestorableTime": "2026-08-19T07:13:12.850000+00:00",
#        "MultiAZ": false,
#        "EngineVersion": "15.3",
#        "AutoMinorVersionUpgrade": true,
#        "ReadReplicaSourceDBInstanceIdentifier": "",
#        "ReadReplicaDBInstanceIdentifiers": [],
#        "ReadReplicaDBClusterIdentifiers": [],
#        "ReplicaMode": "",
#        "LicenseModel": "postgresql-license",
#        "StorageThroughput": 0,
#        "OptionGroupMemberships": [
#            {
#                "OptionGroupName": "default:postgres-15",
#                "Status": "in-sync"
#            }
#        ],
#        "PubliclyAccessible": false,
#        "StatusInfos": [],
#        "StorageType": "gp2",
#        "DbInstancePort": 0,
#        "DBClusterIdentifier": "",
#        "StorageEncrypted": false,
#        "KmsKeyId": "",
#        "DbiResourceId": "db-5CC414DD6715487EAD2F",
#        "CACertificateIdentifier": "rds-ca-rsa2048-g1",
#        "DomainMemberships": [],
#        "CopyTagsToSnapshot": false,
#        "MonitoringInterval": 0,
#        "EnhancedMonitoringResourceArn": "",
#        "MonitoringRoleArn": "",
#        "PromotionTier": 1,
#        "DBInstanceArn": "arn:aws:rds:us-east-1:000000000000:db:test",
#        "IAMDatabaseAuthenticationEnabled": false,
#        "PerformanceInsightsEnabled": false,
#        "EnabledCloudwatchLogsExports": [],
#        "ProcessorFeatures": [],
#        "DeletionProtection": false,
#        "AssociatedRoles": [],
#        "MaxAllocatedStorage": 20,
#        "TagList": [],
#        "CustomerOwnedIpEnabled": false,
#        "NetworkType": "IPV4",
#        "BackupTarget": "region",
#        "CertificateDetails": {
#            "CAIdentifier": "rds-ca-rsa2048-g1",
#            "ValidTill": "2061-01-01T00:00:00+00:00"
#        },
#        "IsStorageConfigUpgradeAvailable": false
#    }
#}