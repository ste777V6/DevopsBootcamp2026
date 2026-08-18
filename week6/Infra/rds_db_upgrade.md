# RDS_DB Upgrade process :

PRE-UPGRADE
□ Check version compatibility
□ Test on staging with production snapshot
□ Measure upgrade duration on staging
□ Schedule maintenance window
□ Notify stakeholders

DAY OF
□ Take manual RDS snapshot
□ Disable auto scaling
□ Scale ECS to 0 (maintenance mode)
□ Apply upgrade
□ Monitor until "available"

POST-UPGRADE
□ Verify engine version
□ Run smoke tests
□ Bring up 1 task, validate
□ Restore full capacity + auto scaling
□ Remove maintenance page
□ Monitor 24-48h

ROLLBACK (if needed)
□ Restore pre-upgrade snapshot
□ Update app endpoint
□ Redeploy



TEST -  Shell scrip to run # rds_upgrade_script.sh (not for production use)

PROD -  Github action pipeline specific for rds upgrade -.github/workflows/rds-upgrade.yml
