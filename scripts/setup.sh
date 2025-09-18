#!/bin/bash

# Grafana and Prometheus Setup Script
# This script helps set up the training environment

set -e

echo "🚀 Setting up Grafana and Prometheus Training Environment"
echo "=========================================================="

# Check prerequisites
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker compose version &> /dev/null; then
        echo "❌ Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    echo "✅ Docker and Docker Compose are available"
}

# Start the monitoring stack
start_stack() {
    echo "📦 Starting the monitoring stack..."
    docker compose up -d
    
    echo "⏳ Waiting for services to be ready..."
    sleep 10
    
    # Check if services are running
    if curl -s http://localhost:3000 > /dev/null; then
        echo "✅ Grafana is running at http://localhost:3000"
        echo "   Default credentials: admin/admin"
    else
        echo "⚠️  Grafana might still be starting up"
    fi
    
    if curl -s http://localhost:9090 > /dev/null; then
        echo "✅ Prometheus is running at http://localhost:9090"
    else
        echo "⚠️  Prometheus might still be starting up"
    fi
}

# Stop the monitoring stack
stop_stack() {
    echo "🛑 Stopping the monitoring stack..."
    docker compose down
    echo "✅ Stack stopped"
}

# Show logs
show_logs() {
    echo "📋 Showing logs for all services..."
    docker compose logs -f
}

# Show status
show_status() {
    echo "📊 Service Status:"
    echo "=================="
    docker compose ps
    
    echo -e "\n🌐 Access URLs:"
    echo "==============="
    echo "Grafana:    http://localhost:3000 (admin/admin)"
    echo "Prometheus: http://localhost:9090"
    echo "Node Exporter: http://localhost:9100"
    echo "cAdvisor:   http://localhost:8080"
    echo "Sample App: http://localhost:8081"
}

# Main menu
main() {
    case "${1:-}" in
        "start")
            check_docker
            start_stack
            ;;
        "stop")
            stop_stack
            ;;
        "logs")
            show_logs
            ;;
        "status")
            show_status
            ;;
        "restart")
            stop_stack
            sleep 2
            check_docker
            start_stack
            ;;
        *)
            echo "Usage: $0 {start|stop|restart|logs|status}"
            echo ""
            echo "Commands:"
            echo "  start   - Start the monitoring stack"
            echo "  stop    - Stop the monitoring stack"
            echo "  restart - Restart the monitoring stack"
            echo "  logs    - Show logs from all services"
            echo "  status  - Show service status and URLs"
            exit 1
            ;;
    esac
}

main "$@"