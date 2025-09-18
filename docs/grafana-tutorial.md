# Grafana Tutorial

This tutorial will guide you through the basics of using Grafana for monitoring and visualization.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Understanding the Interface](#understanding-the-interface)
3. [Working with Data Sources](#working-with-data-sources)
4. [Creating Your First Dashboard](#creating-your-first-dashboard)
5. [Visualization Types](#visualization-types)
6. [Working with Variables](#working-with-variables)
7. [Setting Up Alerts](#setting-up-alerts)
8. [Best Practices](#best-practices)

## Getting Started

Before starting this tutorial, ensure you have:
1. Completed the [installation](installation.md)
2. All services running (check with `./scripts/setup.sh status`)
3. Access to Grafana at http://localhost:3000

## Understanding the Interface

### Main Navigation

When you log into Grafana, you'll see:

- **Home Dashboard**: Overview of your instance
- **Dashboards**: Browse and create dashboards
- **Explore**: Query data sources directly
- **Alerting**: Manage alerts and notifications
- **Configuration**: Data sources, users, and settings

### Key Concepts

- **Dashboard**: A collection of panels showing visualizations
- **Panel**: Individual charts, graphs, or tables
- **Data Source**: Where your data comes from (Prometheus, MySQL, etc.)
- **Query**: How you request specific data
- **Variable**: Dynamic values that can change dashboard content

## Working with Data Sources

Prometheus should already be configured as a data source. Let's verify:

1. Go to **Configuration** → **Data Sources**
2. Click on **Prometheus**
3. Scroll down and click **Test** - you should see "Data source is working"

### Understanding Prometheus Queries

Prometheus uses PromQL (Prometheus Query Language). Basic examples:

```promql
# Get CPU usage
100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Get memory usage
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# Get network traffic
irate(node_network_receive_bytes_total[5m])
```

## Creating Your First Dashboard

Let's create a simple system monitoring dashboard:

### Step 1: Create New Dashboard

1. Click **+** → **Dashboard**
2. Click **Add new panel**

### Step 2: Configure Your First Panel

1. **Query Tab**:
   - Query: `100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)`
   - Legend: `CPU Usage %`

2. **Panel Options**:
   - Title: `CPU Usage`
   - Description: `Current CPU usage percentage`

3. **Field Options**:
   - Unit: `Percent (0-100)`
   - Min: `0`
   - Max: `100`

4. Click **Apply**

### Step 3: Add More Panels

Repeat the process for:

**Memory Usage**:
```promql
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100
```

**Disk Usage**:
```promql
(1 - (node_filesystem_avail_bytes{fstype!="tmpfs"} / node_filesystem_size_bytes{fstype!="tmpfs"})) * 100
```

**Network I/O**:
```promql
irate(node_network_receive_bytes_total[5m])
```

### Step 4: Save Your Dashboard

1. Click the **Save** icon (disk icon)
2. Name: `My First Dashboard`
3. Click **Save**

## Visualization Types

Grafana offers many visualization types:

### Time Series (Graph)
- Best for: Metrics over time
- Use cases: CPU usage, memory trends, network traffic

### Stat
- Best for: Single values
- Use cases: Current CPU %, uptime, error count

### Gauge
- Best for: Values with thresholds
- Use cases: Disk usage, temperature, performance scores

### Table
- Best for: Multiple metrics in rows
- Use cases: Service status, error logs, top processes

### Heatmap
- Best for: Distribution over time
- Use cases: Response time distribution, error rates

## Working with Variables

Variables make dashboards dynamic and reusable:

### Creating a Variable

1. Go to **Dashboard Settings** (gear icon)
2. **Variables** → **Add variable**
3. Configure:
   - **Name**: `instance`
   - **Type**: `Query`
   - **Query**: `label_values(up, instance)`
4. **Save**

### Using Variables

In queries, reference variables with `$variable_name`:
```promql
up{instance="$instance"}
```

## Setting Up Alerts

Alerts notify you when metrics cross thresholds:

### Creating an Alert Rule

1. Edit a panel
2. Go to **Alert tab**
3. **Create Alert**
4. Configure:
   - **Name**: `High CPU Usage`
   - **Condition**: `IS ABOVE 80`
   - **Frequency**: `10s`
   - **For**: `1m`

### Notification Channels

1. **Alerting** → **Notification channels**
2. **Add channel**
3. Choose type (Email, Slack, etc.)
4. Configure settings

## Best Practices

### Dashboard Design

1. **Keep it simple**: Don't overcrowd dashboards
2. **Group related metrics**: Use rows to organize panels
3. **Use consistent time ranges**: Ensure panels show the same period
4. **Add descriptions**: Help users understand what they're seeing

### Query Optimization

1. **Use rate() for counters**: `rate(http_requests_total[5m])`
2. **Aggregate data**: Use `avg()`, `sum()`, `max()` functions
3. **Filter unnecessary labels**: Use `{job="node-exporter"}`
4. **Avoid high cardinality**: Don't group by labels with many values

### Alerting

1. **Set appropriate thresholds**: Avoid false positives
2. **Use multi-condition alerts**: Combine multiple metrics
3. **Add context to notifications**: Include runbook links
4. **Test your alerts**: Ensure they fire when expected

## Practice Exercises

### Exercise 1: System Dashboard
Create a dashboard with:
- CPU usage (time series)
- Memory usage (gauge)
- Disk space (stat)
- Network traffic (time series)

### Exercise 2: Application Metrics
If using the sample app:
- Request rate
- Error rate
- Response time percentiles

### Exercise 3: Alerting
Set up alerts for:
- CPU usage > 80%
- Memory usage > 90%
- Disk space < 10%

## Next Steps

- Explore [Prometheus Guide](prometheus-guide.md)
- Check [Troubleshooting](troubleshooting.md) for common issues
- Practice with real-world scenarios
- Learn advanced PromQL queries

## Additional Resources

- [Grafana Documentation](https://grafana.com/docs/)
- [PromQL Tutorial](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Community Dashboards](https://grafana.com/grafana/dashboards/)