# System Usability Scale (SUS) Questionnaire

Use this questionnaire after the participant has completed the dashboard tasks.

Each statement is rated from 1 to 5:

1 = strongly disagree  
2 = disagree  
3 = neutral  
4 = agree  
5 = strongly agree

## Questions

1. I think that I would like to use this dashboard frequently.
2. I found the dashboard unnecessarily complex.
3. I thought the dashboard was easy to use.
4. I think that I would need support to use this dashboard.
5. I found the different dashboard functions well integrated.
6. I thought there was too much inconsistency in this dashboard.
7. I would imagine that most people would learn to use this dashboard quickly.
8. I found the dashboard very cumbersome to use.
9. I felt very confident using the dashboard.
10. I needed to learn a lot of things before I could get going with this dashboard.

## SUS scoring

For odd-numbered questions:

```text
score = response - 1
```

For even-numbered questions:

```text
score = 5 - response
```

Then sum all adjusted scores and multiply by 2.5.

```text
SUS = sum(adjusted_scores) * 2.5
```

The final score is between 0 and 100.

## Interpretation guide

- below 50: poor usability
- 50 to 68: acceptable but needs improvement
- 68 to 80: good usability
- above 80: very good usability

## Additional open questions

1. What was the easiest part of the dashboard?
2. What was the most confusing part?
3. Which visualization helped you most?
4. What would you improve?
5. Did the dashboard help you understand shot quality better?
