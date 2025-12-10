# OAuth2 Refresh Token Implementation

## Overview

Complete OAuth2 refresh token flow with token rotation and security best practices implemented.

**Status**: ✅ Production-Ready

---

## Features Implemented

### 1. Token Rotation ✅
- Old refresh token revoked when used
- New refresh token issued with each refresh
- Prevents token replay attacks

### 2. Token Family Tracking ✅
- Tokens grouped by family
- Detects stolen tokens
- Revokes entire family if theft detected

### 3. Long-Lived Refresh Tokens ✅
- Default: 7 days (configurable)
- Stored securely in database
- Can be revoked at any time

### 4. Short-Lived Access Tokens ✅
- Default: 30 minutes (configurable)
- Stateless JWT tokens
- Must be refreshed using refresh token

---

## API Endpoints

### POST /api/v1/auth/token (Updated)
**Description**: Login and get both access + refresh tokens

**Request**:
```http
POST /api/v1/auth/token
Content-Type: application/x-www-form-urlencoded

username=testuser&password=password123
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "9vwHO7FXlPZ-NM8uQj3...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### POST /api/v1/auth/refresh (New)
**Description**: Exchange refresh token for new access token

**Request**:
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "9vwHO7FXlPZ-NM8uQj3..."
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "kL2mP9qRs4tUv5wX6...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Behavior**:
- Old refresh token is revoked
- New refresh token issued (token rotation)
- Returns new access token
- If old token reused → entire token family revoked (theft detection)

### POST /api/v1/auth/revoke (New)
**Description**: Manually revoke a refresh token (logout)

**Request**:
```http
POST /api/v1/auth/revoke
Content-Type: application/json

{
  "refresh_token": "9vwHO7FXlPZ-NM8uQj3..."
}
```

**Response**:
```http
204 No Content
```

---

## Database Schema

### refresh_tokens Table

```sql
CREATE TABLE refresh_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(512) UNIQUE NOT NULL,
    token_family VARCHAR(64) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    revoked BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_token ON refresh_tokens(token);
CREATE INDEX idx_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_token_family ON refresh_tokens(token_family);
```

**Fields**:
- `id`: Primary key
- `user_id`: Foreign key to users table
- `token`: Unique refresh token (64 bytes, URL-safe)
- `token_family`: Groups related tokens for theft detection
- `expires_at`: Token expiration timestamp
- `created_at`: Token creation timestamp
- `revoked`: Boolean flag for manual revocation

---

## Security Features

### 1. Token Rotation
Every time a refresh token is used, it's revoked and a new one is issued.

```python
def refresh_access_token(self, refresh_token: str) -> Tuple[str, str]:
    # Get stored token
    stored_token = self._refresh_token_repository.get_by_token(refresh_token)
    
    # Revoke old token
    self._refresh_token_repository.revoke_by_token(refresh_token)
    
    # Issue new tokens
    new_access_token = self.create_access_token(...)
    new_refresh_token = self.create_refresh_token(user.id, stored_token.token_family)
    
    return new_access_token, new_refresh_token
```

### 2. Token Theft Detection
If a revoked refresh token is reused, the entire token family is revoked.

```python
if stored_token.revoked:
    # Token already used - possible theft!
    self._refresh_token_repository.revoke_family(stored_token.token_family)
    raise InvalidRefreshTokenException("Token theft detected")
```

### 3. Token Expiration
Tokens automatically expire after configured time.

```python
if stored_token.expires_at < datetime.utcnow():
    raise InvalidRefreshTokenException("Refresh token has expired")
```

### 4. User Status Validation
Inactive users cannot refresh tokens.

```python
if not user.is_active:
    raise AuthenticationException("User is inactive")
```

---

## Configuration

### Environment Variables

```bash
# Access token lifetime (in minutes)
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Refresh token lifetime (in days)
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Settings Class

```python
class Settings(BaseSettings):
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
```

---

## Usage Examples

### 1. Login and Get Tokens

```python
import httpx

# Login
response = httpx.post(
    "http://localhost:8000/api/v1/auth/token",
    data={"username": "testuser", "password": "password123"}
)

tokens = response.json()
access_token = tokens["access_token"]
refresh_token = tokens["refresh_token"]
```

### 2. Use Access Token

```python
# Access protected endpoint
response = httpx.get(
    "http://localhost:8000/api/v1/items",
    headers={"Authorization": f"Bearer {access_token}"}
)
```

### 3. Refresh Access Token

```python
# When access token expires, use refresh token
response = httpx.post(
    "http://localhost:8000/api/v1/auth/refresh",
    json={"refresh_token": refresh_token}
)

new_tokens = response.json()
access_token = new_tokens["access_token"]
refresh_token = new_tokens["refresh_token"]  # New refresh token!
```

### 4. Logout (Revoke Token)

```python
# Explicitly revoke refresh token
httpx.post(
    "http://localhost:8000/api/v1/auth/revoke",
    json={"refresh_token": refresh_token}
)
```

---

## Client Implementation Guide

### Recommended Token Storage

**Web (Browser)**:
```javascript
// Store access token in memory (not localStorage)
let accessToken = response.data.access_token;

// Store refresh token in httpOnly cookie (server-side)
// OR in secure storage if SPA
```

**Mobile**:
```
- Access token: In-memory only
- Refresh token: Secure keychain/keystore
```

### Automatic Token Refresh

```javascript
// Intercept 401 responses
axios.interceptors.response.use(
  response => response,
  async error => {
    if (error.response.status === 401) {
      // Try to refresh token
      const newTokens = await refreshAccessToken();
      
      // Retry original request with new token
      error.config.headers['Authorization'] = `Bearer ${newTokens.access_token}`;
      return axios.request(error.config);
    }
    return Promise.reject(error);
  }
);
```

---

## Security Best Practices

### ✅ Implemented

1. **Token Rotation**: Old tokens revoked on use
2. **Token Family Tracking**: Detects token theft
3. **Automatic Expiration**: Tokens have time limits
4. **Secure Token Generation**: Uses `secrets.token_urlsafe()`
5. **Database Storage**: Refresh tokens stored securely
6. **User Validation**: Checks user status on refresh
7. **Revocation Support**: Manual logout capability

### 🔒 Additional Recommendations

1. **HTTPS Only**: Always use HTTPS in production
2. **Rate Limiting**: Limit refresh endpoint calls
3. **Token Cleanup**: Periodically delete expired tokens
4. **Audit Logging**: Log token refresh/revoke events
5. **IP Validation**: Optionally bind tokens to IP
6. **Device Tracking**: Track tokens by device

---

## Repository Methods

### RefreshTokenRepository

```python
class RefreshTokenRepository(ABC):
    def create(user_id, token, token_family, expires_at) -> RefreshTokenInDB
    def get_by_token(token) -> Optional[RefreshTokenInDB]
    def revoke_by_token(token) -> bool
    def revoke_all_for_user(user_id) -> int
    def revoke_family(token_family) -> int
    def delete_expired() -> int
```

### AuthService

```python
class AuthService:
    def create_refresh_token(user_id, token_family) -> str
    def create_token_pair(user) -> Tuple[str, str, str]
    def refresh_access_token(refresh_token) -> Tuple[str, str]
    def revoke_refresh_token(refresh_token) -> bool
    def revoke_all_user_tokens(user_id) -> int
```

---

## Error Handling

### InvalidRefreshTokenException

Raised when:
- Token not found in database
- Token has been revoked (theft detected)
- Token has expired
- Token is invalid format

**Response**: `401 Unauthorized`

```json
{
  "detail": "Refresh token has been revoked (possible token theft detected)"
}
```

---

## Testing

### Manual Testing

```bash
# 1. Login
TOKEN_RESPONSE=$(curl -X POST http://localhost:8000/api/v1/auth/token \
  -d "username=testuser&password=password123")

ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.access_token')
REFRESH_TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.refresh_token')

# 2. Use access token
curl http://localhost:8000/api/v1/items \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# 3. Refresh token
NEW_TOKENS=$(curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}")

# 4. Try reusing old token (should fail - theft detection)
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}"
# Expected: 401 Unauthorized

# 5. Revoke token (logout)
curl -X POST http://localhost:8000/api/v1/auth/revoke \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}"
```

---

## Migration Notes

### Breaking Changes

The `/api/v1/auth/token` endpoint now returns additional fields:
- `refresh_token` (NEW)
- `expires_in` (NEW)

**Old Response**:
```json
{
  "access_token": "...",
  "token_type": "bearer"
}
```

**New Response**:
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Backward Compatibility

Existing clients can ignore the new fields. The `access_token` still works as before for the configured lifetime (30 minutes default).

---

## Performance Considerations

### Database Queries

- **Login**: 1 write (insert refresh token)
- **Refresh**: 2 writes (revoke old + insert new), 2 reads (get token + get user)
- **Revoke**: 1 write (update revoked flag)

### Indexes

Three indexes optimize token operations:
1. `idx_token`: Fast token lookup
2. `idx_user_id`: Fast user token queries
3. `idx_token_family`: Fast family revocation

### Cleanup Job

Recommended: Schedule periodic cleanup of expired tokens

```python
# Cron job or scheduled task
def cleanup_expired_tokens():
    count = refresh_token_repository.delete_expired()
    logger.info(f"Deleted {count} expired refresh tokens")
```

---

## Conclusion

✅ **Full OAuth2 refresh token flow implemented**  
✅ **Token rotation prevents replay attacks**  
✅ **Token family tracking detects theft**  
✅ **Production-ready with security best practices**  
✅ **Configurable token lifetimes**  
✅ **Manual revocation supported**  

The implementation follows OAuth2 best practices and provides a secure, scalable token refresh mechanism.
