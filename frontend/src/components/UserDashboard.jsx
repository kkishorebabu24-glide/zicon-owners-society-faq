import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Paper,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Avatar,
  Divider,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Switch,
  FormControlLabel,
  FormGroup,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import SaveIcon from '@mui/icons-material/Save';
import CancelIcon from '@mui/icons-material/Cancel';
import { useAuth } from '../context/AuthContext';

export default function UserDashboard() {
  const { user, authService } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState({});
  const [preferencesOpen, setPreferencesOpen] = useState(false);
  const [preferences, setPreferences] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    if (user) {
      setEditData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        bio: user.bio || '',
        address: user.address || '',
      });
      setPreferences({
        digest_frequency: user.digest_frequency || 'daily',
        receive_notifications: user.receive_notifications ?? true,
        notification_channels: user.notification_channels || {
          email: true,
          telegram: false,
          sms: false,
        },
      });
    }
  }, [user]);

  const handleEditChange = (e) => {
    const { name, value } = e.target;
    setEditData((prev) => ({ ...prev, [name]: value }));
  };

  const handlePreferenceChange = (e) => {
    const { name, checked, type } = e.target;
    if (name === 'receive_notifications') {
      setPreferences((prev) => ({
        ...prev,
        receive_notifications: checked,
      }));
    } else {
      setPreferences((prev) => ({
        ...prev,
        notification_channels: {
          ...prev.notification_channels,
          [name]: checked,
        },
      }));
    }
  };

  const handleSaveProfile = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      // TODO: Call API to update profile
      // For now, just show a success message
      setSuccess('Profile updated successfully!');
      setIsEditing(false);
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSavePreferences = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      // TODO: Call API to update preferences
      // For now, just show a success message
      setSuccess('Preferences updated successfully!');
      setPreferencesOpen(false);
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <Container sx={{ py: 4 }}>
        <Typography>Loading...</Typography>
      </Container>
    );
  }

  const initials = `${user.first_name?.charAt(0)}${user.last_name?.charAt(0)}`.toUpperCase();

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

      <Grid container spacing={3}>
        {/* PROFILE SECTION */}
        <Grid item xs={12} md={4}>
          <Paper elevation={2} sx={{ p: 3, textAlign: 'center' }}>
            <Avatar
              sx={{
                width: 100,
                height: 100,
                margin: '0 auto 2rem',
                fontSize: '2.5rem',
                bgcolor: 'primary.main',
              }}
            >
              {initials}
            </Avatar>
            <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 1 }}>
              {user.first_name} {user.last_name}
            </Typography>
            <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
              {user.email}
            </Typography>
            <Typography variant="caption" color="textSecondary" display="block" sx={{ mb: 2 }}>
              {user.phone}
            </Typography>

            <Divider sx={{ my: 2 }} />

            {/* ROLE BADGE */}
            <Box sx={{ mb: 2 }}>
              <Typography variant="caption" sx={{ textTransform: 'uppercase', fontWeight: 'bold', color: 'primary.main' }}>
                {user.role}
              </Typography>
            </Box>

            {/* ACCOUNT STATUS */}
            <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center', mb: 2 }}>
              <Typography variant="caption" sx={{ ...( user.email_verified ? {color: 'success.main'} : {color: 'warning.main'} ) }}>
                ✓ Email {user.email_verified ? 'Verified' : 'Unverified'}
              </Typography>
            </Box>

            <Button
              variant="contained"
              startIcon={isEditing ? <CancelIcon /> : <EditIcon />}
              onClick={() => setIsEditing(!isEditing)}
              fullWidth
              size="small"
            >
              {isEditing ? 'Cancel' : 'Edit Profile'}
            </Button>

            <Button
              variant="outlined"
              onClick={() => setPreferencesOpen(true)}
              fullWidth
              size="small"
              sx={{ mt: 1 }}
            >
              Preferences
            </Button>
          </Paper>

          {/* MEMBER SINCE */}
          <Paper elevation={2} sx={{ p: 2, mt: 2 }}>
            <Typography variant="caption" color="textSecondary">
              Member since
            </Typography>
            <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
              {new Date(user.created_at).toLocaleDateString()}
            </Typography>
          </Paper>
        </Grid>

        {/* PROFILE EDIT SECTION */}
        <Grid item xs={12} md={8}>
          <Paper elevation={2} sx={{ p: 3 }}>
            {isEditing ? (
              <>
                <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
                  Edit Profile
                </Typography>

                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="First Name"
                      name="first_name"
                      value={editData.first_name}
                      onChange={handleEditChange}
                      disabled={loading}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Last Name"
                      name="last_name"
                      value={editData.last_name}
                      onChange={handleEditChange}
                      disabled={loading}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Bio"
                      name="bio"
                      value={editData.bio}
                      onChange={handleEditChange}
                      disabled={loading}
                      multiline
                      rows={3}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Address"
                      name="address"
                      value={editData.address}
                      onChange={handleEditChange}
                      disabled={loading}
                      multiline
                      rows={3}
                    />
                  </Grid>
                </Grid>

                <Box sx={{ mt: 3, display: 'flex', gap: 1 }}>
                  <Button
                    variant="contained"
                    startIcon={<SaveIcon />}
                    onClick={handleSaveProfile}
                    disabled={loading}
                  >
                    {loading ? <CircularProgress size={24} /> : 'Save Changes'}
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<CancelIcon />}
                    onClick={() => setIsEditing(false)}
                    disabled={loading}
                  >
                    Cancel
                  </Button>
                </Box>
              </>
            ) : (
              <>
                <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
                  Profile Information
                </Typography>

                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Box>
                      <Typography variant="caption" color="textSecondary">
                        First Name
                      </Typography>
                      <Typography variant="body1">{user.first_name}</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Box>
                      <Typography variant="caption" color="textSecondary">
                        Last Name
                      </Typography>
                      <Typography variant="body1">{user.last_name}</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12}>
                    <Box>
                      <Typography variant="caption" color="textSecondary">
                        Bio
                      </Typography>
                      <Typography variant="body1">{user.bio || 'No bio added'}</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12}>
                    <Box>
                      <Typography variant="caption" color="textSecondary">
                        Address
                      </Typography>
                      <Typography variant="body1">{user.address || 'No address added'}</Typography>
                    </Box>
                  </Grid>
                </Grid>
              </>
            )}
          </Paper>

          {/* ACTIVITY SECTION */}
          <Paper elevation={2} sx={{ p: 3, mt: 3 }}>
            <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2 }}>
              Account Activity
            </Typography>
            <Box sx={{ mb: 2 }}>
              <Typography variant="caption" color="textSecondary">
                Last Login
              </Typography>
              <Typography variant="body2">
                {user.last_login_at
                  ? new Date(user.last_login_at).toLocaleString()
                  : 'Never'}
              </Typography>
            </Box>
            <Box>
              <Typography variant="caption" color="textSecondary">
                Account Created
              </Typography>
              <Typography variant="body2">
                {new Date(user.created_at).toLocaleString()}
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* PREFERENCES DIALOG */}
      <Dialog open={preferencesOpen} onClose={() => setPreferencesOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Notification Preferences</DialogTitle>
        <DialogContent sx={{ pt: 2 }}>
          <FormGroup>
            <FormControlLabel
              control={
                <Switch
                  name="receive_notifications"
                  checked={preferences.receive_notifications}
                  onChange={handlePreferenceChange}
                />
              }
              label="Enable Notifications"
            />

            {preferences.receive_notifications && (
              <>
                <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>
                  Notification Channels
                </Typography>
                <FormControlLabel
                  control={
                    <Switch
                      name="email"
                      checked={preferences.notification_channels?.email ?? false}
                      onChange={handlePreferenceChange}
                    />
                  }
                  label="Email Notifications"
                />
                <FormControlLabel
                  control={
                    <Switch
                      name="telegram"
                      checked={preferences.notification_channels?.telegram ?? false}
                      onChange={handlePreferenceChange}
                    />
                  }
                  label="Telegram Notifications"
                />
                <FormControlLabel
                  control={
                    <Switch
                      name="sms"
                      checked={preferences.notification_channels?.sms ?? false}
                      onChange={handlePreferenceChange}
                    />
                  }
                  label="SMS Notifications"
                />

                <Typography variant="subtitle2" sx={{ mt: 3, mb: 1 }}>
                  Digest Frequency
                </Typography>
                <Box sx={{ ml: 2 }}>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    Current: <strong>{preferences.digest_frequency}</strong>
                  </Typography>
                  {/* TODO: Add frequency selector */}
                </Box>
              </>
            )}
          </FormGroup>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPreferencesOpen(false)}>Cancel</Button>
          <Button
            onClick={handleSavePreferences}
            variant="contained"
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}
