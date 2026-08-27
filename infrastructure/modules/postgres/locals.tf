locals {
  # RDS
  # /teams
  rds_postgres_teams_schemas             = { for v in var.rds_postgres_teams : v => v }
  rds_postgres_teams_usernames           = { for v in var.rds_postgres_teams : v => "${v}-0123456789" }
  rds_postgres_teams_passwords           = { for v in var.rds_postgres_teams : v => "${v}-0123456789" }
  rds_postgres_teams_migration_usernames = { for v in var.rds_postgres_teams : v => "${v}-migration-0123456789" }
  rds_postgres_teams_migration_passwords = { for v in var.rds_postgres_teams : v => "${v}-migration-0123456789" }
}