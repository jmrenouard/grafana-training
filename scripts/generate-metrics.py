#!/usr/bin/env python3
"""
Sample Metrics Generator for Grafana and Prometheus Training

This script generates sample metrics that can be scraped by Prometheus
to provide data for training dashboards and alerts.
"""

import random
import time
import http.server
import socketserver
from datetime import datetime
import threading
import argparse


class MetricsGenerator:
    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        
    def generate_application_metrics(self):
        """Generate sample application metrics"""
        now = time.time()
        uptime = now - self.start_time
        
        # Simulate some realistic patterns
        hour = datetime.now().hour
        base_load = 0.3 + 0.5 * (1 + abs(12 - hour) / 12)  # Higher load during business hours
        cpu_usage = max(0, min(100, base_load * 100 + random.normalvariate(0, 10)))
        memory_usage = max(0, min(100, base_load * 80 + random.normalvariate(0, 5)))
        
        # Network metrics
        network_in = random.uniform(1000000, 10000000)  # bytes
        network_out = random.uniform(500000, 5000000)   # bytes
        
        # Application metrics
        response_time = random.lognormvariate(1, 0.5) * 100  # milliseconds
        
        # Occasionally generate errors
        if random.random() < 0.05:  # 5% chance
            self.error_count += 1
            
        self.request_count += random.randint(1, 10)
        
        return {
            'cpu_usage_percent': cpu_usage,
            'memory_usage_percent': memory_usage,
            'network_received_bytes_total': network_in,
            'network_transmitted_bytes_total': network_out,
            'http_requests_total': self.request_count,
            'http_request_duration_seconds': response_time / 1000,
            'http_errors_total': self.error_count,
            'application_uptime_seconds': uptime,
        }
    
    def format_prometheus_metrics(self, metrics):
        """Format metrics in Prometheus exposition format"""
        output = []
        
        # Add HELP and TYPE comments
        output.append("# HELP cpu_usage_percent Current CPU usage percentage")
        output.append("# TYPE cpu_usage_percent gauge")
        output.append(f"cpu_usage_percent {metrics['cpu_usage_percent']:.2f}")
        output.append("")
        
        output.append("# HELP memory_usage_percent Current memory usage percentage")
        output.append("# TYPE memory_usage_percent gauge")
        output.append(f"memory_usage_percent {metrics['memory_usage_percent']:.2f}")
        output.append("")
        
        output.append("# HELP network_received_bytes_total Total bytes received")
        output.append("# TYPE network_received_bytes_total counter")
        output.append(f"network_received_bytes_total {metrics['network_received_bytes_total']:.0f}")
        output.append("")
        
        output.append("# HELP network_transmitted_bytes_total Total bytes transmitted")
        output.append("# TYPE network_transmitted_bytes_total counter")
        output.append(f"network_transmitted_bytes_total {metrics['network_transmitted_bytes_total']:.0f}")
        output.append("")
        
        output.append("# HELP http_requests_total Total HTTP requests")
        output.append("# TYPE http_requests_total counter")
        output.append(f"http_requests_total {metrics['http_requests_total']}")
        output.append("")
        
        output.append("# HELP http_request_duration_seconds HTTP request duration in seconds")
        output.append("# TYPE http_request_duration_seconds histogram")
        output.append(f"http_request_duration_seconds {metrics['http_request_duration_seconds']:.3f}")
        output.append("")
        
        output.append("# HELP http_errors_total Total HTTP errors")
        output.append("# TYPE http_errors_total counter")
        output.append(f"http_errors_total {metrics['http_errors_total']}")
        output.append("")
        
        output.append("# HELP application_uptime_seconds Application uptime in seconds")
        output.append("# TYPE application_uptime_seconds counter")
        output.append(f"application_uptime_seconds {metrics['application_uptime_seconds']:.0f}")
        output.append("")
        
        return "\n".join(output)


class MetricsHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, generator=None, **kwargs):
        self.generator = generator
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/metrics':
            metrics = self.generator.generate_application_metrics()
            response = self.generator.format_prometheus_metrics(metrics)
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(response.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass


def main():
    parser = argparse.ArgumentParser(description='Generate sample metrics for Prometheus')
    parser.add_argument('--port', type=int, default=8082, help='Port to serve metrics on (default: 8082)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    generator = MetricsGenerator()
    
    # Create a custom handler with the generator
    def handler(*args, **kwargs):
        return MetricsHandler(*args, generator=generator, **kwargs)
    
    try:
        with socketserver.TCPServer(("", args.port), handler) as httpd:
            if args.verbose:
                print(f"🎯 Metrics server started on port {args.port}")
                print(f"📊 Metrics available at: http://localhost:{args.port}/metrics")
                print("📈 Generating realistic sample metrics...")
                print("Press Ctrl+C to stop")
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        if args.verbose:
            print("\n🛑 Metrics generator stopped")
    except Exception as e:
        print(f"❌ Error starting metrics server: {e}")


if __name__ == "__main__":
    main()