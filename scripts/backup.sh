#!/bin/bash

# Grafana Backup Script
# This script backs up Grafana dashboards, data sources, and settings

set -e

BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_PATH="$BACKUP_DIR/grafana_backup_$TIMESTAMP"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔄 Grafana Backup Script${NC}"
echo "========================="

# Check if Grafana is running
check_grafana() {
    if ! curl -s http://localhost:3000/api/health > /dev/null; then
        echo -e "${RED}❌ Grafana is not accessible at http://localhost:3000${NC}"
        echo "Make sure Grafana is running with: ./scripts/setup.sh start"
        exit 1
    fi
    echo -e "${GREEN}✅ Grafana is running${NC}"
}

# Create backup directory
create_backup_dir() {
    mkdir -p "$BACKUP_PATH"
    echo -e "${GREEN}📁 Created backup directory: $BACKUP_PATH${NC}"
}

# Backup dashboards
backup_dashboards() {
    echo -e "${YELLOW}📊 Backing up dashboards...${NC}"
    
    # Get all dashboard UIDs
    DASHBOARD_UIDS=$(curl -s -H "Content-Type: application/json" \
        http://admin:admin@localhost:3000/api/search?type=dash-db | \
        jq -r '.[].uid')
    
    mkdir -p "$BACKUP_PATH/dashboards"
    
    for uid in $DASHBOARD_UIDS; do
        if [ "$uid" != "null" ] && [ -n "$uid" ]; then
            echo "  📋 Backing up dashboard: $uid"
            curl -s -H "Content-Type: application/json" \
                http://admin:admin@localhost:3000/api/dashboards/uid/$uid | \
                jq '.dashboard' > "$BACKUP_PATH/dashboards/$uid.json"
        fi
    done
    
    echo -e "${GREEN}✅ Dashboards backed up${NC}"
}

# Backup data sources
backup_datasources() {
    echo -e "${YELLOW}🔌 Backing up data sources...${NC}"
    
    mkdir -p "$BACKUP_PATH/datasources"
    
    curl -s -H "Content-Type: application/json" \
        http://admin:admin@localhost:3000/api/datasources | \
        jq '.' > "$BACKUP_PATH/datasources/datasources.json"
    
    echo -e "${GREEN}✅ Data sources backed up${NC}"
}

# Backup alert rules (if any)
backup_alerts() {
    echo -e "${YELLOW}🚨 Backing up alert rules...${NC}"
    
    mkdir -p "$BACKUP_PATH/alerts"
    
    # Get legacy alert rules
    curl -s -H "Content-Type: application/json" \
        http://admin:admin@localhost:3000/api/alerts | \
        jq '.' > "$BACKUP_PATH/alerts/legacy_alerts.json"
    
    # Get unified alerting rules (Grafana 9+)
    curl -s -H "Content-Type: application/json" \
        http://admin:admin@localhost:3000/api/ruler/grafana/api/v1/rules | \
        jq '.' > "$BACKUP_PATH/alerts/unified_alerts.json" 2>/dev/null || true
    
    echo -e "${GREEN}✅ Alert rules backed up${NC}"
}

# Backup organizations and users (basic info)
backup_org_users() {
    echo -e "${YELLOW}👥 Backing up organization and user info...${NC}"
    
    mkdir -p "$BACKUP_PATH/admin"
    
    # Get organization info
    curl -s -H "Content-Type: application/json" \
        http://admin:admin@localhost:3000/api/org | \
        jq '.' > "$BACKUP_PATH/admin/organization.json"
    
    # Get users (basic info, no passwords)
    curl -s -H "Content-Type: application/json" \
        http://admin:admin@localhost:3000/api/org/users | \
        jq '.' > "$BACKUP_PATH/admin/users.json"
    
    echo -e "${GREEN}✅ Organization and user info backed up${NC}"
}

# Create backup metadata
create_metadata() {
    echo -e "${YELLOW}📄 Creating backup metadata...${NC}"
    
    cat > "$BACKUP_PATH/backup_info.json" << EOF
{
  "backup_timestamp": "$TIMESTAMP",
  "backup_date": "$(date -Iseconds)",
  "grafana_version": "$(curl -s http://admin:admin@localhost:3000/api/health | jq -r '.version')",
  "backup_script_version": "1.0",
  "contents": {
    "dashboards": true,
    "datasources": true,
    "alerts": true,
    "organization": true,
    "users": true
  }
}
EOF
    
    echo -e "${GREEN}✅ Metadata created${NC}"
}

# Create archive
create_archive() {
    echo -e "${YELLOW}📦 Creating backup archive...${NC}"
    
    cd "$BACKUP_DIR"
    tar -czf "grafana_backup_$TIMESTAMP.tar.gz" "grafana_backup_$TIMESTAMP/"
    
    # Remove uncompressed directory
    rm -rf "grafana_backup_$TIMESTAMP/"
    
    echo -e "${GREEN}✅ Backup archive created: $BACKUP_DIR/grafana_backup_$TIMESTAMP.tar.gz${NC}"
}

# Restore function
restore_backup() {
    local backup_file="$1"
    
    if [ -z "$backup_file" ]; then
        echo -e "${RED}❌ Please specify a backup file to restore${NC}"
        echo "Usage: $0 restore /path/to/backup.tar.gz"
        exit 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        echo -e "${RED}❌ Backup file not found: $backup_file${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}🔄 Restoring from backup: $backup_file${NC}"
    
    # Extract backup
    RESTORE_DIR="/tmp/grafana_restore_$$"
    mkdir -p "$RESTORE_DIR"
    tar -xzf "$backup_file" -C "$RESTORE_DIR"
    
    BACKUP_CONTENT_DIR=$(find "$RESTORE_DIR" -name "grafana_backup_*" -type d | head -1)
    
    if [ -z "$BACKUP_CONTENT_DIR" ]; then
        echo -e "${RED}❌ Invalid backup file format${NC}"
        rm -rf "$RESTORE_DIR"
        exit 1
    fi
    
    # Restore dashboards
    if [ -d "$BACKUP_CONTENT_DIR/dashboards" ]; then
        echo -e "${YELLOW}📊 Restoring dashboards...${NC}"
        for dashboard_file in "$BACKUP_CONTENT_DIR/dashboards"/*.json; do
            if [ -f "$dashboard_file" ]; then
                dashboard_data=$(cat "$dashboard_file")
                curl -s -X POST \
                    -H "Content-Type: application/json" \
                    -d "{\"dashboard\": $dashboard_data, \"overwrite\": true}" \
                    http://admin:admin@localhost:3000/api/dashboards/db > /dev/null
                echo "  📋 Restored: $(basename "$dashboard_file")"
            fi
        done
        echo -e "${GREEN}✅ Dashboards restored${NC}"
    fi
    
    # Note: Data sources and other settings would need manual review
    echo -e "${YELLOW}⚠️  Note: Data sources and other settings need manual review${NC}"
    echo -e "${YELLOW}⚠️  Check files in: $BACKUP_CONTENT_DIR${NC}"
    
    # Don't clean up restore directory automatically
    echo -e "${GREEN}✅ Restore completed. Temporary files in: $RESTORE_DIR${NC}"
}

# List available backups
list_backups() {
    echo -e "${GREEN}📋 Available backups:${NC}"
    echo "===================="
    
    if [ -d "$BACKUP_DIR" ]; then
        find "$BACKUP_DIR" -name "grafana_backup_*.tar.gz" -type f | sort -r | while read -r backup; do
            size=$(du -h "$backup" | cut -f1)
            echo "  📦 $(basename "$backup") ($size)"
        done
    else
        echo -e "${YELLOW}No backups found in $BACKUP_DIR${NC}"
    fi
}

# Main function
main() {
    case "${1:-}" in
        "backup"|"")
            check_grafana
            create_backup_dir
            backup_dashboards
            backup_datasources
            backup_alerts
            backup_org_users
            create_metadata
            create_archive
            echo -e "${GREEN}🎉 Backup completed successfully!${NC}"
            ;;
        "restore")
            check_grafana
            restore_backup "$2"
            ;;
        "list")
            list_backups
            ;;
        *)
            echo "Usage: $0 {backup|restore|list}"
            echo ""
            echo "Commands:"
            echo "  backup          - Create a new backup (default)"
            echo "  restore <file>  - Restore from backup file"
            echo "  list            - List available backups"
            echo ""
            echo "Examples:"
            echo "  $0 backup"
            echo "  $0 restore ./backups/grafana_backup_20231201_120000.tar.gz"
            echo "  $0 list"
            exit 1
            ;;
    esac
}

main "$@"