/**
 * Real-time Digests Component
 * 
 * Displays AI-generated digests with real-time updates.
 * Shows digest publication and delivery status.
 */

import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
  Box,
  Card,
  CardContent,
  CardActions,
  Grid,
  Button,
  Chip,
  Stack,
  Typography,
  LinearProgress,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ScheduleIcon from '@mui/icons-material/Schedule';
import { markDigestRead } from '../store/slices/digests';

const DigestsComponent = () => {
  const dispatch = useDispatch();
  const { items, unreadCount, loading, error, lastUpdated } = useSelector(
    (state) => state.digests
  );
  const [expandedId, setExpandedId] = useState(null);

  const handleMarkRead = (digestId) => {
    dispatch(markDigestRead(digestId));
  };

  const handleAccordionChange = (digestId) => {
    setExpandedId(expandedId === digestId ? null : digestId);
  };

  const getStatusColor = (isRead) => {
    return isRead ? 'default' : 'error';
  };

  const getStatusIcon = (isRead) => {
    return isRead ? (
      <CheckCircleIcon fontSize="small" />
    ) : (
      <ScheduleIcon fontSize="small" />
    );
  };

  return (
    <Box sx={{ p: 2 }}>
      {/* Header */}
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Typography variant="h5">Daily Digests</Typography>
        <Stack direction="row" alignItems="center" gap={2}>
          {unreadCount > 0 && (
            <Chip
              label={`${unreadCount} Unread`}
              color="error"
              variant="outlined"
            />
          )}
          {lastUpdated && (
            <Typography variant="caption" color="textSecondary">
              Last updated: {new Date(lastUpdated).toLocaleTimeString()}
            </Typography>
          )}
        </Stack>
      </Stack>

      {/* Error Alert */}
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {/* Loading Progress */}
      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Empty State */}
      {items.length === 0 ? (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 4 }}>
            <Typography color="textSecondary">
              No digests available yet. Check back later!
            </Typography>
          </CardContent>
        </Card>
      ) : (
        <Grid container spacing={2}>
          {items.map((digest) => (
            <Grid item xs={12} key={digest.id}>
              <Card
                sx={{
                  bgcolor: digest.is_read ? 'white' : '#f0f7ff',
                  borderLeft: digest.is_read ? 'none' : '4px solid #1976d2',
                  transition: 'all 0.3s ease',
                }}
              >
                <CardContent>
                  {/* Header */}
                  <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 2 }}>
                    <Box sx={{ flexGrow: 1 }}>
                      <Stack direction="row" alignItems="center" gap={1} sx={{ mb: 1 }}>
                        <Typography variant="h6">
                          {digest.title}
                        </Typography>
                        <Chip
                          icon={getStatusIcon(digest.is_read)}
                          label={digest.is_read ? 'Read' : 'Unread'}
                          size="small"
                          color={getStatusColor(digest.is_read)}
                          variant={digest.is_read ? 'outlined' : 'filled'}
                        />
                      </Stack>

                      {/* Period */}
                      <Typography variant="body2" color="textSecondary">
                        Period: {new Date(digest.period_start).toLocaleDateString()} -{' '}
                        {new Date(digest.period_end).toLocaleDateString()}
                      </Typography>
                    </Box>

                    {/* Action Buttons */}
                    <Stack direction="column" spacing={0.5}>
                      {!digest.is_read && (
                        <Button
                          size="small"
                          variant="outlined"
                          onClick={() => handleMarkRead(digest.id)}
                        >
                          Mark Read
                        </Button>
                      )}
                      {digest.delivered_at && (
                        <Chip
                          label="Delivered"
                          size="small"
                          color="success"
                          variant="outlined"
                        />
                      )}
                    </Stack>
                  </Stack>

                  {/* Summary Preview */}
                  <Typography variant="body2" sx={{ mb: 2, color: '#555' }}>
                    {digest.summary.substring(0, 150)}
                    {digest.summary.length > 150 ? '...' : ''}
                  </Typography>

                  {/* Key Topics */}
                  {digest.key_topics && digest.key_topics.length > 0 && (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" fontWeight="bold" sx={{ mb: 1 }}>
                        Key Topics:
                      </Typography>
                      <Stack direction="row" spacing={0.5} sx={{ flexWrap: 'wrap' }}>
                        {digest.key_topics.map((topic, idx) => (
                          <Chip
                            key={idx}
                            label={topic}
                            size="small"
                            variant="outlined"
                            color="primary"
                          />
                        ))}
                      </Stack>
                    </Box>
                  )}

                  {/* Expandable Details */}
                  {(digest.key_discussions?.length > 0 || digest.action_items?.length > 0) && (
                    <Accordion
                      expanded={expandedId === digest.id}
                      onChange={() => handleAccordionChange(digest.id)}
                    >
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Typography variant="body2" fontWeight="bold">
                          View Full Details
                        </Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Stack spacing={2}>
                          {/* Key Discussions */}
                          {digest.key_discussions && digest.key_discussions.length > 0 && (
                            <Box>
                              <Typography variant="body2" fontWeight="bold" sx={{ mb: 1 }}>
                                Key Discussions:
                              </Typography>
                              <List dense disablePadding>
                                {digest.key_discussions.map((discussion, idx) => (
                                  <ListItem key={idx} disableGutters>
                                    <ListItemText
                                      primary={discussion}
                                      primaryTypographyProps={{ variant: 'body2' }}
                                    />
                                  </ListItem>
                                ))}
                              </List>
                            </Box>
                          )}

                          {/* Action Items */}
                          {digest.action_items && digest.action_items.length > 0 && (
                            <Box>
                              <Typography variant="body2" fontWeight="bold" sx={{ mb: 1 }}>
                                Action Items:
                              </Typography>
                              <List dense disablePadding>
                                {digest.action_items.map((item, idx) => (
                                  <ListItem key={idx} disableGutters>
                                    <ListItemText
                                      primary={item}
                                      primaryTypographyProps={{ variant: 'body2' }}
                                    />
                                  </ListItem>
                                ))}
                              </List>
                            </Box>
                          )}

                          {/* Full Summary */}
                          <Box>
                            <Typography variant="body2" fontWeight="bold" sx={{ mb: 1 }}>
                              Full Summary:
                            </Typography>
                            <Typography variant="body2" sx={{ color: '#666' }}>
                              {digest.summary}
                            </Typography>
                          </Box>
                        </Stack>
                      </AccordionDetails>
                    </Accordion>
                  )}
                </CardContent>

                {/* Footer */}
                <CardActions>
                  <Typography variant="caption" color="textSecondary" sx={{ flexGrow: 1 }}>
                    Published: {new Date(digest.published_at).toLocaleString()}
                  </Typography>
                  <Button size="small" variant="contained">
                    Share
                  </Button>
                  <Button size="small" variant="outlined">
                    Archive
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Footer Info */}
      <Box sx={{ mt: 3, p: 2, bgcolor: '#f5f5f5', borderRadius: 1 }}>
        <Typography variant="body2" color="textSecondary">
          💡 <strong>Real-time Updates:</strong> New digests appear instantly as they're published.
          You'll be notified in real-time when digests are ready to read!
        </Typography>
      </Box>
    </Box>
  );
};

export default DigestsComponent;
