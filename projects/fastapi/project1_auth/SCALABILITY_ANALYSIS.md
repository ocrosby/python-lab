# Scalability Analysis

## Performance Profiling Results

### Critical Performance Issues

#### 1. **PASSWORD HASHING - MAJOR BOTTLENECK** 🔴
- **Time**: ~193ms per hash operation
- **Total**: 1.93 seconds for 10 operations
- **Impact**: Blocks application during registration and login
- **Scaling Problem**: As user load increases, password operations will create severe bottlenecks

**Recommendation**: 
- Move password hashing to background workers using Celery/Redis
- Use async password verification with `asyncio.to_thread()` to prevent blocking
- Consider reducing bcrypt work factor from default (likely 12) to 10 for acceptable security with better performance

```python
# Current (blocking):
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

# Recommended (non-blocking):
import asyncio
hashed = await asyncio.to_thread(bcrypt.hashpw, password.encode(), bcrypt.gensalt())
```

#### 2. **PASSWORD VERIFICATION - MAJOR BOTTLENECK** 🔴
- **Time**: ~193ms per verification
- **Total**: 1.93 seconds for 10 verifications  
- **Impact**: Every login request will take ~200ms just for password checking
- **Scaling Problem**: With 1000 concurrent logins, you'll need 193 seconds of CPU time

**Recommendation**:
- Use async password verification with `asyncio.to_thread()`
- Implement rate limiting on login endpoints (already critical for security)
- Consider caching recent successful authentication tokens (with short TTL)

#### 3. **TOKEN OPERATIONS - ACCEPTABLE** ✅
- **Time**: 0.1ms per encode+decode cycle
- **Total**: 0.001 seconds for 10 operations
- **Impact**: Minimal
- **Scaling**: JWT operations are fast and won't be a bottleneck

---

## Database Architecture Issues

### Current Connection Pool Configuration
```python
DB_POOL_MIN_CONN=1
DB_POOL_MAX_CONN=10
```

#### Issues Identified:

1. **Connection Pool Size Too Small** 🟡
   - Max 10 connections will limit throughput under load
   - Recommendation: Increase to 20-50 based on expected concurrent users
   - Formula: `max_connections = (2 × CPU_cores) + disk_spindles`

2. **No Connection Pool Monitoring** 🟡
   - No visibility into pool exhaustion
   - Recommendation: Add connection pool metrics and logging

3. **Repository Pattern Not Using Connection Pooling Efficiently** 🟡
   - Every operation gets/returns a connection
   - For multi-step operations, this creates overhead
   - Current implementation at `repository.py:36-54`

```python
@contextmanager
def transaction(self):
    conn = self.get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        self.return_connection(conn)
```

**Issue**: Connection acquired for entire transaction duration, not released until complete. Under high load, this can starve the pool.

---

## Identified Scaling Problems

### 1. **Synchronous I/O Throughout** 🔴
- FastAPI supports async but all repository operations are synchronous
- Every database call blocks a worker thread
- Files: `repository.py`, `auth_service.py`, `service.py`

**Impact**: 
- Limited concurrent request handling
- Poor resource utilization
- Worker threads will be blocked waiting on I/O

**Recommendation**:
- Use `asyncpg` instead of `psycopg2` for async database operations
- Convert all repositories to async
- Use `async def` in service layer
- Migrate from `psycopg2.pool.SimpleConnectionPool` to `asyncpg.create_pool()`

### 2. **No Caching Layer** 🟡
- Every request hits the database
- No caching for frequently accessed data (user profiles, tokens)
- Refresh token lookups query database every time

**Recommendation**:
- Add Redis for session/token caching
- Cache user objects after authentication
- Implement cache-aside pattern for user lookups

### 3. **Missing Database Indexes** 🟠
Current indexes (from `repository.py:351-353`):
```python
CREATE INDEX IF NOT EXISTS idx_token ON refresh_tokens(token)
CREATE INDEX IF NOT EXISTS idx_user_id ON refresh_tokens(user_id)
CREATE INDEX IF NOT EXISTS idx_token_family ON refresh_tokens(token_family)
```

**Missing indexes**:
- No index on `users.email` (lookup happens during registration check)
- No index on `users.username` (lookup happens on every login)
- No composite index on `refresh_tokens(user_id, revoked)` for user token revocation queries

**Recommendation**:
```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_refresh_tokens_user_revoked ON refresh_tokens(user_id, revoked);
CREATE INDEX idx_refresh_tokens_expires_at ON refresh_tokens(expires_at) WHERE NOT revoked;
```

### 4. **No Request Rate Limiting** 🔴
- Authentication endpoints have no rate limiting
- Vulnerable to brute force attacks
- Will consume resources under attack

**Recommendation**:
- Add `slowapi` or similar rate limiting middleware
- Implement per-IP and per-user rate limits
- Add exponential backoff for failed login attempts

### 5. **No Background Task Processing** 🟡
- Expired token cleanup runs synchronously (if called)
- No automated cleanup of stale data
- Repository method `delete_expired()` exists but is never called

**Recommendation**:
- Add Celery or FastAPI BackgroundTasks for:
  - Periodic cleanup of expired refresh tokens
  - Email sending (if implemented)
  - Password hashing during registration
  
### 6. **Global Connection Pool State** 🟠
From `dependencies.py:14-15`:
```python
_connection_pool: Optional[pool.SimpleConnectionPool] = None
_connection_manager: Optional[ConnectionManager] = None
```

**Issues**:
- Global mutable state makes testing harder
- Not thread-safe if pool initialization races
- Difficult to mock in tests

**Recommendation**: Already using dependency injection well, but consider moving pool to app state:
```python
@asynccontextmanager
async def lifespan_context(app):
    app.state.pool = await create_async_pool()
    yield
    await app.state.pool.close()
```

### 7. **No Health Check Database Testing** 🟡
- Health endpoints exist but don't test database connectivity
- Can't detect database connection issues until requests fail
- From `routers/health.py` - only returns static responses

**Recommendation**:
```python
@router.get("/readiness")
async def readiness(db: Annotated[Connection, Depends(get_db)]):
    await db.execute("SELECT 1")
    return {"status": "ready"}
```

---

## Architecture Recommendations for Scale

### Priority 1 (Critical - Do Immediately)
1. ✅ **Make password operations async** - Prevents blocking under load
2. ✅ **Add database indexes** - 10-100x query performance improvement
3. ✅ **Add rate limiting** - Prevents resource exhaustion

### Priority 2 (High - Within 1 Sprint)
1. ✅ **Migrate to async database driver** (asyncpg)
2. ✅ **Add Redis caching layer** for auth tokens and user sessions
3. ✅ **Increase connection pool size** to 20-50 connections
4. ✅ **Add connection pool monitoring/metrics**

### Priority 3 (Medium - Within 2 Sprints)
1. ✅ **Add background task processing** (Celery or FastAPI BackgroundTasks)
2. ✅ **Implement token cleanup scheduler**
3. ✅ **Add health checks with database connectivity tests**
4. ✅ **Add metrics/monitoring** (Prometheus, Datadog, etc.)

### Priority 4 (Nice to Have)
1. ✅ **Add database read replicas** for read-heavy operations
2. ✅ **Implement query result caching**
3. ✅ **Add database query logging/profiling** to identify slow queries
4. ✅ **Consider connection pooling at PgBouncer level** for better resource management

---

## Load Testing Recommendations

Before deploying to production, run load tests with:
- **Locust** or **k6** for HTTP load testing
- Test scenarios:
  - 100 concurrent users registering
  - 1000 concurrent users logging in
  - 5000 requests/second to authenticated endpoints
  - Token refresh under load

Monitor:
- Response time percentiles (p50, p95, p99)
- Database connection pool exhaustion
- CPU utilization during password hashing
- Memory usage growth

---

## Conclusion

The application architecture is well-structured with good separation of concerns (DI, repository pattern, service layer). However, **password hashing is the critical bottleneck** that will prevent scaling. The synchronous I/O model and missing indexes are secondary concerns that should be addressed before production deployment.

**Estimated Current Capacity**: ~50-100 concurrent users
**With Recommended Changes**: 1000-5000 concurrent users (depending on hardware)

The current DI setup using FastAPI's `Depends()` is sufficient and does not require a full DI container at this scale.
