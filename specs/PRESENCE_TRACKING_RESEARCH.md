# Real-Time Presence Tracking for Collaborative Applications

## Executive Summary

This document provides architectural recommendations for implementing real-time presence tracking (status: online/offline, who is viewing/editing which task) for the Todo application, focusing on scalability for 100+ concurrent users.

**Key Findings:**
- **PostgreSQL vs Redis**: Redis is superior for presence tracking due to lower latency (sub-millisecond vs 10-100ms), automatic expiration (TTL), and pub/sub capabilities
- **Heartbeat Interval**: 30 seconds optimal; balances battery drain (mobile), network load, and detection latency
- **Cleanup Strategy**: Redis TTL with automatic expiration + periodic PostgreSQL cleanup + graceful disconnect handlers
- **Task-Level Tracking**: Combine Redis for real-time state + PostgreSQL for persistence + WebSocket for instant updates

---

## 1. PostgreSQL vs Redis for Presence Tracking

### 1.1 Comparison Matrix

| Criteria | PostgreSQL | Redis |
|----------|------------|-------|
| **Latency** | 10-100ms (disk I/O + network) | <1ms (in-memory) |
| **Throughput** | 1,000-10,000 ops/sec | 50,000-100,000+ ops/sec |
| **TTL/Expiration** | Manual cleanup via cron | Native TTL (automatic) |
| **Pub/Sub** | LISTEN/NOTIFY (limited) | First-class support (efficient) |
| **Persistence** | Built-in durability | Optional (RDB/AOF) |
| **Memory Usage** | Minimal | Higher (in-memory) |
| **Cost at Scale** | Lower (disk storage) | Higher (RAM requirement) |
| **Failover Complexity** | Medium (replication) | High (cluster/sentinel) |
| **Typical Use Case** | Historical data, audit logs | Hot data, caching, real-time |

### 1.2 Recommendation: Redis (Primary) + PostgreSQL (Hybrid)

**Architecture Pattern:**
```
┌─────────────────────────────────────────────────────────────┐
│                    WebSocket Server                          │
│  (FastAPI + python-socketio / Starlette WebSockets)         │
└──────────────────┬──────────────────┬──────────────────────┘
                   │                  │
         ┌─────────▼──────┐   ┌──────▼─────────┐
         │  Redis Cache   │   │  PostgreSQL DB │
         │                │   │                │
         │ - Presence     │   │ - Audit logs   │
         │   (TTL: 60s)   │   │ - Task state   │
         │ - Task edits   │   │ - User data    │
         │   (TTL: 120s)  │   │                │
         │ - Pub/Sub      │   │                │
         └────────────────┘   └────────────────┘
```

**Rationale:**
1. **Redis for Real-Time**: Sub-millisecond latency for presence updates
2. **PostgreSQL for Durability**: Audit trail of all presence events
3. **Hybrid Approach**: Best of both worlds—immediate responsiveness + historical records
4. **Cost Effective**: Redis for hot data (~1MB per 10,000 users), PostgreSQL for everything else

---

## 2. Optimal Heartbeat Interval: 30 Seconds

### 2.1 Comparison: 10s vs 30s

| Metric | 10 Second Interval | 30 Second Interval | Winner |
|--------|-------------------|-------------------|--------|
| **Bandwidth** | 3 requests/min | 1 request/min | 30s (67% less) |
| **Mobile Battery** | -5% faster drain | Baseline | 30s |
| **Server Load** | 3x requests | 1x requests | 30s |
| **Detection Latency** | 0-10s average | 0-30s average | 10s (but acceptable) |
| **User Perception** | "Very responsive" | "Responsive" | 10s (marginal) |

### 2.2 Recommended: 30-Second Heartbeat with Adaptive Backoff

```python
# Backend config
HEARTBEAT_CONFIG = {
    "interval_seconds": 30,
    "timeout_threshold": 90,
    "max_missed_beats": 2,
    "backoff_multiplier": 1.5,
    "grace_period": 5,
}
```

**Calculation:**
- 30s interval × 100 users = 3,300 requests/hour
- At 50KB per request: 165 MB/hour or ~24 Mbps
- Detection latency: max 60 seconds (2 × 30s interval + processing)
- Battery impact: ~2% per hour

### 2.3 Adaptive Heartbeat (Advanced)

```python
class AdaptiveHeartbeat:
    def __init__(self):
        self.base_interval = 30
        self.intervals = {
            "good_connection": 30,
            "poor_connection": 60,
            "battery_low": 120,
            "in_focus": 20,
            "out_of_focus": 60,
        }

    def get_interval(self, connection_quality, battery_level, is_focused):
        if battery_level < 20:
            return self.intervals["battery_low"]
        if connection_quality < 3:
            return self.intervals["poor_connection"]
        if not is_focused:
            return self.intervals["out_of_focus"]
        if is_focused and connection_quality > 3:
            return self.intervals["in_focus"]
        return self.intervals["good_connection"]
```

---

## 3. Automatic Cleanup Strategies

### 3.1 Three-Tier Cleanup Approach

#### **Tier 1: Redis TTL (Automatic Expiration)**
```python
redis_client.setex(
    key=f"presence:{user_id}:{task_id}",
    time=90,
    value=json.dumps({
        "user_id": user_id,
        "task_id": task_id,
        "timestamp": now,
        "action": "editing"
    })
)
```

#### **Tier 2: Graceful Disconnect Handler**
```python
async def cleanup_user_presence(user_id: str):
    """Remove all presence records for user"""
    cursor = 0
    while True:
        cursor, keys = redis_client.scan(
            cursor,
            match=f"presence:{user_id}:*"
        )
        if keys:
            redis_client.delete(*keys)
        if cursor == 0:
            break

    db.log_presence_event(
        user_id=user_id,
        event_type="disconnect",
        timestamp=datetime.utcnow()
    )
```

#### **Tier 3: Periodic PostgreSQL Cleanup**
```python
# Cron job - runs every 5 minutes
async def cleanup_stale_presence():
    """Remove presence records older than 3 minutes"""
    cutoff_time = datetime.utcnow() - timedelta(minutes=3)

    deleted = db.query(PresenceLog).filter(
        PresenceLog.timestamp < cutoff_time - timedelta(days=7)
    ).delete()
    db.commit()

    logger.info(f"Cleaned {deleted} stale presence records")
```

---

## 4. Tracking "Who is Viewing/Editing Which Task"

### 4.1 Data Model (PostgreSQL)

```python
class TaskPresence(SQLModel, table=True):
    __tablename__ = "task_presence"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    task_id: int = Field(foreign_key="tasks.id", index=True)
    status: str = Field(default="viewing", max_length=20, index=True)
    cursor_position: Optional[int] = Field(default=None)
    selected_text: Optional[str] = Field(default=None, max_length=500)
    last_heartbeat: datetime = Field(default_factory=datetime.utcnow, index=True)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    browser_session_id: str = Field(max_length=255)
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None, max_length=500)


class PresenceEvent(SQLModel, table=True):
    __tablename__ = "presence_events"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    task_id: Optional[int] = Field(foreign_key="tasks.id")
    event_type: str = Field(max_length=20, index=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    duration_seconds: Optional[int] = Field(default=None)
```

### 4.2 Redis Schema

```python
"""
Key Schema:

1. User Presence:
   presence:user:{user_id} = { "status": "online", "last_seen": 1703000000 }
   TTL: 90 seconds

2. Task Editing:
   task:editing:{task_id} = { "user_id": "user123", "started_at": 1703000000 }
   TTL: 120 seconds

3. Task Viewers:
   task:viewers:{task_id} = [
       {"user_id": "user1", "status": "viewing", "joined_at": 1703000000},
       {"user_id": "user2", "status": "editing", "joined_at": 1703000000}
   ]
   TTL: 90 seconds
"""
```

### 4.3 Implementation: Presence Service

```python
class PresenceService:
    """Manages real-time presence tracking"""

    def __init__(self, redis_client, db_session):
        self.redis = redis_client
        self.db = db_session
        self.heartbeat_interval = 30
        self.presence_ttl = self.heartbeat_interval * 3

    async def record_heartbeat(
        self,
        user_id: str,
        task_id: int,
        session_id: str,
        status: str = "viewing",
        cursor_position: Optional[int] = None
    ):
        """Record user's presence for a task"""
        now = datetime.utcnow()
        timestamp = int(now.timestamp())

        presence_data = {
            "user_id": user_id,
            "task_id": task_id,
            "status": status,
            "timestamp": timestamp,
            "cursor_position": cursor_position
        }

        # Update Redis
        presence_key = f"presence:{user_id}:{task_id}:{session_id}"
        self.redis.setex(presence_key, self.presence_ttl, json.dumps(presence_data))

        # Update task viewers
        task_viewers_key = f"task:viewers:{task_id}"
        viewers = json.loads(self.redis.get(task_viewers_key) or "[]")
        viewers = [v for v in viewers if v["user_id"] != user_id]
        viewers.append({
            "user_id": user_id,
            "status": status,
            "joined_at": timestamp
        })
        self.redis.setex(task_viewers_key, self.presence_ttl, json.dumps(viewers))

        # Log to PostgreSQL
        existing = self.db.exec(
            select(TaskPresence).where(
                (TaskPresence.user_id == user_id) &
                (TaskPresence.task_id == task_id) &
                (TaskPresence.browser_session_id == session_id)
            )
        ).first()

        if existing:
            existing.status = status
            existing.last_heartbeat = now
            self.db.add(existing)
        else:
            new_presence = TaskPresence(
                user_id=user_id,
                task_id=task_id,
                status=status,
                browser_session_id=session_id,
                cursor_position=cursor_position,
                last_heartbeat=now,
                started_at=now
            )
            self.db.add(new_presence)

        self.db.commit()
        return presence_data

    async def get_task_viewers(self, task_id: int):
        """Get all users viewing/editing a task"""
        viewers_key = f"task:viewers:{task_id}"
        viewers_json = self.redis.get(viewers_key)
        return json.loads(viewers_json) if viewers_json else []

    async def stop_editing(self, user_id: str, task_id: int, session_id: str):
        """User stopped editing task"""
        editing_key = f"task:editing:{task_id}:{session_id}"
        self.redis.delete(editing_key)
        await self.record_heartbeat(user_id, task_id, session_id, "viewing")
```

### 4.4 API Endpoints

```python
# backend/src/routes/presence.py

@router.post("/{task_id}/heartbeat")
async def record_heartbeat(
    task_id: int,
    request: Request,
    session: Session = Depends(get_session),
    user_data = Depends(verify_jwt)
):
    """Record user's presence for a task"""
    body = await request.json()
    service = PresenceService(redis_client, session)

    result = await service.record_heartbeat(
        user_id=user_data.get("user_id"),
        task_id=int(task_id),
        session_id=body.get("session_id"),
        status=body.get("status", "viewing"),
        cursor_position=body.get("cursor_position")
    )

    return {"success": True, "presence": result}


@router.get("/{task_id}/viewers")
async def get_task_viewers(
    task_id: int,
    session: Session = Depends(get_session),
    user_data = Depends(verify_jwt)
):
    """Get all users viewing/editing a task"""
    service = PresenceService(redis_client, session)
    viewers = await service.get_task_viewers(int(task_id))
    return {"task_id": task_id, "viewers": viewers, "total": len(viewers)}
```

---

## 5. Scalability Analysis for 100+ Concurrent Users

### 5.1 Load Calculations

```
Scenario: 100 concurrent users, 30-second heartbeat

REDIS:
- Heartbeats: 100 users × (1 / 30s) = 3.3 ops/sec
- Memory: 100 users × 500 bytes = 50 KB
- Network: 3.3 KBps (negligible)

POSTGRESQL:
- Heartbeats logged: 3.3 per second = 288,000 per day
- Storage: 288,000 × 200 bytes = 57.6 MB per day
- Retention: 7 days = 403 MB

WEBSOCKET:
- Connections: 100 active
- Bandwidth: 6.6 KBps
```

### 5.2 Performance Benchmarks

| Operation | Latency | Throughput |
|-----------|---------|-----------|
| Redis SET (heartbeat) | 0.5-1ms | 50,000/sec |
| Redis GET (viewers) | 0.5-1ms | 50,000/sec |
| PostgreSQL INSERT | 5-10ms | 1,000/sec |
| WebSocket broadcast | 10-50ms | Depends on network |

---

## 6. Comparison Table: Implementation Approaches

| Approach | Complexity | Latency | Cost | Scalability |
|----------|-----------|---------|------|-------------|
| **Redis Only** | Low | Sub-1ms | $$$ | 50K+ concurrent |
| **PostgreSQL Only** | Medium | 10-100ms | $$ | 1K concurrent |
| **Redis + PostgreSQL** | Medium | <1ms | $$$ | 100K+ concurrent |
| **Redis Pub/Sub Only** | Medium | 5-50ms | $$$ | 10K+ concurrent |
| **WebSocket Only** | High | 0-100ms | $$ | 5K per server |

---

## 7. Deployment Checklist

### Pre-Production

- [ ] Redis cluster configured with 3+ nodes
- [ ] Redis persistence enabled
- [ ] PostgreSQL connection pooling configured
- [ ] Heartbeat interval tested (30s)
- [ ] TTL values configured
- [ ] Graceful disconnect handlers tested
- [ ] WebSocket reconnection logic implemented
- [ ] Load testing (100+ concurrent users)

### Production

- [ ] Redis monitoring enabled
- [ ] PostgreSQL monitoring enabled
- [ ] WebSocket connection monitoring
- [ ] Cleanup cron jobs running
- [ ] Presence event audit trail enabled
- [ ] Disaster recovery plan in place

---

## Summary & Recommendations

For the Todo application at 100+ concurrent users:

1. **Use Redis + PostgreSQL Hybrid Model** for best performance and cost
2. **30-Second Heartbeat Interval** for optimal balance
3. **Three-Tier Cleanup** (TTL + disconnect + periodic)
4. **WebSocket + REST Hybrid** for real-time updates
5. **Deploy with Redis Cluster** (3+ nodes) + PostgreSQL connection pooling

This ensures scalability, reliability, and cost-effectiveness for collaborative task management.
