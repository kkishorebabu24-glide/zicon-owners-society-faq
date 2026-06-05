# Authentication, User Dashboard & Society Notifications Guide

## Overview

The Society App now features a complete authentication system with user profiles, dashboards, and real-time society notifications. This guide covers:

1. **Authentication Flow** - JWT-based login/registration
2. **User Dashboard** - Profile management and preferences
3. **Society Notifications** - Real-time notification system

---

## Part 1: Authentication System

### Backend API Endpoints

#### Register New User
```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Resident",
  "email": "john@example.com",
  "phone": "+919876543210",
  "password": "SecurePassword123!",
  "bio": "Long-time resident of Sector 12",
  "address": "Apt 501, Block C"
}
```

**Response (201):**
```json
{
  "user_id": 1,
  "email": "john@example.com",
  "message": "Registration successful. Please log in."
}
```

#### Login
```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePassword123!"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900
}
```

#### Get Current User
```bash
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": 1,
  "first_name": "John",
  "last_name": "Resident",
  "email": "john@example.com",
  "phone": "+919876543210",
  "role": "resident",
  "is_active": true,
  "email_verified": false,
  "phone_verified": false,
  "avatar_url": null,
  "bio": "Long-time resident",
  "address": "Apt 501",
  "digest_frequency": "daily",
  "receive_notifications": true,
  "notification_channels": {
    "email": true,
    "telegram": false,
    "sms": false
  },
  "created_at": "2026-06-04T10:00:00Z",
  "last_login_at": "2026-06-04T10:30:00Z"
}
```

#### Refresh Access Token
```bash
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "token": "<refresh_token>"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "<refresh_token>",
  "token_type": "bearer",
  "expires_in": 900
}
```

#### Logout
```bash
POST /api/v1/auth/logout
Authorization: Bearer <access_token>
```

### Frontend Authentication Flow

#### 1. Registration
```javascript
import { useAuth } from './context/AuthContext';

function RegisterComponent() {
  const { register, loading, error } = useAuth();

  const handleRegister = async () => {
    const result = await register({
      firstName: 'John',
      lastName: 'Resident',
      email: 'john@example.com',
      phone: '+919876543210',
      password: 'SecurePassword123!',
      bio: 'Long-time resident',
      address: 'Apt 501'
    });

    if (result.success) {
      // Registration successful
      console.log('User registered:', result.data);
    } else {
      // Registration failed
      console.error('Error:', result.error);
    }
  };

  return <button onClick={handleRegister} disabled={loading}>Register</button>;
}
```

#### 2. Login
```javascript
import { useAuth } from './context/AuthContext';

function LoginComponent() {
  const { login, loading, error } = useAuth();

  const handleLogin = async () => {
    const result = await login('john@example.com', 'SecurePassword123!');

    if (result.success) {
      // Login successful, redirect to dashboard
      navigate('/dashboard');
    } else {
      // Login failed
      console.error('Error:', result.error);
    }
  };

  return <button onClick={handleLogin} disabled={loading}>Login</button>;
}
```

#### 3. Check Authentication Status
```javascript
import { useAuth } from './context/AuthContext';

function MyComponent() {
  const { isAuthenticated, user, loading } = useAuth();

  if (loading) return <div>Loading...</div>;

  if (!isAuthenticated) {
    return <div>Please log in</div>;
  }

  return <div>Welcome, {user.first_name}!</div>;
}
```

#### 4. Protected Routes
```javascript
import { ProtectedRoute } from './components/ProtectedRoute';

<Routes>
  <Route path="/auth" element={<AuthPage />} />
  <Route path="/dashboard" element={<ProtectedRoute element={<Dashboard />} />} />
</Routes>
```

### Token Management

Tokens are automatically stored in `localStorage`:
- `auth_access_token` - Current access token (15-minute expiry)
- `auth_refresh_token` - Refresh token (7-day expiry)
- `auth_user` - Current user data (JSON)

Tokens are automatically refreshed when expired via the `authService.refreshAccessToken()` method.

---

## Part 2: User Dashboard

### Profile Management

The user dashboard displays:
- **Profile Section**: Avatar, name, email, phone, role
- **Account Status**: Email/phone verification status
- **Edit Mode**: Update first name, last name, bio, address
- **Account Activity**: Last login, member since date

### Editing Profile

```javascript
import { useAuth } from './context/AuthContext';

function UserDashboard() {
  const { user, authService } = useAuth();
  const [editData, setEditData] = useState({
    first_name: user.first_name,
    last_name: user.last_name,
    bio: user.bio,
    address: user.address
  });

  const handleSaveProfile = async () => {
    // TODO: Implement PUT /api/v1/auth/{user_id} endpoint
    // Send editData to backend
  };

  return (
    // UI for editing profile
  );
}
```

### Notification Preferences

Users can configure:
- **Enable/Disable Notifications**: Global toggle
- **Notification Channels**: Email, Telegram, SMS
- **Digest Frequency**: Daily, Weekly, Immediate

```javascript
const preferences = {
  digest_frequency: 'daily',
  receive_notifications: true,
  notification_channels: {
    email: true,
    telegram: false,
    sms: false
  }
};
```

---

## Part 3: Society Notifications

### Backend Notification Endpoints

#### Get Paginated Notifications
```bash
GET /api/v1/notifications?skip=0&limit=20&unread_only=false
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "user_id": 1,
      "type": "listing_match",
      "title": "New Match Found",
      "message": "Someone is interested in your furniture offer",
      "icon": "shopping_bag",
      "color": "success",
      "related_type": "listing",
      "related_id": 123,
      "action_url": "/listings/123",
      "metadata": {
        "match_id": 456,
        "match_score": 0.95
      },
      "is_read": false,
      "is_archived": false,
      "created_at": "2026-06-04T10:30:00Z",
      "read_at": null
    }
  ],
  "total": 42,
  "unread_count": 5,
  "skip": 0,
  "limit": 20
}
```

#### Get Single Notification
```bash
GET /api/v1/notifications/{notification_id}
Authorization: Bearer <access_token>
```

#### Mark as Read
```bash
PUT /api/v1/notifications/{notification_id}/mark-read
Authorization: Bearer <access_token>
```

#### Mark All as Read
```bash
PUT /api/v1/notifications/mark-all-read
Authorization: Bearer <access_token>
```

#### Delete Notification
```bash
DELETE /api/v1/notifications/{notification_id}
Authorization: Bearer <access_token>
```

#### Get Unread Count
```bash
GET /api/v1/notifications/stats/unread-count
Authorization: Bearer <access_token>

Response: { "unread_count": 5 }
```

### Notification Types

Notifications can be of various types:

| Type | Icon | Color | When | Example |
|------|------|-------|------|---------|
| `listing_match` | ✓ | success | Match found for listing | "Someone interested in your offer" |
| `digest_published` | ℹ | info | New digest available | "Daily Digest Ready" |
| `digest_delivered` | ✓ | success | Digest delivered | "Digest sent to your email" |
| `announcement` | 📢 | primary | Society announcement | "New parking rules announced" |
| `admin_message` | ⚠ | warning | Admin message | "Maintenance scheduled" |

### Frontend Notification Component

The `SocietyNotifications` component provides:

```javascript
import SocietyNotifications from './components/SocietyNotifications';

// In AppBar
<SocietyNotifications />
```

**Features:**
- Bell icon with unread badge
- Auto-refresh interval (30s/60s toggleable)
- Filter by type (newest/oldest/unread)
- Mark as read/delete actions
- Shows 50 most recent notifications

### Creating Notifications Programmatically

To create notifications from your backend services:

```python
from app.db.models import SocietyNotification
from app.core.database import SessionLocal

db = SessionLocal()

# Create notification
notification = SocietyNotification(
    user_id=user_id,
    type='listing_match',
    title='New Match Found',
    message='Someone is interested in your furniture offer',
    icon='shopping_bag',
    color='success',
    related_type='listing',
    related_id=listing_id,
    action_url=f'/listings/{listing_id}',
    metadata={
        'match_id': match_id,
        'match_score': 0.95
    }
)
db.add(notification)
db.commit()
```

### Broadcasting Notifications via WebSocket

Integrate with real-time updates:

```python
from app.core.websocket_manager import get_connection_manager

manager = get_connection_manager()

# Publish notification event
await manager.publish_event(
    event_type='notification_received',
    data={
        'user_id': user_id,
        'notification_id': notification.id,
        'type': notification.type,
        'title': notification.title
    },
    target_users=[user_id]  # Send only to this user
)
```

---

## Testing the Complete Flow

### Step 1: Register a User (Frontend)
1. Open http://localhost:3000
2. Click on "Register" tab
3. Fill in the form with sample data
4. Click "Register"
5. Should see "Registration successful" message

### Step 2: Login
1. Switch to "Login" tab
2. Enter registered email and password
3. Click "Login"
4. Should be redirected to Dashboard

### Step 3: View Profile
1. You should see your profile information
2. Try editing a field
3. Click "Save Changes" (API endpoint needs implementation)

### Step 4: Configure Preferences
1. Click "Preferences" button
2. Toggle notification settings
3. Click "Save" (API endpoint needs implementation)

### Step 5: Test Notifications
Create a test notification via API:

```bash
curl -X POST http://localhost:8000/api/v1/notifications \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "type": "test_notification",
    "title": "Test Notification",
    "message": "This is a test notification",
    "color": "info"
  }'
```

Then open the notification bell - it should appear!

### Step 6: Test WebSocket
1. Open browser DevTools
2. Go to Network > WS tab
3. You should see ws://localhost:8000/api/v1/marketplace/ws/listings connected
4. Status should show 🟢 Online

### Step 7: Logout
1. Click your name dropdown
2. Click "Logout"
3. Should be redirected to login page

---

## Environment Configuration

### Frontend (.env or package.json)
```env
REACT_APP_API_URL=http://localhost:8000
```

### Backend (.env)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/society_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

---

## Security Best Practices

1. **Tokens**: Never store access tokens in cookies (XSS vulnerability). Using localStorage is acceptable for SPAs.
2. **HTTPS**: Always use HTTPS in production
3. **Password**: Passwords are hashed with bcrypt before storage
4. **Validation**: All inputs validated with Pydantic on backend
5. **CORS**: Configured to trusted origins only
6. **Rate Limiting**: Implement rate limiting on auth endpoints in production

---

## Troubleshooting

### "Invalid email or password" on Login
- Check if user exists in database
- Verify password is correct (case-sensitive)
- Check database is running: `docker ps`

### Blank Login Page
- Check if REACT_APP_API_URL is correctly set
- Open browser console for errors
- Verify frontend is running: http://localhost:3000

### Notifications Not Appearing
- Check if user is authenticated (token valid)
- Verify WebSocket connection (🟢 Online badge)
- Check browser console for errors
- Manually fetch: GET /api/v1/notifications

### Token Refresh Failing
- Verify refresh token not expired (7 days)
- Check SECRET_KEY is same as login
- Verify Redis is running for session storage

---

## Next Steps

1. **Implement Missing API Endpoints**:
   - PUT `/api/v1/auth/{user_id}` - Update user profile
   - PUT `/api/v1/auth/{user_id}/preferences` - Update preferences

2. **Email Verification**:
   - Add email verification workflow
   - Verify email before allowing certain actions

3. **Password Management**:
   - Add "Forgot Password" flow
   - Add password change endpoint
   - Add password reset email

4. **Enhanced Notifications**:
   - Create notifications from marketplace events
   - Create notifications from digest publishing
   - Filter notifications by type
   - Notification templates

5. **User Roles & Permissions**:
   - Restrict certain operations by role
   - Admin dashboard for user management
   - Moderator tools for content moderation

6. **Integration Tests**:
   - End-to-end test suite
   - Authentication flow tests
   - Permission/authorization tests
