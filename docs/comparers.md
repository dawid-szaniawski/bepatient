# Comparers
## Default comparers

Comparers serve as straightforward functions designed to compare two objects and return
a boolean value. _bepatient_ offers a comprehensive range of default comparers,
all designed to suit your testing needs. They can be accessed here:

```python
from bepatient import COMPARATORS


print(COMPARATORS)
```

The basic comparers include:
```yaml
comparators:
  - is_equal
  - is_not_equal
  - is_greater_than
  - is_lesser_than
  - is_greater_than_or_equal
  - is_lesser_than_or_equal
  - not_contain
  - contain_all
  - contain_any
  - have_len_equal
  - have_len_greater
  - have_len_lesser
```

## Custom comparers

To create your own comparer, you just need to prepare a function that takes two
arguments and returns a boolean value.

Example:
```python
from typing import Any


def is_instance(data: Any, expected_value: Any) -> bool:
    return is_instance(data, expected_value)
```

---
