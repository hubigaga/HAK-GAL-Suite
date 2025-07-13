# QUERY TRANSLATION QUALITY ANALYSIS REPORT

**Datum**: "2025-07-13 03:34:31.440572"
**Test Cases**: 20

## OVERALL PERFORMANCE METRICS

- **Average Precision**: 0.775
- **Average Recall**: 0.900
- **Average F1-Score**: 0.826
- **Semantic Similarity**: 0.900
- **Syntax Validity Rate**: 55.0%
- **Perfect Match Rate**: 50.0%

## CATEGORY-SPECIFIC ANALYSIS

### FACTUAL
- Test Cases: 11
- Average F1: 0.909
- Syntax Validity: 90.9%

### NEGATION
- Test Cases: 2
- Average F1: 0.800
- Syntax Validity: 0.0%

### COMPLEX
- Test Cases: 3
- Average F1: 0.838
- Syntax Validity: 0.0%

### RELATIONAL
- Test Cases: 4
- Average F1: 0.600
- Syntax Validity: 25.0%

## RECOMMENDATIONS

- 🟢 **GOOD**: F1-Score above 0.7 - translation quality acceptable
- 🔴 **CRITICAL**: Syntax validity below 80% - parser issues
