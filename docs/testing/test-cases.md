# Test Cases for Home Food Sellers Platform

## Functional Test Cases

| ID | Feature | Test Scenario | Preconditions | Test Steps | Expected Result | Priority |
|----|---------|---------------|---------------|------------|-----------------|----------|
| TC-001 | User Registration | Successful resident registration | User has valid flat number | 1. Navigate to registration page<br>2. Enter valid flat number, name, email, phone<br>3. Submit registration<br>4. Check email for OTP<br>5. Enter OTP to verify | User account created, pending admin approval | High |
| TC-002 | User Registration | Duplicate flat number registration | Flat number already registered | 1. Attempt registration with existing flat number<br>2. Submit form | Error message: "Flat number already registered" | High |
| TC-003 | User Registration | Invalid flat number | User enters non-existent flat | 1. Enter invalid flat number (e.g., "9999")<br>2. Submit registration | Error message: "Invalid flat number" | High |
| TC-004 | User Registration | Admin approval workflow | New user registered | 1. Admin logs in<br>2. Navigate to pending approvals<br>3. Review user details<br>4. Approve/reject user | User status updated, email notification sent | High |
| TC-005 | Seller Menu Management | Create new menu item | User is approved seller | 1. Login as seller<br>2. Navigate to menu management<br>3. Click "Add Item"<br>4. Enter item details (name, price, quantity, category, pickup time)<br>5. Save item | Menu item created and displayed in seller's menu | High |
| TC-006 | Seller Menu Management | Edit existing menu item | Menu item exists | 1. Select existing menu item<br>2. Modify details<br>3. Save changes | Menu item updated successfully | High |
| TC-007 | Seller Menu Management | Delete menu item | Menu item exists with no active orders | 1. Select menu item<br>2. Click delete<br>3. Confirm deletion | Menu item removed from menu | Medium |
| TC-008 | Seller Menu Management | Duplicate pickup time validation | Menu item exists | 1. Create item with pickup time 7:00 PM<br>2. Attempt to create another item with same time | Error: "Pickup time already exists for today" | High |
| TC-009 | Buyer Browsing | Browse today's meals | Multiple sellers have active menus | 1. Login as buyer<br>2. Navigate to browse page<br>3. View available meals | All current day's menu items displayed | High |
| TC-010 | Buyer Browsing | Filter by category | Meals from different categories exist | 1. Select category filter (Veg/Non-Veg/Snacks)<br>2. Apply filter | Only items from selected category shown | Medium |
| TC-011 | Buyer Browsing | Filter by seller rating | Sellers have different ratings | 1. Sort by rating<br>2. View seller profiles | Sellers displayed by rating order | Medium |
| TC-012 | Order Placement | Place order successfully | Item available, sufficient quantity | 1. Select menu item<br>2. Enter quantity<br>3. Confirm order<br>4. Pay cash on pickup | Order created, status "Ordered" | High |
| TC-013 | Order Placement | Order exceeds available quantity | Item has limited quantity | 1. Attempt to order more than available<br>2. Submit order | Error: "Insufficient quantity available" | High |
| TC-014 | Order Placement | Seller cannot order own food | User is both buyer and seller | 1. Login as seller<br>2. Attempt to order own menu item | Error: "Cannot order your own food" | High |
| TC-015 | Order Lifecycle | Seller marks order ready | Order placed and paid | 1. Seller views orders<br>2. Mark order as "Ready for pickup"<br>3. Save status | Order status updated, buyer notified | High |
| TC-016 | Order Lifecycle | Buyer confirms pickup | Order marked ready | 1. Buyer views orders<br>2. Confirm pickup<br>3. Rate seller (optional) | Order status "Completed" | High |
| TC-017 | Order Lifecycle | Order cancellation | Order not yet ready | 1. Buyer cancels order<br>2. Confirm cancellation | Order status "Cancelled", quantity restored | Medium |
| TC-018 | Rating System | Buyer rates seller after pickup | Order completed | 1. After pickup confirmation<br>2. Rate seller 1-5 stars<br>3. Add optional comment<br>4. Submit rating | Rating saved, seller average updated | Medium |
| TC-019 | Rating System | Rating display on seller profile | Seller has ratings | 1. View seller profile<br>2. Check rating section | Average rating and individual ratings shown | Medium |
| TC-020 | Edge Cases | Concurrent orders for same item | Multiple buyers ordering simultaneously | 1. Two buyers order last available item<br>2. Submit orders simultaneously | Only one order succeeds, other gets error | High |
| TC-021 | Edge Cases | Menu expiry | Menu has pickup time passed | 1. Time passes pickup time<br>2. Attempt to order expired item | Item no longer available for ordering | High |
| TC-022 | Edge Cases | Network connectivity loss | During order placement | 1. Start order process<br>2. Lose network connection<br>3. Regain connection | Order state preserved or clear error message | Medium |
| TC-023 | Admin Functions | View pending sellers | New registrations exist | 1. Admin login<br>2. View pending approvals<br>3. Review details | List of pending sellers with details | High |
| TC-024 | Admin Functions | Approve seller | Pending seller exists | 1. Select seller<br>2. Click approve<br>3. Confirm | Seller status updated to approved | High |
| TC-025 | Admin Functions | Reject seller | Pending seller exists | 1. Select seller<br>2. Click reject<br>3. Provide reason | Seller status updated to rejected | Medium |

## Non-Functional Test Cases

| ID | Category | Test Scenario | Preconditions | Test Steps | Expected Result | Priority |
|----|----------|---------------|---------------|------------|-----------------|----------|
| NF-001 | Performance | 500 concurrent users browsing | Test environment with 1000+ menu items | 1. Use Locust to simulate 500 users<br>2. Browse meals for 10 minutes<br>3. Monitor response times | Average response <500ms, no failures | High |
| NF-002 | Performance | Order placement under load | 100 concurrent orders | 1. Simulate 100 users placing orders<br>2. Monitor database performance<br>3. Check for race conditions | All orders processed correctly | High |
| NF-003 | Security | Flat numbers not exposed in URLs | User logged in | 1. Inspect network requests<br>2. Check URL parameters<br>3. Verify API responses | No flat numbers in URLs or responses | High |
| NF-004 | Security | IDOR vulnerability prevention | Multiple user accounts | 1. Login as User A<br>2. Attempt to access User B's data via URL manipulation<br>3. Try to modify other users' orders | Access denied, proper authorization | Critical |
| NF-005 | Security | Rate limiting on OTP requests | Valid phone number | 1. Request OTP 10 times in 1 minute<br>2. Check if requests are blocked | Rate limiting enforced after threshold | High |
| NF-006 | Security | Input validation and sanitization | Registration form | 1. Enter SQL injection attempts<br>2. Enter XSS payloads<br>3. Submit malformed data | All malicious inputs rejected | High |
| NF-007 | Usability | Mobile-first responsive design | Various device sizes | 1. Test on mobile (320px-768px)<br>2. Test on tablet (768px-1024px)<br>3. Test on desktop (>1024px) | Interface adapts properly to all sizes | High |
| NF-008 | Usability | Clear error messages | Invalid form submissions | 1. Submit forms with missing fields<br>2. Enter invalid data<br>3. Check error display | Clear, actionable error messages | Medium |
| NF-009 | Usability | Accessibility compliance | Screen reader enabled | 1. Navigate with keyboard only<br>2. Use screen reader<br>3. Check color contrast<br>4. Test form labels | WCAG 2.1 AA compliance | Medium |
| NF-010 | Reliability | Offline functionality | PWA installed | 1. Go offline<br>2. Access cached data<br>3. Attempt online operations | Graceful offline handling | Medium |
| NF-011 | Performance | Database query optimization | Large dataset (1000+ orders) | 1. Execute complex queries<br>2. Monitor execution time<br>3. Check query plans | Queries complete within 2 seconds | Medium |
| NF-012 | Security | Data encryption at rest | Database configured | 1. Inspect database files<br>2. Check encryption settings<br>3. Verify sensitive data handling | Sensitive data properly encrypted | High |

## Test Case Execution Guidelines

### Test Data Requirements
- 50 registered residents (mix of buyers/sellers)
- 20 active sellers with diverse menus
- 100+ historical orders
- Various user permission levels

### Test Environment Setup
- Local: Docker Compose with test database
- Staging: Cloud environment with production-like setup
- All tests should be runnable in CI/CD pipeline

### Automation Priority
- High: API integration tests, critical user flows
- Medium: UI component tests, data validation
- Low: Exploratory testing, visual regression

### Regression Testing
- Run full test suite before each release
- Focus on critical paths for hotfixes
- Maintain smoke test suite for quick validation