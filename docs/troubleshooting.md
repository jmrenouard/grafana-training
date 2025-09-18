# Troubleshooting Guide

This guide helps you diagnose and fix common issues with the Grafana and Prometheus training environment.

## Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [Docker Issues](#docker-issues)
3. [Grafana Problems](#grafana-problems)
4. [Prometheus Issues](#prometheus-issues)
5. [Network Problems](#network-problems)
6. [Performance Issues](#performance-issues)
7. [Data Problems](#data-problems)

## Quick Diagnostics

Before diving into specific issues, run these quick checks:

### Check Service Status
```bash
./scripts/setup.sh status
```

### Check All Services
```bash
docker-compose ps
```

### View Recent Logs
```bash
docker-compose logs --tail=50
```

### Check Port Usage
```bash
sudo netstat -tlnp | grep -E ':(3000|9090|9100|8080|8081)'
```

## Docker Issues

### Services Won't Start

**Symptom**: `docker-compose up` fails or services exit immediately

**Possible Causes & Solutions**:

1. **Port conflicts**:
   ```bash
   # Check what's using the ports
   sudo netstat -tlnp | grep -E ':(3000|9090|9100|8080|8081)'
   
   # Kill processes using the ports
   sudo kill -9 <PID>
   
   # Or modify docker-compose.yml to use different ports
   ```

2. **Insufficient permissions**:
   ```bash
   # Add user to docker group
   sudo usermod -aG docker $USER
   
   # Log out and back in, then test
   docker run hello-world
   ```

3. **Insufficient disk space**:
   ```bash
   # Check disk space
   df -h
   
   # Clean up Docker
   docker system prune -f
   docker volume prune -f
   ```

4. **Memory issues**:
   ```bash
   # Check available memory
   free -h
   
   # Increase Docker memory limit in Docker Desktop settings
   ```

### Image Pull Failures

**Symptom**: "failed to solve with frontend dockerfile.v0"

**Solutions**:
```bash
# Pull images manually
docker pull grafana/grafana:latest
docker pull prom/prometheus:latest
docker pull prom/node-exporter:latest

# Clear Docker cache
docker builder prune -f
```

### Volume Mount Issues

**Symptom**: Configuration files not loading

**Solutions**:
```bash
# Check file permissions
ls -la configs/
chmod -R 644 configs/

# Verify paths in docker-compose.yml
# Use absolute paths if needed
```

## Grafana Problems

### Cannot Access Grafana Web Interface

**Symptoms**:
- Browser shows "This site can't be reached"
- Connection timeout or refused

**Diagnostics**:
```bash
# Check if Grafana container is running
docker-compose ps grafana

# Check Grafana logs
docker-compose logs grafana

# Test port connectivity
curl -I http://localhost:3000
```

**Solutions**:
1. **Wait for startup**: Grafana can take 30-60 seconds to start
2. **Check firewall**: Ensure port 3000 is open
3. **Restart Grafana**:
   ```bash
   docker-compose restart grafana
   ```

### Login Issues

**Symptom**: Cannot login with admin/admin

**Solutions**:
1. **Reset admin password**:
   ```bash
   docker-compose exec grafana grafana-cli admin reset-admin-password admin
   ```

2. **Check environment variables**:
   ```bash
   docker-compose exec grafana env | grep GF_
   ```

### Dashboard Not Loading

**Symptoms**:
- Blank panels
- "No data" errors
- Loading forever

**Diagnostics**:
```bash
# Test Prometheus connection from Grafana container
docker-compose exec grafana curl http://prometheus:9090/api/v1/query?query=up

# Check data source configuration
# Go to Configuration > Data Sources > Prometheus > Test
```

**Solutions**:
1. **Verify data source**: Configuration > Data Sources > Test
2. **Check queries**: Use Explore to test PromQL queries
3. **Time range issues**: Adjust dashboard time range
4. **Restart Grafana**:
   ```bash
   docker-compose restart grafana
   ```

### Dashboards Missing

**Symptom**: Pre-configured dashboards don't appear

**Solutions**:
```bash
# Check dashboard provisioning
docker-compose exec grafana ls -la /var/lib/grafana/dashboards/

# Restart Grafana to reload provisioning
docker-compose restart grafana

# Check provisioning logs
docker-compose logs grafana | grep -i provision
```

## Prometheus Issues

### Cannot Access Prometheus

**Symptoms**:
- http://localhost:9090 not accessible
- Connection refused

**Diagnostics**:
```bash
# Check container status
docker-compose ps prometheus

# Check logs
docker-compose logs prometheus

# Test from inside container
docker-compose exec prometheus wget -qO- localhost:9090/-/healthy
```

### Targets Down

**Symptom**: Targets show as "DOWN" in Status > Targets

**Common Causes**:

1. **Node Exporter not running**:
   ```bash
   docker-compose ps node-exporter
   docker-compose logs node-exporter
   ```

2. **Network connectivity**:
   ```bash
   # Test from Prometheus container
   docker-compose exec prometheus curl http://node-exporter:9100/metrics
   ```

3. **Configuration issues**:
   ```bash
   # Validate Prometheus config
   docker-compose exec prometheus promtool check config /etc/prometheus/prometheus.yml
   ```

**Solutions**:
```bash
# Restart specific service
docker-compose restart node-exporter

# Reload Prometheus config
curl -X POST http://localhost:9090/-/reload

# Check service discovery
# Go to http://localhost:9090/service-discovery
```

### Configuration Errors

**Symptom**: Prometheus fails to start with config errors

**Diagnostics**:
```bash
# Check configuration syntax
docker run --rm -v $(pwd)/configs/prometheus:/etc/prometheus prom/prometheus:latest promtool check config /etc/prometheus/prometheus.yml

# Validate rules
docker run --rm -v $(pwd)/configs/prometheus:/etc/prometheus prom/prometheus:latest promtool check rules /etc/prometheus/rules/*.yml
```

### High Memory Usage

**Symptom**: Prometheus consumes too much memory

**Solutions**:
1. **Reduce retention period**:
   ```yaml
   # In docker-compose.yml, add to prometheus command:
   - '--storage.tsdb.retention.time=7d'
   ```

2. **Limit series**:
   ```yaml
   # Add to prometheus command:
   - '--storage.tsdb.retention.size=1GB'
   ```

3. **Reduce scrape frequency**:
   ```yaml
   # In prometheus.yml:
   global:
     scrape_interval: 30s  # Instead of 15s
   ```

## Network Problems

### DNS Resolution Issues

**Symptom**: Services can't communicate with each other

**Diagnostics**:
```bash
# Test DNS resolution between containers
docker-compose exec grafana nslookup prometheus
docker-compose exec prometheus nslookup grafana
```

**Solutions**:
```bash
# Recreate containers with proper network
docker-compose down
docker-compose up -d
```

### Port Binding Conflicts

**Symptom**: "Port already in use" errors

**Find and resolve conflicts**:
```bash
# Find what's using the port
sudo netstat -tlnp | grep :3000
sudo lsof -i :3000

# Kill the process
sudo kill -9 <PID>

# Or change ports in docker-compose.yml
```

## Performance Issues

### Slow Dashboard Loading

**Possible Causes**:
1. **Complex queries**: Simplify PromQL queries
2. **Large time ranges**: Reduce dashboard time range
3. **High cardinality metrics**: Review metric labels
4. **Resource constraints**: Increase Docker memory

**Solutions**:
```bash
# Check query performance in Prometheus
# Go to http://localhost:9090/graph
# Use query stats to identify slow queries

# Monitor resource usage
docker stats
```

### High CPU Usage

**Diagnostics**:
```bash
# Check container resource usage
docker stats

# Check system resources
top
htop
```

**Solutions**:
1. **Increase Docker resources**: Docker Desktop settings
2. **Reduce scrape frequency**: Increase scrape_interval
3. **Use recording rules**: Pre-compute complex queries

## Data Problems

### No Metrics Data

**Symptom**: Grafana shows "No data" for all queries

**Diagnostics**:
```bash
# Check if Prometheus is scraping data
curl http://localhost:9090/api/v1/query?query=up

# Check targets status
curl http://localhost:9090/api/v1/targets

# Test specific metrics
curl http://localhost:9100/metrics
```

**Solutions**:
1. **Wait for data**: Allow time for first scrape (15-30 seconds)
2. **Check target endpoints**: Verify metrics endpoints work
3. **Restart services**:
   ```bash
   docker-compose restart
   ```

### Incorrect Metrics

**Symptom**: Metrics show wrong values or unexpected results

**Common Issues**:
1. **Counter vs Gauge confusion**: Use rate() for counters
2. **Wrong time ranges**: Check query time ranges
3. **Label mismatches**: Verify label names and values

**Debugging**:
```bash
# Test queries in Prometheus
# Go to http://localhost:9090/graph
# Use "Table" view to see raw values
```

### Historical Data Missing

**Symptom**: Old data disappears

**Causes**:
1. **Retention period**: Data deleted after retention time
2. **Volume issues**: Data lost when containers restart
3. **Storage limits**: Data pruned due to size limits

**Solutions**:
```bash
# Check retention settings
docker-compose exec prometheus cat /etc/prometheus/prometheus.yml

# Ensure volumes are persistent
# Check docker-compose.yml volumes section
```

## Getting Additional Help

### Log Analysis

Always check logs for specific error messages:
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs grafana
docker-compose logs prometheus

# Follow logs in real-time
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100
```

### Useful Commands

```bash
# Full restart
docker-compose down && docker-compose up -d

# Clean restart (removes volumes)
docker-compose down -v && docker-compose up -d

# Check Docker system info
docker system info
docker system df

# Inspect container details
docker inspect grafana-training_grafana_1
```

### When to Ask for Help

If you've tried the above solutions and still have issues:

1. **Collect information**:
   - Error messages from logs
   - Docker version: `docker --version`
   - OS information: `uname -a`
   - Steps to reproduce the issue

2. **Check existing issues** in the repository

3. **Open a new issue** with detailed information

### Emergency Reset

If everything is broken and you want to start fresh:

```bash
# Stop and remove everything
docker-compose down -v

# Remove all Docker containers and images (CAREFUL!)
docker system prune -a -f

# Remove all volumes (CAREFUL!)
docker volume prune -f

# Start fresh
docker-compose up -d
```

**Warning**: This will delete ALL data and require re-downloading images.