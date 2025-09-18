# Installation Guide

This guide will help you set up the Grafana and Prometheus training environment on your local machine.

## Prerequisites

Before starting, ensure you have the following installed:

- **Docker** (version 20.10 or later)
- **Docker Compose** (version 1.29 or later)
- **Git**

### Installing Docker

#### On Ubuntu/Debian:
```bash
# Update package index
sudo apt-get update

# Install Docker
sudo apt-get install docker.io docker-compose

# Add your user to docker group
sudo usermod -aG docker $USER

# Log out and back in for group changes to take effect
```

#### On macOS:
```bash
# Install Docker Desktop
brew install --cask docker

# Or download from: https://docs.docker.com/desktop/mac/install/
```

#### On Windows:
- Download Docker Desktop from: https://docs.docker.com/desktop/windows/install/
- Follow the installation wizard

## Quick Setup

1. **Clone the repository**:
```bash
git clone https://github.com/jmrenouard/grafana-training.git
cd grafana-training
```

2. **Start the environment**:
```bash
./scripts/setup.sh start
```

3. **Verify installation**:
```bash
./scripts/setup.sh status
```

## Manual Setup

If you prefer to set up manually:

1. **Start all services**:
```bash
docker-compose up -d
```

2. **Check if services are running**:
```bash
docker-compose ps
```

3. **View logs** (if needed):
```bash
docker-compose logs -f
```

## Accessing Services

Once everything is running, you can access:

- **Grafana**: http://localhost:3000
  - Username: `admin`
  - Password: `admin`
- **Prometheus**: http://localhost:9090
- **Node Exporter**: http://localhost:9100
- **cAdvisor**: http://localhost:8080
- **Sample App**: http://localhost:8081

## Initial Configuration

### Grafana First Login

1. Open http://localhost:3000
2. Login with `admin/admin`
3. You'll be prompted to change the password (optional for training)
4. The Prometheus data source should be automatically configured

### Verifying Prometheus

1. Open http://localhost:9090
2. Go to Status → Targets
3. Verify all targets are "UP"

## Troubleshooting

### Common Issues

**Port conflicts**:
If you get port binding errors, check if ports 3000, 9090, 9100, 8080, or 8081 are already in use:
```bash
sudo netstat -tlnp | grep -E ':(3000|9090|9100|8080|8081)'
```

**Docker permission denied**:
Make sure your user is in the docker group:
```bash
sudo usermod -aG docker $USER
# Log out and back in
```

**Services not starting**:
Check Docker logs:
```bash
docker-compose logs grafana
docker-compose logs prometheus
```

**Dashboard not loading**:
Wait a few minutes for services to fully start, then refresh the browser.

### Stopping the Environment

To stop all services:
```bash
./scripts/setup.sh stop
```

Or manually:
```bash
docker-compose down
```

### Cleaning Up

To remove all containers and volumes:
```bash
docker-compose down -v
docker system prune -f
```

## Next Steps

After successful installation, proceed to:
- [Grafana Tutorial](grafana-tutorial.md)
- [Prometheus Guide](prometheus-guide.md)

## Getting Help

If you encounter issues:
1. Check the [Troubleshooting](troubleshooting.md) guide
2. Review Docker and Docker Compose logs
3. Open an issue in the repository