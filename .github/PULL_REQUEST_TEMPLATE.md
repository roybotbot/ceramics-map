## What does this PR do?

<!-- Brief description of the change -->

## Checklist (for studio additions)

- [ ] `studios.json` is valid JSON
- [ ] New entry has `name` and `address`
- [ ] Coordinates are `[longitude, latitude]` (not reversed)
- [ ] At least one category boolean is `true`
- [ ] No duplicate of an existing studio
- [ ] Website URL starts with `http://` or `https://` (if provided)

## How to test

```bash
python3 scripts/validate.py
```
