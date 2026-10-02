# Feature Cycle

1. Read the project plan and responsibility map configured in `.codecraft/project.json`.
2. Select only the human-approved behavior slice.
3. State receiver responsibilities, information ownership, decision ownership, state ownership, protocols, injection points, and composition boundary.
4. Present the numbered BDD approval grid.
5. After approval, create one public behavior test and run it to the expected red.
6. Pause for human confirmation of the expected outside red.
7. Add the smallest focused test needed to drive the next production step.
8. Make the smallest production change that turns the focused test green, then make the BDD test green.
9. Refactor only while green and review responsibilities and SOLID afterward.
10. Run the applicable isolated completion lane and preserve its receipt for commit review.
11. Record feature evidence with the skill's template and update the plan only when completion evidence is current.

Never modify an existing protected BDD asset without the repository's exact protected-change authorization flow.
