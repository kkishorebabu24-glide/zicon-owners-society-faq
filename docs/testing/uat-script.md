# User Acceptance Testing (UAT) Script

## Overview
This UAT script is designed for 10-20 resident volunteers to validate the Home Food Sellers Platform before production deployment. Each scenario should take 15-30 minutes to complete.

## UAT Participants
- **Primary Testers**: 5-10 residents familiar with society operations
- **Domain Experts**: 2-3 society committee members
- **Technical Support**: Developer available for questions

## Test Environment
- Staging environment with production-like data
- Mobile devices (Android/iOS) and desktops
- Test accounts pre-created for each participant

## Scenario 1: New Buyer Discovers and Orders a Meal

### Objective
Validate the complete buyer journey from discovery to order completion

### Preconditions
- Test buyer account created and approved
- Multiple sellers have active menus for today
- Various food categories available

### Test Steps
1. **App Discovery**
   - Open the PWA in browser/mobile
   - Verify app loads within 3 seconds
   - Check if app prompts for installation

2. **Account Setup**
   - Login with test credentials
   - Verify dashboard loads correctly
   - Check profile information display

3. **Meal Browsing**
   - Navigate to "Browse Meals" section
   - Verify today's meals are displayed
   - Test category filtering (Veg/Non-Veg/Snacks)
   - Sort by price, rating, or pickup time
   - View seller profiles and ratings

4. **Menu Selection**
   - Select a menu item from different seller
   - Check item details (price, quantity, pickup time)
   - Verify seller information and rating

5. **Order Placement**
   - Add item to cart/order
   - Review order summary
   - Confirm order placement
   - Note pickup instructions

6. **Order Tracking**
   - Check order status in "My Orders"
   - Verify order appears with correct details
   - Test push notifications (if implemented)

### Expected Results
- Smooth navigation throughout the flow
- Clear information display
- Intuitive ordering process
- Accurate order summary

### Success Criteria
- Complete order placement without assistance
- All information clearly visible
- Process takes less than 5 minutes

## Scenario 2: Seller Lists Today's Special and Receives an Order

### Objective
Validate seller menu management and order fulfillment workflow

### Preconditions
- Test seller account created and approved
- Seller has permission to create menus

### Test Steps
1. **Seller Dashboard Access**
   - Login as seller
   - Verify seller-specific dashboard
   - Check existing menu items (if any)

2. **Menu Creation**
   - Navigate to "Manage Menu"
   - Click "Add New Item"
   - Enter item details:
     - Name: "Special Chicken Biryani"
     - Price: ₹150
     - Quantity: 10 servings
     - Category: Non-Veg
     - Pickup Time: 8:00 PM
     - Description: "Authentic home-made biryani"
   - Save the menu item

3. **Menu Management**
   - Edit the created item (change price to ₹160)
   - Verify changes saved
   - Check time slot validation (try duplicate time)

4. **Order Monitoring**
   - Switch to buyer account in another session
   - Place order for the created item
   - Return to seller account
   - Verify order appears in "Orders" section

5. **Order Fulfillment**
   - Mark order as "Ready for Pickup"
   - Verify status update
   - Check if buyer receives notification

### Expected Results
- Intuitive menu creation interface
- Real-time order updates
- Clear order management workflow

### Success Criteria
- Menu item created without errors
- Order received and processed correctly
- Status updates work as expected

## Scenario 3: Admin Approves a New Resident

### Objective
Validate admin approval workflow and user management

### Preconditions
- Admin account with approval permissions
- Pending resident registration exists

### Test Steps
1. **Admin Login**
   - Access admin panel
   - Verify admin dashboard loads
   - Check pending approvals count

2. **Review Pending Users**
   - Navigate to "Pending Approvals"
   - View list of pending residents
   - Click on a pending user to view details

3. **User Verification**
   - Review user information (name, flat, contact)
   - Verify flat number validity
   - Check for any suspicious information

4. **Approval Process**
   - Approve the resident
   - Verify confirmation message
   - Check if user status updates

5. **Notification Verification**
   - Verify approval notification sent to user
   - Test user can now login and access features

### Expected Results
- Clear admin interface
- Comprehensive user information display
- Secure approval process

### Success Criteria
- User approved successfully
- Status updates correctly
- Notifications work properly

## UAT Feedback Form

### Participant Information
- Name: __________________________
- Flat Number: ___________________
- Device Used: ___________________
- Scenario Completed: _____________

### Scenario Rating (1-5 scale)
1. **Ease of Use**: How intuitive was the interface?
   [1] [2] [3] [4] [5]

2. **Performance**: How responsive was the application?
   [1] [2] [3] [4] [5]

3. **Functionality**: Did everything work as expected?
   [1] [2] [3] [4] [5]

4. **Mobile Experience**: How well did it work on mobile?
   [1] [2] [3] [4] [5]

### Open Feedback
1. What worked well?
   ________________________________________________________
   ________________________________________________________

2. What didn't work well?
   ________________________________________________________
   ________________________________________________________

3. Any suggestions for improvement?
   ________________________________________________________
   ________________________________________________________

4. Would you use this platform regularly?
   - Yes
   - No
   - Maybe (explain): ____________________

5. Additional Comments:
   ________________________________________________________
   ________________________________________________________
   ________________________________________________________

### Bug Reports
If you encountered any issues, please describe:
- What you were trying to do:
- What happened instead:
- Steps to reproduce:
- Screenshots (if possible):

---

## UAT Success Criteria

### Overall Success Metrics
- **Completion Rate**: >90% of participants complete all scenarios
- **Average Rating**: >4.0 out of 5 for all scenarios
- **Bug Count**: <5 critical issues identified
- **Performance**: All operations complete within expected time

### Go/No-Go Decision
- **Go**: All critical scenarios pass, no blocking issues
- **No-Go**: Critical functionality broken, major usability issues

### Post-UAT Activities
1. Review all feedback and bug reports
2. Prioritize issues for fixing
3. Update test cases based on findings
4. Plan production deployment
5. Schedule follow-up user training sessions