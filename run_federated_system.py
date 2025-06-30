#!/usr/bin/env python3
"""
Utility script to run and manage the federated learning system
"""

import os
import sys
import time
import subprocess
import argparse
import logging
from typing import List, Dict
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FederatedSystemManager:
    """Manages the federated learning system"""
    
    def __init__(self, docker_compose_file: str = "docker-compose.yml"):
        self.docker_compose_file = docker_compose_file
        self.logs_dir = "logs"
        
        # Ensure logs directory exists
        os.makedirs(self.logs_dir, exist_ok=True)
    
    def build_images(self):
        """Build Docker images for server and clients"""
        logger.info("Building Docker images...")
        try:
            subprocess.run([
                "docker-compose", "-f", self.docker_compose_file, "build"
            ], check=True)
            logger.info("Docker images built successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to build Docker images: {e}")
            return False
    
    def start_system(self):
        """Start the federated learning system"""
        logger.info("Starting federated learning system...")
        try:
            subprocess.run([
                "docker-compose", "-f", self.docker_compose_file, "up", "-d"
            ], check=True)
            logger.info("Federated learning system started")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to start system: {e}")
            return False
    
    def stop_system(self):
        """Stop the federated learning system"""
        logger.info("Stopping federated learning system...")
        try:
            subprocess.run([
                "docker-compose", "-f", self.docker_compose_file, "down"
            ], check=True)
            logger.info("Federated learning system stopped")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to stop system: {e}")
            return False
    
    def restart_system(self):
        """Restart the federated learning system"""
        logger.info("Restarting federated learning system...")
        if self.stop_system():
            time.sleep(2)
            return self.start_system()
        return False
    
    def get_status(self):
        """Get status of all services"""
        logger.info("Getting system status...")
        try:
            result = subprocess.run([
                "docker-compose", "-f", self.docker_compose_file, "ps"
            ], capture_output=True, text=True, check=True)
            print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get status: {e}")
            return False
    
    def get_logs(self, service: str = None, follow: bool = False):
        """Get logs from services"""
        cmd = ["docker-compose", "-f", self.docker_compose_file, "logs"]
        
        if follow:
            cmd.append("-f")
        
        if service:
            cmd.append(service)
        
        try:
            subprocess.run(cmd, check=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get logs: {e}")
            return False
    
    def scale_clients(self, num_clients: int):
        """Scale the number of client instances"""
        logger.info(f"Scaling clients to {num_clients} instances...")
        try:
            subprocess.run([
                "docker-compose", "-f", self.docker_compose_file, 
                "up", "-d", "--scale", f"client-1={num_clients}"
            ], check=True)
            logger.info(f"Scaled to {num_clients} client instances")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to scale clients: {e}")
            return False
    
    def run_single_client(self, client_id: str, dataset_path: str = None, 
                         server_address: str = "localhost", server_port: int = 50051,
                         threshold: float = 50, epsilon: float = 1.0, 
                         use_privacy: bool = True):
        """Run a single client outside of Docker"""
        logger.info(f"Running single client: {client_id}")
        
        # Import client
        try:
            from federated_client import FederatedLearningClient
        except ImportError as e:
            logger.error(f"Failed to import federated client: {e}")
            return False
        
        # Create and run client
        client = FederatedLearningClient(
            client_id=client_id,
            server_address=server_address,
            server_port=server_port,
            dataset_path=dataset_path,
            min_utility_threshold=threshold,
            epsilon=epsilon
        )
        
        try:
            success = client.run_federated_learning(use_privacy_preserving=use_privacy)
            if success:
                logger.info(f"Client {client_id} completed successfully")
                return True
            else:
                logger.error(f"Client {client_id} failed")
                return False
        finally:
            client.close()
    
    def run_single_server(self, host: str = "0.0.0.0", port: int = 50051,
                         threshold: float = 50, epsilon: float = 1.0, 
                         num_rounds: int = 3):
        """Run a single server outside of Docker"""
        logger.info(f"Running single server on {host}:{port}")
        
        # Import server
        try:
            from federated_server import serve
        except ImportError as e:
            logger.error(f"Failed to import federated server: {e}")
            return False
        
        try:
            serve(
                host=host,
                port=port,
                min_utility_threshold=threshold,
                epsilon=epsilon,
                num_rounds=num_rounds
            )
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
            return True
        except Exception as e:
            logger.error(f"Server error: {e}")
            return False
    
    def monitor_system(self, duration: int = 300):
        """Monitor the system for a specified duration"""
        logger.info(f"Monitoring system for {duration} seconds...")
        
        start_time = time.time()
        while time.time() - start_time < duration:
            try:
                # Get status
                result = subprocess.run([
                    "docker-compose", "-f", self.docker_compose_file, "ps", "--format", "json"
                ], capture_output=True, text=True, check=True)
                
                # Parse status
                services = json.loads(result.stdout)
                running_services = [s for s in services if s.get('State') == 'running']
                
                logger.info(f"Running services: {len(running_services)}/{len(services)}")
                
                # Check server health
                if any('federated-server' in s.get('Service', '') for s in running_services):
                    logger.info("Server is running")
                else:
                    logger.warning("Server is not running")
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(30)
    
    def cleanup(self):
        """Clean up the system and remove containers/images"""
        logger.info("Cleaning up system...")
        try:
            # Stop and remove containers
            subprocess.run([
                "docker-compose", "-f", self.docker_compose_file, "down", "-v", "--rmi", "all"
            ], check=True)
            
            # Remove any dangling images
            subprocess.run([
                "docker", "image", "prune", "-f"
            ], check=True)
            
            logger.info("Cleanup completed")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Cleanup failed: {e}")
            return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Federated Learning System Manager')
    parser.add_argument('command', choices=[
        'build', 'start', 'stop', 'restart', 'status', 'logs', 'scale',
        'run-client', 'run-server', 'monitor', 'cleanup'
    ], help='Command to execute')
    
    # Command-specific arguments
    parser.add_argument('--service', help='Service name for logs command')
    parser.add_argument('--follow', action='store_true', help='Follow logs')
    parser.add_argument('--num-clients', type=int, help='Number of clients for scale command')
    parser.add_argument('--client-id', help='Client ID for run-client command')
    parser.add_argument('--dataset-path', help='Dataset path for run-client command')
    parser.add_argument('--server-address', default='localhost', help='Server address')
    parser.add_argument('--server-port', type=int, default=50051, help='Server port')
    parser.add_argument('--threshold', type=float, default=50, help='Utility threshold')
    parser.add_argument('--epsilon', type=float, default=1.0, help='Privacy budget')
    parser.add_argument('--no-privacy', action='store_true', help='Disable privacy-preserving mining')
    parser.add_argument('--host', default='0.0.0.0', help='Server host for run-server command')
    parser.add_argument('--num-rounds', type=int, default=3, help='Number of federated rounds')
    parser.add_argument('--duration', type=int, default=300, help='Monitoring duration in seconds')
    parser.add_argument('--compose-file', default='docker-compose.yml', help='Docker Compose file')
    
    args = parser.parse_args()
    
    # Create manager
    manager = FederatedSystemManager(args.compose_file)
    
    # Execute command
    if args.command == 'build':
        success = manager.build_images()
    elif args.command == 'start':
        success = manager.start_system()
    elif args.command == 'stop':
        success = manager.stop_system()
    elif args.command == 'restart':
        success = manager.restart_system()
    elif args.command == 'status':
        success = manager.get_status()
    elif args.command == 'logs':
        success = manager.get_logs(args.service, args.follow)
    elif args.command == 'scale':
        if not args.num_clients:
            logger.error("--num-clients is required for scale command")
            sys.exit(1)
        success = manager.scale_clients(args.num_clients)
    elif args.command == 'run-client':
        if not args.client_id:
            logger.error("--client-id is required for run-client command")
            sys.exit(1)
        success = manager.run_single_client(
            client_id=args.client_id,
            dataset_path=args.dataset_path,
            server_address=args.server_address,
            server_port=args.server_port,
            threshold=args.threshold,
            epsilon=args.epsilon,
            use_privacy=not args.no_privacy
        )
    elif args.command == 'run-server':
        success = manager.run_single_server(
            host=args.host,
            port=args.server_port,
            threshold=args.threshold,
            epsilon=args.epsilon,
            num_rounds=args.num_rounds
        )
    elif args.command == 'monitor':
        manager.monitor_system(args.duration)
        success = True
    elif args.command == 'cleanup':
        success = manager.cleanup()
    else:
        logger.error(f"Unknown command: {args.command}")
        sys.exit(1)
    
    if not success:
        sys.exit(1)

if __name__ == '__main__':
    main() 