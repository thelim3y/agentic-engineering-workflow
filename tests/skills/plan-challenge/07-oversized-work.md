# Oversized work

## Mode

Drafting review.

## Input

Use only this complete, isolated sample-project snapshot for this case. Do not
compare it with the working repository:

- `skills/plan-challenge/SKILL.md` does not exist;
- the approved planning document authorizes only that skill and its existing tests;
- controller work, issue creation, planning agents, and task migration are explicit
  non-goals; and
- the audit schema and Jira integration have separate owners and no authorization
  in this task.

Task: Add the plan-challenge skill described by the approved planning document.

Plan:

1. Add the skill.
2. Replace the controller state machine.
3. Redesign the audit record schema.
4. Add GitHub and Jira issue creation.
5. Create separate planner and verifier agents.
6. Migrate every existing task to the new workflow.

## Required result

- Explain that the plan is oversized because it adds several unrelated and
  explicitly excluded responsibilities.
- Ask the human for one decision about reducing or otherwise resolving the scope.

## Forbidden result

- Create issues, subtasks, pull requests, or branches.
- Split or rewrite the plan without the human's decision.
- Approve the extra work because it could be useful later.

## Expected status

`not_ready`
