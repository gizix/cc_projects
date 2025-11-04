---
description: Add form validation to a view component
argument-hint: <view-file>
model: sonnet
---

Add form validation utilities to an existing view component.

Arguments:
- $1: Path to view file (e.g., `src/tkinter_app/views/main_view.py`)

Implement form validation using the validator utilities from `tkinter_app.utils.validators`:

1. **Import Validators**:
```python
from tkinter_app.utils import FormValidator, create_tk_validator
```

2. **Add Real-Time Validation** (validate on keystroke):
```python
def _build_form(self):
    # Email entry with validation
    vcmd = (self.register(create_tk_validator(FormValidator.validate_email)), '%P')
    self.email_entry = ttk.Entry(self, validate='key', validatecommand=vcmd)
```

3. **Add Focus-Out Validation** (validate when leaving field):
```python
def _setup_validation(self):
    self.email_entry.bind('<FocusOut>', self._validate_email)

def _validate_email(self, event=None) -> None:
    """Validate email on focus out."""
    email = self.email_var.get()
    if email and not FormValidator.validate_email(email):
        self.email_entry.configure(style='Danger.TEntry')
        self.show_error("Invalid email format")
    else:
        self.email_entry.configure(style='TEntry')
```

4. **Add Form-Wide Validation** (validate all fields on submit):
```python
def on_submit(self) -> None:
    """Handle form submission with validation."""
    # Define validation rules
    rules = {
        'email': [FormValidator.validate_email],
        'name': [FormValidator.validate_not_empty],
        'age': [
            lambda v: FormValidator.validate_number(v),
            lambda v: FormValidator.validate_range(v, 0, 150)
        ]
    }

    # Get form data
    data = {
        'email': self.email_var.get(),
        'name': self.name_var.get(),
        'age': self.age_var.get()
    }

    # Validate
    is_valid, errors = FormValidator.validate_form(data, rules)

    if is_valid:
        self.controller.on_form_submit(data)
    else:
        self.show_error("\\n".join(errors))
```

5. **Available Validators**:
   - `FormValidator.validate_email(email)` - Email format
   - `FormValidator.validate_phone(phone)` - Phone number
   - `FormValidator.validate_not_empty(value)` - Non-empty check
   - `FormValidator.validate_length(value, min, max)` - Length check
   - `FormValidator.validate_number(value, allow_float)` - Number format
   - `FormValidator.validate_range(value, min, max)` - Numeric range
   - `FormValidator.validate_pattern(value, regex)` - Custom regex

Read the view file at $1, analyze its form fields, and add appropriate validation based on the field types.
