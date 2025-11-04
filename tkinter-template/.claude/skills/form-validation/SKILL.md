---
name: form-validation
description: Add comprehensive form validation to Tkinter views using the template's validator utilities. Use when creating forms, handling user input, when user mentions "validation", "form", or when working with Entry/Text widgets.
allowed-tools: Read, Write
---

You are a form validation expert for Tkinter applications. You implement robust input validation using this template's utilities.

## Validation Utilities

This template provides `FormValidator` class with common validation functions:

```python
from tkinter_app.utils import FormValidator, create_tk_validator
```

## Available Validators

1. **Email**: `FormValidator.validate_email(email)`
2. **Phone**: `FormValidator.validate_phone(phone)`
3. **Not Empty**: `FormValidator.validate_not_empty(value)`
4. **Length**: `FormValidator.validate_length(value, min, max)`
5. **Number**: `FormValidator.validate_number(value, allow_float=False)`
6. **Range**: `FormValidator.validate_range(value, min_val, max_val)`
7. **Pattern**: `FormValidator.validate_pattern(value, regex)`

## Validation Strategies

### 1. Real-Time Validation (on keystroke)

```python
def _build_form(self):
    # Create validator command
    vcmd = (
        self.register(create_tk_validator(FormValidator.validate_email)),
        '%P'  # New value
    )

    self.email_entry = ttk.Entry(
        self,
        textvariable=self.email_var,
        validate='key',  # Validate on keystroke
        validatecommand=vcmd
    )
```

### 2. Focus-Out Validation (when leaving field)

```python
def _build_form(self):
    self.email_entry = ttk.Entry(self, textvariable=self.email_var)
    self.email_entry.bind('<FocusOut>', self._validate_email)

    self.error_label = ttk.Label(self, text="", foreground="red")

def _validate_email(self, event=None) -> None:
    """Validate email when focus leaves field."""
    email = self.email_var.get()
    if email and not FormValidator.validate_email(email):
        self.email_entry.configure(style='Danger.TEntry')
        self.error_label.config(text="Invalid email format")
    else:
        self.email_entry.configure(style='TEntry')
        self.error_label.config(text="")
```

### 3. Form-Wide Validation (on submit)

```python
def on_submit(self) -> None:
    """Validate entire form before submission."""
    # Define validation rules
    rules = {
        'name': [FormValidator.validate_not_empty],
        'email': [FormValidator.validate_email],
        'phone': [FormValidator.validate_phone],
        'age': [
            lambda v: FormValidator.validate_number(v),
            lambda v: FormValidator.validate_range(v, 0, 150)
        ]
    }

    # Collect form data
    data = {
        'name': self.name_var.get(),
        'email': self.email_var.get(),
        'phone': self.phone_var.get(),
        'age': self.age_var.get(),
    }

    # Validate
    is_valid, errors = FormValidator.validate_form(data, rules)

    if is_valid:
        self.controller.on_form_submit(data)
        self.clear_form()
    else:
        self.show_errors(errors)
```

## Complete Form Example

```python
class UserFormView(ttk.Frame):
    """Form with comprehensive validation."""

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._build_form()

    def _build_form(self) -> None:
        form_frame = ttk.Frame(self, padding=20)
        form_frame.pack(fill=BOTH, expand=True)

        # Name field (required, min 2 chars)
        ttk.Label(form_frame, text="Name *:").grid(
            row=0, column=0, sticky=W, pady=5
        )
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(
            form_frame,
            textvariable=self.name_var
        )
        self.name_entry.grid(row=0, column=1, sticky=EW, pady=5, padx=(10, 0))
        self.name_entry.bind('<FocusOut>', self._validate_name)

        # Email field (valid format)
        ttk.Label(form_frame, text="Email *:").grid(
            row=1, column=0, sticky=W, pady=5
        )
        self.email_var = tk.StringVar()
        self.email_entry = ttk.Entry(
            form_frame,
            textvariable=self.email_var
        )
        self.email_entry.grid(row=1, column=1, sticky=EW, pady=5, padx=(10, 0))
        self.email_entry.bind('<FocusOut>', self._validate_email)

        # Phone field (optional, but must be valid if provided)
        ttk.Label(form_frame, text="Phone:").grid(
            row=2, column=0, sticky=W, pady=5
        )
        self.phone_var = tk.StringVar()
        self.phone_entry = ttk.Entry(
            form_frame,
            textvariable=self.phone_var
        )
        self.phone_entry.grid(row=2, column=1, sticky=EW, pady=5, padx=(10, 0))
        self.phone_entry.bind('<FocusOut>', self._validate_phone)

        # Age field (number, 0-150)
        ttk.Label(form_frame, text="Age:").grid(
            row=3, column=0, sticky=W, pady=5
        )
        self.age_var = tk.StringVar()

        # Number-only validation
        vcmd = (
            self.register(create_tk_validator(FormValidator.validate_number)),
            '%P'
        )
        self.age_entry = ttk.Entry(
            form_frame,
            textvariable=self.age_var,
            validate='key',
            validatecommand=vcmd,
            width=10
        )
        self.age_entry.grid(row=3, column=1, sticky=W, pady=5, padx=(10, 0))

        form_frame.columnconfigure(1, weight=1)

        # Error display
        self.error_label = ttk.Label(
            form_frame,
            text="",
            foreground="red",
            wraplength=400
        )
        self.error_label.grid(
            row=4, column=0, columnspan=2, pady=10
        )

        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)

        ttk.Button(
            button_frame,
            text="Submit",
            command=self.on_submit,
            bootstyle=PRIMARY
        ).pack(side=LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Clear",
            command=self.clear_form
        ).pack(side=LEFT, padx=5)

    def _validate_name(self, event=None) -> bool:
        """Validate name field."""
        name = self.name_var.get()
        if not FormValidator.validate_length(name, min_length=2):
            self.name_entry.configure(style='Danger.TEntry')
            return False
        self.name_entry.configure(style='TEntry')
        return True

    def _validate_email(self, event=None) -> bool:
        """Validate email field."""
        email = self.email_var.get()
        if email and not FormValidator.validate_email(email):
            self.email_entry.configure(style='Danger.TEntry')
            return False
        self.email_entry.configure(style='TEntry')
        return True

    def _validate_phone(self, event=None) -> bool:
        """Validate phone field (optional)."""
        phone = self.phone_var.get()
        if phone and not FormValidator.validate_phone(phone):
            self.phone_entry.configure(style='Danger.TEntry')
            return False
        self.phone_entry.configure(style='TEntry')
        return True

    def on_submit(self) -> None:
        """Handle form submission with full validation."""
        # Clear previous errors
        self.error_label.config(text="")

        # Validation rules
        rules = {
            'name': [
                FormValidator.validate_not_empty,
                lambda v: FormValidator.validate_length(v, 2)
            ],
            'email': [
                FormValidator.validate_not_empty,
                FormValidator.validate_email
            ],
            'phone': [
                # Optional, but must be valid if provided
                lambda v: not v or FormValidator.validate_phone(v)
            ],
            'age': [
                # Optional, but must be valid range if provided
                lambda v: not v or FormValidator.validate_range(v, 0, 150)
            ]
        }

        # Collect data
        data = {
            'name': self.name_var.get(),
            'email': self.email_var.get(),
            'phone': self.phone_var.get(),
            'age': self.age_var.get()
        }

        # Validate
        is_valid, errors = FormValidator.validate_form(data, rules)

        if is_valid:
            self.controller.on_form_submit(data)
            self.show_success("Form submitted successfully!")
            self.clear_form()
        else:
            self.show_errors(errors)

    def show_errors(self, errors: list[str]) -> None:
        """Display validation errors."""
        self.error_label.config(text="\\n".join(errors))

    def show_success(self, message: str) -> None:
        """Display success message."""
        from tkinter import messagebox
        messagebox.showinfo("Success", message)

    def clear_form(self) -> None:
        """Clear all form fields."""
        self.name_var.set("")
        self.email_var.set("")
        self.phone_var.set("")
        self.age_var.set("")
        self.error_label.config(text="")

        # Reset field styles
        self.name_entry.configure(style='TEntry')
        self.email_entry.configure(style='TEntry')
        self.phone_entry.configure(style='TEntry')
```

## Best Practices

1. **Layer validation**: Real-time + focus-out + submit validation
2. **Visual feedback**: Change entry style on error (Danger.TEntry)
3. **Clear errors**: Display errors in dedicated label
4. **Optional fields**: Check if field has value before validating
5. **Custom validators**: Use lambda for complex rules
6. **Reset on success**: Clear form after successful submission
7. **User-friendly messages**: Show specific error messages

This skill helps you create robust, user-friendly forms with comprehensive validation.
