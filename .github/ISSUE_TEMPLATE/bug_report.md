name: 🐛 Bug Report
description: File a bug report to help us improve SentinelOps
title: "[BUG]: "
labels: ["bug"]
body:

- type: markdown
  attributes:
  value: |
  Thanks for reporting a bug! Please fill out the form below.
- type: textarea
  id: description
  attributes:
  label: Bug Description
  description: A clear and concise description of what the bug is.
  placeholder: Describe the issue...
  validations:
  required: true
- type: textarea
  id: steps
  attributes:
  label: Steps to Reproduce
  description: How do we reproduce this?
  placeholder: | 1. Go to '...' 2. Click on '....' 3. See error
  validations:
  required: true
- type: textarea
  id: expected
  attributes:
  label: Expected Behavior
  description: What did you expect to happen?
  validations:
  required: true
- type: textarea
  id: screenshots
  attributes:
  label: Screenshots
  description: If applicable, add screenshots to help explain your problem.
