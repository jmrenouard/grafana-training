# Prometheus Guide

This guide covers Prometheus fundamentals, configuration, and best practices for monitoring.

## Table of Contents

1. [What is Prometheus?](#what-is-prometheus)
2. [Architecture Overview](#architecture-overview)
3. [Metrics and Labels](#metrics-and-labels)
4. [PromQL Basics](#promql-basics)
5. [Configuration](#configuration)
6. [Service Discovery](#service-discovery)
7. [Recording Rules](#recording-rules)
8. [Alerting Rules](#alerting-rules)
9. [Best Practices](#best-practices)

## What is Prometheus?

Prometheus is an open-source monitoring and alerting toolkit designed for reliability and scalability. It:

- **Collects metrics** from configured targets
- **Stores time-series data** efficiently
- **Provides a query language** (PromQL) for analysis
- **Supports alerting** based on query results
- **Integrates well** with Grafana and other tools

### Key Features

- Multi-dimensional data model with time series data
- Flexible query language (PromQL)
- Pull-based metric collection
- Service discovery integration
- Efficient storage engine
- Built-in alerting

## Architecture Overview

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Target    │    │   Target    │    │   Target    │
│ Application │    │    Node     │    │   Service   │
│   :8080     │    │  Exporter   │    │   :9100     │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │ (scrape)
                           ▼
                ┌─────────────────┐
                │   Prometheus    │
                │     Server      │
                │     :9090       │
                └─────────────────┘
                           │
                           ▼
                ┌─────────────────┐
                │     Grafana     │
                │     :3000       │
                └─────────────────┘
```

## Metrics and Labels

### Metric Types

**Counter**: Always increasing value
```
http_requests_total{method="GET", status="200"} 1234
```

**Gauge**: Can go up and down
```
memory_usage_bytes{instance="server1"} 8589934592
```

**Histogram**: Observations in buckets
```
http_request_duration_seconds_bucket{le="0.1"} 1000
http_request_duration_seconds_bucket{le="0.5"} 1500
```

**Summary**: Similar to histogram with quantiles
```
http_request_duration_seconds{quantile="0.5"} 0.12
http_request_duration_seconds{quantile="0.9"} 0.35
```

### Labels

Labels add dimensions to metrics:
```
cpu_usage_percent{instance="server1", cpu="0", mode="idle"} 95.5
cpu_usage_percent{instance="server1", cpu="0", mode="user"} 3.2
cpu_usage_percent{instance="server1", cpu="0", mode="system"} 1.3
```

## PromQL Basics

### Instant Vector Selectors

Select metrics at a single point in time:
```promql
up
up{job="prometheus"}
up{job="prometheus", instance="localhost:9090"}
```

### Range Vector Selectors

Select metrics over a time range:
```promql
up[5m]
http_requests_total[1h]
```

### Operators

**Arithmetic**: `+`, `-`, `*`, `/`, `%`, `^`
```promql
(node_memory_MemTotal_bytes - node_memory_MemFree_bytes) / 1024 / 1024
```

**Comparison**: `==`, `!=`, `>`, `<`, `>=`, `<=`
```promql
up == 1
cpu_usage_percent > 80
```

**Logical**: `and`, `or`, `unless`
```promql
up == 1 and cpu_usage_percent > 50
```

### Functions

**rate()**: Calculate per-second rate
```promql
rate(http_requests_total[5m])
```

**irate()**: Instant rate (last two samples)
```promql
irate(cpu_seconds_total[5m])
```

**increase()**: Total increase over time range
```promql
increase(http_requests_total[1h])
```

**avg()**, **sum()**, **max()**, **min()**: Aggregation
```promql
avg(cpu_usage_percent) by (instance)
sum(rate(http_requests_total[5m])) by (method)
```

### Common Queries

**CPU Usage**:
```promql
100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

**Memory Usage**:
```promql
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100
```

**Disk Usage**:
```promql
(1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100
```

**HTTP Request Rate**:
```promql
sum(rate(http_requests_total[5m])) by (method, status)
```

**95th Percentile Response Time**:
```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

## Configuration

### Basic prometheus.yml

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']
```

### Scrape Configuration Options

```yaml
scrape_configs:
  - job_name: 'my-app'
    scrape_interval: 30s     # Override global interval
    scrape_timeout: 10s      # Timeout for each scrape
    metrics_path: '/metrics' # Path to metrics endpoint
    static_configs:
      - targets: ['app1:8080', 'app2:8080']
    relabel_configs:         # Modify labels
      - source_labels: [__address__]
        target_label: instance
        regex: '([^:]+):.*'
        replacement: '${1}'
```

## Service Discovery

Instead of static targets, use service discovery:

### File-based Discovery

```yaml
scrape_configs:
  - job_name: 'file-discovery'
    file_sd_configs:
      - files:
        - 'targets/*.json'
        refresh_interval: 1m
```

Example target file (`targets/web-servers.json`):
```json
[
  {
    "targets": ["web1:8080", "web2:8080"],
    "labels": {
      "service": "web",
      "environment": "production"
    }
  }
]
```

### Docker Discovery

```yaml
scrape_configs:
  - job_name: 'docker'
    docker_sd_configs:
      - host: unix:///var/run/docker.sock
        refresh_interval: 5s
    relabel_configs:
      - source_labels: [__meta_docker_container_name]
        target_label: container
```

## Recording Rules

Pre-compute expensive queries:

```yaml
groups:
  - name: cpu-rules
    rules:
      - record: instance:cpu_usage:rate5m
        expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

      - record: job:cpu_usage:mean5m
        expr: avg by(job) (instance:cpu_usage:rate5m)
```

Benefits:
- Faster dashboard loading
- Consistent calculations
- Reduced query complexity

## Alerting Rules

Define when to fire alerts:

```yaml
groups:
  - name: system-alerts
    rules:
      - alert: HighCPUUsage
        expr: instance:cpu_usage:rate5m > 80
        for: 5m
        labels:
          severity: warning
          service: system
        annotations:
          summary: "High CPU usage on {{ $labels.instance }}"
          description: "CPU usage is {{ $value }}% for more than 5 minutes"

      - alert: DiskSpaceLow
        expr: (node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100 < 10
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Disk space low on {{ $labels.instance }}"
          description: "Only {{ $value }}% disk space remaining on {{ $labels.mountpoint }}"
```

## Best Practices

### Metric Design

1. **Use consistent naming**: `http_requests_total`, `cpu_usage_seconds`
2. **Include units in names**: `_bytes`, `_seconds`, `_total`
3. **Use base units**: seconds instead of milliseconds
4. **Avoid high cardinality**: Don't use user IDs as labels

### Label Guidelines

1. **Keep labels low cardinality**: < 10 values per label
2. **Use meaningful names**: `method`, `status`, `instance`
3. **Avoid redundant labels**: Don't duplicate information
4. **Use label values consistently**: `GET` not `get`

### Query Performance

1. **Use recording rules** for expensive queries
2. **Limit time ranges** in dashboards
3. **Use appropriate functions**: `rate()` for counters
4. **Aggregate early**: `sum() by (job)` instead of `sum()`

### Storage

1. **Set retention period**: `--storage.tsdb.retention.time=15d`
2. **Monitor disk usage**: Prometheus can grow quickly
3. **Use recording rules**: Reduce storage requirements
4. **Consider downsampling**: For long-term storage

### Configuration Management

1. **Version control**: Keep prometheus.yml in git
2. **Validate config**: Use `promtool check config`
3. **Test rules**: Use `promtool check rules`
4. **Reload config**: `curl -X POST localhost:9090/-/reload`

## Troubleshooting

### Common Issues

**Target Down**:
- Check if the service is running
- Verify network connectivity
- Check firewall rules
- Validate metrics endpoint

**High Memory Usage**:
- Review metric cardinality
- Implement recording rules
- Adjust retention settings
- Consider series limits

**Slow Queries**:
- Use recording rules
- Optimize PromQL queries
- Reduce time ranges
- Check for high cardinality labels

### Useful Commands

```bash
# Check configuration
promtool check config prometheus.yml

# Check rules
promtool check rules rules/*.yml

# Query from command line
promtool query instant 'up'

# Test rules
promtool test rules test.yml
```

## Next Steps

- Practice PromQL queries in Prometheus web UI
- Create custom recording and alerting rules
- Explore exporters for different services
- Learn about Prometheus federation
- Study performance optimization techniques

## Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [PromQL Tutorial](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Best Practices](https://prometheus.io/docs/practices/)
- [Exporters List](https://prometheus.io/docs/instrumenting/exporters/)