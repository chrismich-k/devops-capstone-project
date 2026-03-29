---
name: User Story
about: Template to create a new User Story, including acceptance criteria suitable
  for BDD.
title: ''
labels: ''
assignees: ''

---

**As a** [role]
**I need** [function]
**So that** [benefit]

### Details and Assumptions
- [document what you know]
- [document some more]

### Acceptance Criteria

**Scenario: [General scenario title]**
```gherkin
Given [some context]
When [certain action is taken]
Then [the outcome of action is observed]
```

**Scenario: [Success scenario title]**
```gherkin
Given [some context or precondition]
When [a specific action is taken]
Then [a measurable outcome is observed]
And [additional result if applicable]
```

**Scenario: [Failure/Edge case scenario title]**
```gherkin
Given [context for the error case]
When [an invalid action or input is provided]
Then [the system should respond with an error/specific status]
```
