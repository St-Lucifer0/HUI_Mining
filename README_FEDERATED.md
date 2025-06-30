# Federated Learning System for High-Utility Itemset Mining

This project extends your existing FP-Growth implementation for High-Utility Itemset Mining (HUIM) into a federated learning system using gRPC and Docker. The system allows multiple devices to collaboratively mine high-utility itemsets while preserving data privacy.

## Architecture Overview

```
┌─────────────────┐    gRPC    ┌─────────────────┐
│   Client 1      │ ────────── │                 │
│ (Device/Laptop) │            │                 │
└─────────────────┘            │   Federated     │
                               │    Server       │
┌─────────────────┐            │                 │
│   Client 2      │ ────────── │                 │
│ (Device/Laptop) │            │                 │
└─────────────────┘            └─────────────────┘
                               │                 │
┌─────────────────┐            │                 │
│   Client 3      │ ────────── │                 │
│ (Device/Laptop) │            │                 │
└─────────────────┘            └─────────────────┘
```

## Features

- **Federated Learning**: Multiple clients collaborate without sharing raw data
- **Privacy Preservation**: Differential privacy and secure computation
- **gRPC Communication**: Fast, efficient communication between clients and server
- **Docker Containerization**: Easy deployment and scaling
- **High-Utility Itemset Mining**: Your existing FP-Growth algorithm
- **Real-time Monitoring**: System health and performance monitoring

## Prerequisites

- Docker and Docker Compose
- Python 3.9+
- Your existing FP-Growth codebase

## Quick Start

### 1. Build and Start the System

```bash
# Build Docker images
python run_federated_system.py build

# Start the entire system
python run_federated_system.py start
```

This will start:
- 1 federated learning server
- 3 client instances with different configurations
- 1 monitoring service

### 2. Monitor the System

```bash
# Check system status
python run_federated_system.py status

# View logs
python run_federated_system.py logs

# Follow logs in real-time
python run_federated_system.py logs --follow
```

### 3. Stop the System

```bash
python run_federated_system.py stop
```

## Detailed Usage

### Running Individual Components

#### Start Server Only
```bash
python run_federated_system.py run-server --host 0.0.0.0 --port 50051 --threshold 50 --epsilon 1.0
```

#### Run Single Client
```bash
python run_federated_system.py run-client \
    --client-id client-1 \
    --dataset-path ./foodmart_dataset_csv.csv \
    --server-address localhost \
    --server-port 50051 \
    --threshold 50 \
    --epsilon 1.0
```

#### Scale Clients
```bash
# Scale to 5 client instances
python run_federated_system.py scale --num-clients 5
```

### Docker Commands

#### Build Images
```bash
docker-compose build
```

#### Start Services
```bash
docker-compose up -d
```

#### View Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs federated-server
docker-compose logs client-1

# Follow logs
docker-compose logs -f
```

#### Stop Services
```bash
docker-compose down
```

## Configuration

### Environment Variables

#### Server Configuration
- `MIN_UTILITY_THRESHOLD`: Minimum utility threshold for itemsets (default: 50)
- `EPSILON`: Privacy budget for differential privacy (default: 1.0)
- `NUM_ROUNDS`: Number of federated learning rounds (default: 3)

#### Client Configuration
- `CLIENT_ID`: Unique identifier for the client
- `SERVER_ADDRESS`: Address of the federated server
- `SERVER_PORT`: Port of the federated server (default: 50051)
- `DATASET_PATH`: Path to local dataset file
- `THRESHOLD`: Local utility threshold
- `EPSILON`: Local privacy budget
- `USE_PRIVACY`: Enable privacy-preserving mining (true/false)

### Docker Compose Configuration

The `docker-compose.yml` file defines:

1. **federated-server**: The central aggregation server
2. **client-1**: Client using FoodMart dataset with privacy
3. **client-2**: Client using sample data with different parameters
4. **client-3**: Client using sample data without privacy
5. **monitoring**: Optional monitoring service

## API Reference

### gRPC Service

The federated learning system uses the following gRPC service:

```protobuf
service FederatedLearningService {
  rpc RegisterClient (ClientRegistration) returns (RegistrationResponse);
  rpc SendLocalResults (LocalResults) returns (ServerAcknowledgment);
  rpc GetGlobalResults (GlobalResultsRequest) returns (GlobalResults);
  rpc BroadcastGlobalModel (GlobalModel) returns (ClientAcknowledgment);
  rpc HealthCheck (HealthRequest) returns (HealthResponse);
}
```

### Key Messages

- `ClientRegistration`: Client registration information
- `LocalResults`: Local mining results from clients
- `GlobalResults`: Aggregated results from server
- `HighUtilityItemset`: Individual high-utility itemset

## Privacy and Security

### Differential Privacy
- Laplace noise is added to utility values
- Privacy budget is tracked and managed
- Configurable epsilon values per client

### Secure Communication
- gRPC provides encrypted communication
- Optional data encryption for sensitive information
- Session-based authentication

### Data Isolation
- Raw transaction data never leaves client devices
- Only aggregated results are shared
- Local computation preserves data privacy

## Monitoring and Logging

### System Monitoring
```bash
# Monitor system for 10 minutes
python run_federated_system.py monitor --duration 600
```

### Log Files
Logs are stored in the `./logs` directory:
- Server logs: `federated-server.log`
- Client logs: `client-*.log`
- System logs: `system.log`

### Health Checks
- Automatic health checks every 30 seconds
- Service restart on failure
- Real-time status monitoring

## Performance Optimization

### Scaling
- Horizontal scaling of client instances
- Load balancing across multiple clients
- Configurable resource limits

### Caching
- Local result caching on clients
- Server-side aggregation caching
- Optimized data structures

### Network Optimization
- gRPC streaming for large datasets
- Compression for network efficiency
- Connection pooling

## Troubleshooting

### Common Issues

1. **Connection Refused**
   ```bash
   # Check if server is running
   python run_federated_system.py status
   
   # Restart server
   python run_federated_system.py restart
   ```

2. **Client Registration Failed**
   ```bash
   # Check server logs
   python run_federated_system.py logs federated-server
   
   # Verify client configuration
   docker-compose logs client-1
   ```

3. **Docker Build Failures**
   ```bash
   # Clean and rebuild
   python run_federated_system.py cleanup
   python run_federated_system.py build
   ```

### Debug Mode
```bash
# Run with debug logging
docker-compose up --build --force-recreate
```

## Development

### Adding New Clients
1. Add client service to `docker-compose.yml`
2. Configure environment variables
3. Set appropriate dependencies

### Extending the Protocol
1. Modify `federated_learning.proto`
2. Regenerate gRPC code
3. Update server and client implementations

### Custom Algorithms
1. Extend `FederatedLearningClient` class
2. Implement custom mining algorithms
3. Add new message types to protobuf

## File Structure

```
├── federated_learning.proto          # gRPC service definition
├── federated_learning_pb2.py         # Generated protobuf code
├── federated_learning_pb2_grpc.py    # Generated gRPC code
├── federated_server.py               # Federated learning server
├── federated_client.py               # Federated learning client
├── run_federated_system.py           # System management utility
├── Dockerfile.server                 # Server Docker image
├── Dockerfile.client                 # Client Docker image
├── docker-compose.yml                # System orchestration
├── requirements.txt                  # Python dependencies
├── README_FEDERATED.md               # This file
└── logs/                             # Log files directory
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project extends your existing FP-Growth implementation. Please ensure compliance with the original license terms.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review logs for error messages
3. Open an issue with detailed information
4. Provide system configuration and error logs 