# Terminal Organization Guide

## Recommended: 4 Parallel Terminals

### Terminal 1: Service Monitoring
```bash
cd /mnt/d/ai-agents
./system_status.sh
docker logs -f optimistic_matsumoto
```

### Terminal 2: Development & Testing
```bash
cd /mnt/d/ai-agents
python test_light_processor.py
curl http://localhost:5008/v1/health_check
curl http://localhost:5007/v1/health_check
```

### Terminal 3: Document Processing
```bash
cd /mnt/d/ai-agents
python simple_index.py
python create_real_embeddings.py
```

### Terminal 4: Service Management
```bash
cd /mnt/d/ai-agents
./restart_system.sh
docker-compose up -d
```

## Benefits:
- ✅ Real-time service monitoring
- ✅ Immediate error detection
- ✅ Better debugging workflow
- ✅ Parallel development
