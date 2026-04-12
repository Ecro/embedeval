# n=3 aggregate — claude-code://sonnet

## Per-run pass@1

| Run | pass@1 | passed | total |
|-----|--------|--------|-------|
| n1 | 66.1% | 154 | 233 |
| n2 | 70.4% | 164 | 233 |
| n3 | 67.4% | 157 | 233 |

## Aggregate

- Mean pass@1: **68.0%**
- Sample stdev: 2.20%
- 95% CI (Wilson, pooled n×cases=699): [64.4%, 71.3%]
- Case stability: 87.1% (203/233 stable across all runs)

## Pass-count distribution

| Passed in k of 3 runs | Cases |
|------------------------|-------|
| 0 | 60 |
| 1 | 14 |
| 2 | 16 |
| 3 | 143 |
