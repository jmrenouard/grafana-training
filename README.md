# Grafana and Prometheus Training

This repository contains comprehensive training materials, scripts, configurations, and documentation for learning Grafana and Prometheus monitoring stack.

## 📋 Contents

- **Configurations**: Ready-to-use configuration files for Grafana and Prometheus
- **Scripts**: Utility scripts for setup, data generation, and maintenance
- **Documentation**: Comprehensive guides and tutorials
- **Examples**: Sample dashboards, alerts, and data sources
- **Docker Setup**: Complete containerized environment for hands-on learning

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Getting Started

1. Clone this repository:
```bash
git clone https://github.com/jmrenouard/grafana-training.git
cd grafana-training
```

2. Start the monitoring stack:
```bash
docker-compose up -d
```

3. Access the services:
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

### What You'll Learn

- 📊 **Grafana Fundamentals**: Dashboard creation, visualization types, data sources
- 🔍 **Prometheus Basics**: Metrics collection, PromQL queries, service discovery
- 🚨 **Alerting**: Setting up alerts and notification channels
- 📈 **Best Practices**: Monitoring strategies and performance optimization
- 🛠️ **Advanced Topics**: Custom metrics, recording rules, and federation

## 📁 Repository Structure

```
├── configs/           # Configuration files
│   ├── grafana/      # Grafana configuration
│   └── prometheus/   # Prometheus configuration
├── scripts/          # Utility scripts
├── docs/             # Documentation and tutorials
├── examples/         # Sample dashboards and alerts
│   ├── dashboards/   # Grafana dashboard JSON files
│   └── alerts/       # Alert rule examples
├── docker/           # Docker-related files
└── docker-compose.yml # Complete stack setup
```

## 📚 Training Modules

1. **Getting Started** - Basic setup and concepts
2. **Data Sources** - Connecting Grafana to various data sources
3. **Dashboard Creation** - Building effective visualizations
4. **Alerting** - Setting up monitoring alerts
5. **Advanced Topics** - Custom metrics and complex queries

## 🔧 Available Scripts

- `scripts/setup.sh` - Initial environment setup
- `scripts/generate-metrics.py` - Sample metrics generator
- `scripts/backup.sh` - Backup Grafana dashboards and settings

## 🐳 Docker Environment

The included Docker Compose setup provides:
- Grafana with pre-configured dashboards
- Prometheus with sample targets
- Node Exporter for system metrics
- Sample application for testing

## 📖 Documentation

Detailed documentation is available in the `docs/` directory:
- [Installation Guide](docs/installation.md)
- [Grafana Tutorial](docs/grafana-tutorial.md)
- [Prometheus Guide](docs/prometheus-guide.md)
- [Troubleshooting](docs/troubleshooting.md)

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests for any improvements.

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:
1. Check the [troubleshooting guide](docs/troubleshooting.md)
2. Open an issue in this repository
3. Review the documentation in the `docs/` folder
