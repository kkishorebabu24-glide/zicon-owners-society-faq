---
name: Bug Report
description: Report a bug or issue in the Home Food Sellers Platform
title: "[BUG] "
labels: ["bug", "triage"]
assignees: []
body:
  - type: markdown
    attributes:
      value: |
        ## Bug Report Template

        Thank you for reporting a bug! Please fill out the information below to help us investigate and fix the issue.

  - type: input
    id: summary
    attributes:
      label: Bug Summary
      description: A brief, clear summary of the bug
      placeholder: "e.g., Cannot place order when quantity exceeds available stock"
    validations:
      required: true

  - type: dropdown
    id: severity
    attributes:
      label: Severity
      description: How critical is this bug?
      options:
        - Critical - Blocks core functionality
        - High - Major feature broken
        - Medium - Feature impaired but workaround exists
        - Low - Minor issue or cosmetic
    validations:
      required: true

  - type: dropdown
    id: component
    attributes:
      label: Component
      description: Which part of the application is affected?
      options:
        - Frontend (React PWA)
        - Backend API
        - Database
        - Authentication
        - User Registration
        - Seller Dashboard
        - Buyer Dashboard
        - Order Management
        - Rating System
        - Admin Panel
        - Mobile Responsiveness
        - Performance
        - Security
        - Other
    validations:
      required: true

  - type: textarea
    id: description
    attributes:
      label: Description
      description: Detailed description of the bug
      placeholder: |
        Describe what you were doing when the bug occurred:
        1. Step 1
        2. Step 2
        3. Expected result vs actual result
    validations:
      required: true

  - type: textarea
    id: reproduction
    attributes:
      label: Steps to Reproduce
      description: Provide exact steps to reproduce the issue
      placeholder: |
        1. Go to '...'
        2. Click on '....'
        3. Scroll down to '....'
        4. See error
    validations:
      required: true

  - type: textarea
    id: expected-behavior
    attributes:
      label: Expected Behavior
      description: What should happen when following the steps above?
      placeholder: "The order should be placed successfully and user should see confirmation"
    validations:
      required: true

  - type: textarea
    id: actual-behavior
    attributes:
      label: Actual Behavior
      description: What actually happens?
      placeholder: "Error message appears: 'Internal server error'"
    validations:
      required: true

  - type: input
    id: environment
    attributes:
      label: Environment
      description: Where did this occur?
      placeholder: "e.g., Local development, Staging, Production"
    validations:
      required: true

  - type: input
    id: browser-device
    attributes:
      label: Browser/Device
      description: Browser and device information
      placeholder: "e.g., Chrome 120.0 on Android Samsung Galaxy S21"
    validations:
      required: true

  - type: dropdown
    id: user-role
    attributes:
      label: User Role
      description: What type of user encountered this?
      options:
        - Guest User
        - Registered Buyer
        - Approved Seller
        - Admin
        - Other
    validations:
      required: true

  - type: textarea
    id: error-messages
    attributes:
      label: Error Messages/Screenshots
      description: Any error messages or screenshots
      placeholder: |
        Error message: "500 Internal Server Error"

        Screenshots:
        - [Attach screenshot showing the error]
        - [Attach screenshot of browser console if applicable]
    validations:
      required: false

  - type: input
    id: frequency
    attributes:
      label: Frequency
      description: How often does this occur?
      placeholder: "e.g., Always, Sometimes (30% of the time), Once"
    validations:
      required: true

  - type: textarea
    id: additional-context
    attributes:
      label: Additional Context
      description: Any additional information that might be helpful
      placeholder: |
        - Related to recent changes?
        - Network conditions?
        - Time of day?
        - Other observations?
    validations:
      required: false

  - type: checkboxes
    id: checklist
    attributes:
      label: Checklist
      description: Please verify these before submitting
      options:
        - label: I have searched for existing issues to avoid duplicates
          required: true
        - label: I have provided clear steps to reproduce the issue
          required: true
        - label: I have included relevant environment and browser information
          required: true
        - label: I have attached screenshots if the issue is visual
          required: false
