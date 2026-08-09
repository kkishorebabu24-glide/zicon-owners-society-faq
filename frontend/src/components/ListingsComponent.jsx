/**
 * Real-time Listings Component
 * 
 * Displays marketplace listings (offers and requests) with real-time updates.
 * Updates instantly when new listings are created or existing ones are modified.
 */

import React, { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
  Box,
  Card,
  CardContent,
  CardActions,
  Grid,
  TextField,
  Button,
  Chip,
  Stack,
  Typography,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  LinearProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControlLabel,
  Checkbox,
} from '@mui/material';
import ShoppingBagIcon from '@mui/icons-material/ShoppingBag';
import RequestQuoteIcon from '@mui/icons-material/RequestQuote';
import { setFilter, setListings, setLoading, setError, clearError } from '../store/slices/listings';
import { useAuth } from '../context/AuthContext';
import { authService } from '../services/authService';

const apiUrl = process.env.REACT_APP_API_URL || '';

const ListingsComponent = () => {
  const dispatch = useDispatch();
  const { user, isAuthenticated } = useAuth();
  const { items, filter, loading, error, lastUpdated } = useSelector(
    (state) => state.listings
  );
  const [viewMode, setViewMode] = useState('all'); // 'all', 'offers', 'requests'
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingListing, setEditingListing] = useState(null);
  const [saving, setSaving] = useState(false);
  const [submitError, setSubmitError] = useState(null);
  const [formData, setFormData] = useState({
    type: 'offer',
    title: '',
    description: '',
    category: '',
    price: '',
    currency: 'USD',
    price_negotiable: false,
    location: '',
    tags: '',
  });

  const resetForm = () => {
    setFormData({
      type: 'offer',
      title: '',
      description: '',
      category: '',
      price: '',
      currency: 'USD',
      price_negotiable: false,
      location: '',
      tags: '',
    });
    setEditingListing(null);
    setSubmitError(null);
  };

  const handleFilterChange = (field, value) => {
    dispatch(setFilter({ [field]: value }));
  };

  const handleSearchChange = (e) => {
    dispatch(setFilter({ searchQuery: e.target.value }));
  };

  const handleOpenCreateDialog = () => {
    resetForm();
    setIsDialogOpen(true);
  };

  const handleOpenEditDialog = (listing) => {
    setEditingListing(listing);
    setFormData({
      type: listing.type,
      title: listing.title || '',
      description: listing.description || '',
      category: listing.category || '',
      price: listing.price ?? '',
      currency: listing.currency || 'USD',
      price_negotiable: Boolean(listing.price_negotiable),
      location: listing.location || '',
      tags: Array.isArray(listing.tags) ? listing.tags.join(', ') : '',
    });
    setSubmitError(null);
    setIsDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setIsDialogOpen(false);
    resetForm();
  };

  const handleFormChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const loadListings = async () => {
    dispatch(setLoading(true));
    dispatch(clearError());

    try {
      const response = await fetch(`${apiUrl}/api/v1/marketplace/listings?limit=50`, {
        headers: authService.getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error('Unable to load marketplace listings');
      }

      const payload = await response.json();
      dispatch(setListings(payload));
    } catch (err) {
      dispatch(setError(err.message || 'Unable to load marketplace listings'));
    } finally {
      dispatch(setLoading(false));
    }
  };

  useEffect(() => {
    loadListings();
  }, [dispatch]);

  const handleSubmitListing = async () => {
    if (!isAuthenticated || !authService.getToken()) {
      setSubmitError('Please sign in to create or update a listing.');
      return;
    }

    if (!formData.title.trim() || !formData.description.trim() || !formData.category.trim()) {
      setSubmitError('Title, description, and category are required.');
      return;
    }

    setSaving(true);
    setSubmitError(null);

    try {
      const payload = {
        type: formData.type,
        title: formData.title.trim(),
        description: formData.description.trim(),
        category: formData.category.trim(),
        price: formData.price === '' ? null : Number(formData.price),
        currency: formData.currency || 'USD',
        price_negotiable: Boolean(formData.price_negotiable),
        location: formData.location.trim() || null,
        tags: formData.tags
          .split(',')
          .map((tag) => tag.trim())
          .filter(Boolean),
        images: [],
      };

      const url = editingListing
        ? `${apiUrl}/api/v1/marketplace/listings/${editingListing.id}`
        : `${apiUrl}/api/v1/marketplace/listings`;
      const method = editingListing ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: authService.getAuthHeaders(),
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorPayload = await response.json().catch(() => ({}));
        throw new Error(errorPayload.detail || 'Failed to save listing');
      }

      await loadListings();
      handleCloseDialog();
    } catch (err) {
      setSubmitError(err.message || 'Unable to save listing');
    } finally {
      setSaving(false);
    }
  };

  // Filter listings based on current filters
  const filteredListings = items.filter((listing) => {
    if (viewMode === 'offers' && listing.type !== 'offer') return false;
    if (viewMode === 'requests' && listing.type !== 'request') return false;

    if (filter.category && listing.category !== filter.category) return false;

    if (
      filter.searchQuery &&
      !listing.title.toLowerCase().includes(filter.searchQuery.toLowerCase())
    ) {
      return false;
    }

    return true;
  });

  const getListingColor = (type) => {
    return type === 'offer' ? 'primary' : 'secondary';
  };

  const getListingIcon = (type) => {
    return type === 'offer' ? (
      <ShoppingBagIcon fontSize="small" />
    ) : (
      <RequestQuoteIcon fontSize="small" />
    );
  };

  return (
    <Box sx={{ p: 2 }}>
      {/* Header with connection status */}
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Typography variant="h5">Marketplace Listings</Typography>
        <Stack direction="row" spacing={1} alignItems="center">
          {isAuthenticated && (
            <Button variant="contained" onClick={handleOpenCreateDialog}>
              Create Listing
            </Button>
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

      {/* Filters */}
      <Card sx={{ mb: 3, p: 2 }}>
        <Grid container spacing={2} alignItems="flex-end">
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth>
              <InputLabel>View</InputLabel>
              <Select
                value={viewMode}
                onChange={(e) => setViewMode(e.target.value)}
                label="View"
              >
                <MenuItem value="all">All Listings</MenuItem>
                <MenuItem value="offers">Offers Only</MenuItem>
                <MenuItem value="requests">Requests Only</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth>
              <InputLabel>Category</InputLabel>
              <Select
                value={filter.category || ''}
                onChange={(e) =>
                  handleFilterChange('category', e.target.value || null)
                }
                label="Category"
              >
                <MenuItem value="">All Categories</MenuItem>
                <MenuItem value="furniture">Furniture</MenuItem>
                <MenuItem value="electronics">Electronics</MenuItem>
                <MenuItem value="services">Services</MenuItem>
                <MenuItem value="food">Food & Groceries</MenuItem>
                <MenuItem value="home">Home & Garden</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              placeholder="Search listings..."
              value={filter.searchQuery}
              onChange={handleSearchChange}
              size="small"
            />
          </Grid>
        </Grid>
      </Card>

      {/* Create/Edit Dialog */}
      <Dialog open={isDialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>{editingListing ? 'Update Listing' : 'Create Listing'}</DialogTitle>
        <DialogContent dividers>
          {submitError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {submitError}
            </Alert>
          )}
          <Grid container spacing={2} sx={{ mt: 0.5 }}>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Type</InputLabel>
                <Select
                  value={formData.type}
                  onChange={(e) => handleFormChange('type', e.target.value)}
                  label="Type"
                >
                  <MenuItem value="offer">Offer</MenuItem>
                  <MenuItem value="request">Request</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Category"
                value={formData.category}
                onChange={(e) => handleFormChange('category', e.target.value)}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Title"
                value={formData.title}
                onChange={(e) => handleFormChange('title', e.target.value)}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                minRows={3}
                label="Description"
                value={formData.description}
                onChange={(e) => handleFormChange('description', e.target.value)}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Price"
                type="number"
                value={formData.price}
                onChange={(e) => handleFormChange('price', e.target.value)}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Currency"
                value={formData.currency}
                onChange={(e) => handleFormChange('currency', e.target.value)}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={formData.price_negotiable}
                    onChange={(e) => handleFormChange('price_negotiable', e.target.checked)}
                  />
                }
                label="Price is negotiable"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Location"
                value={formData.location}
                onChange={(e) => handleFormChange('location', e.target.value)}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Tags (comma separated)"
                value={formData.tags}
                onChange={(e) => handleFormChange('tags', e.target.value)}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button variant="contained" onClick={handleSubmitListing} disabled={saving}>
            {saving ? 'Saving...' : editingListing ? 'Update Listing' : 'Create Listing'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Listings Grid */}
      <Grid container spacing={2}>
        {filteredListings.length === 0 ? (
          <Grid item xs={12}>
            <Card>
              <CardContent sx={{ textAlign: 'center', py: 4 }}>
                <Typography color="textSecondary">
                  No listings found. Try adjusting your filters or search.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ) : (
          filteredListings.map((listing) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={listing.id}>
              <Card
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    boxShadow: 4,
                    transform: 'translateY(-4px)',
                  },
                  bgcolor: listing.status !== 'active' ? '#f5f5f5' : 'white',
                }}
              >
                <CardContent sx={{ flexGrow: 1 }}>
                  {/* Type Badge */}
                  <Chip
                    icon={getListingIcon(listing.type)}
                    label={listing.type.charAt(0).toUpperCase() + listing.type.slice(1)}
                    color={getListingColor(listing.type)}
                    size="small"
                    sx={{ mb: 1 }}
                  />

                  {/* Status Badge */}
                  {listing.status !== 'active' && (
                    <Chip
                      label={listing.status.toUpperCase()}
                      size="small"
                      variant="outlined"
                      sx={{ ml: 1, mb: 1 }}
                    />
                  )}

                  {/* Title */}
                  <Typography gutterBottom variant="h6" sx={{ mt: 1 }}>
                    {listing.title}
                  </Typography>

                  {/* Category */}
                  <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                    Category: {listing.category}
                  </Typography>

                  {/* Price */}
                  {listing.price && (
                    <Typography variant="body1" fontWeight="bold" sx={{ mb: 1 }}>
                      ${listing.price} {listing.currency}
                      {listing.price_negotiable && (
                        <Chip
                          label="Negotiable"
                          size="small"
                          variant="outlined"
                          sx={{ ml: 1 }}
                        />
                      )}
                    </Typography>
                  )}

                  {/* Tags */}
                  {listing.tags && listing.tags.length > 0 && (
                    <Stack direction="row" spacing={0.5} sx={{ mb: 1, flexWrap: 'wrap' }}>
                      {listing.tags.map((tag) => (
                        <Chip key={tag} label={tag} size="small" variant="outlined" />
                      ))}
                    </Stack>
                  )}

                  {/* Stats */}
                  <Stack direction="row" spacing={2} sx={{ mt: 2 }}>
                    <Typography variant="caption" color="textSecondary">
                      👁 {listing.view_count} views
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      ❤️ {listing.interest_count} interested
                    </Typography>
                  </Stack>

                  {/* Created Time */}
                  <Typography variant="caption" color="textSecondary" sx={{ mt: 1 }}>
                    Posted: {new Date(listing.created_at).toLocaleDateString()}
                  </Typography>
                </CardContent>

                {/* Actions */}
                <CardActions>
                  <Button size="small" fullWidth variant="contained">
                    View Details
                  </Button>
                  {isAuthenticated && user?.id === listing.creator_id && (
                    <Button size="small" fullWidth variant="outlined" onClick={() => handleOpenEditDialog(listing)}>
                      Edit
                    </Button>
                  )}
                </CardActions>
              </Card>
            </Grid>
          ))
        )}
      </Grid>

      {/* Footer */}
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mt: 3 }}>
        <Typography variant="body2" color="textSecondary">
          Showing {filteredListings.length} of {items.length} listings
        </Typography>
        <Typography variant="caption" color="textSecondary">
          💡 Updates appear instantly via real-time WebSocket
        </Typography>
      </Stack>
    </Box>
  );
};

export default ListingsComponent;
