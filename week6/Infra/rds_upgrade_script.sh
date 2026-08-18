# pipeline.sh

# 1. Terraform: disable autoscaling + maintenance mode
terraform apply -var="ecs_desired_count=0" -var="autoscaling_min=0"

# 2. CLI: manual snapshot (can't do this well in Terraform)
aws rds create-db-snapshot \
  --db-instance-identifier student-app-db \
  --db-snapshot-identifier pre-upgrade-$(date +%Y%m%d)

# 3. CLI: wait for snapshot
aws rds wait db-snapshot-available \
  --db-snapshot-identifier pre-upgrade-$(date +%Y%m%d)

# 4. Terraform: apply the upgrade
terraform apply -var="db_engine_version=17"

# 5. CLI: wait for DB to be available
aws rds wait db-instance-available \
  --db-instance-identifier student-app-db

# 6. CLI: run smoke tests
psql -h $DB_HOST -U myuser -d mydb -c "SELECT version();"

# 7. Terraform: restore capacity
terraform apply -var="ecs_desired_count=1" -var="autoscaling_min=2"