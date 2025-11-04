---
description: Create comprehensive SQLAlchemy model validation including field validators, relationship validators, constraints, and business rule enforcement
allowed-tools: [Read, Write, Grep]
---

This skill provides patterns for comprehensive data validation at the SQLAlchemy model level.

## When This Skill Activates

Automatically activates when:
- Defining new models
- Adding validation rules
- Ensuring data integrity
- Implementing business logic at model level

## Field-Level Validation

### Using SQLAlchemy Validators

```python
from sqlalchemy.orm import validates
from sqlalchemy.exc import IntegrityError
from app.extensions import db
import re

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer)
    website = db.Column(db.String(200))

    @validates('username')
    def validate_username(self, key, username):
        """Validate username format."""
        if not username:
            raise ValueError('Username cannot be empty')

        if len(username) < 3:
            raise ValueError('Username must be at least 3 characters')

        if len(username) > 80:
            raise ValueError('Username cannot exceed 80 characters')

        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValueError('Username can only contain letters, numbers, and underscores')

        return username

    @validates('email')
    def validate_email(self, key, email):
        """Validate email format."""
        if not email:
            raise ValueError('Email cannot be empty')

        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValueError('Invalid email format')

        return email.lower()  # Normalize to lowercase

    @validates('age')
    def validate_age(self, key, age):
        """Validate age range."""
        if age is not None:
            if age < 0:
                raise ValueError('Age cannot be negative')
            if age > 150:
                raise ValueError('Invalid age')

        return age

    @validates('website')
    def validate_website(self, key, website):
        """Validate URL format."""
        if website:
            url_pattern = r'^https?://.+'
            if not re.match(url_pattern, website):
                raise ValueError('Website must be a valid URL starting with http:// or https://')

        return website
```

## Database Constraints

### Column-Level Constraints

```python
class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)

    # NOT NULL constraint
    name = db.Column(db.String(100), nullable=False)

    # UNIQUE constraint
    sku = db.Column(db.String(50), unique=True, nullable=False)

    # CHECK constraint (PostgreSQL, MySQL)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)

    # Default values
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.CheckConstraint('price >= 0', name='positive_price'),
        db.CheckConstraint('quantity >= 0', name='positive_quantity'),
        db.Index('idx_product_sku', 'sku'),  # Index for faster lookups
    )

    @validates('price')
    def validate_price(self, key, price):
        """Additional validation for price."""
        if price < 0:
            raise ValueError('Price cannot be negative')
        if price > 1000000:
            raise ValueError('Price exceeds maximum allowed value')
        return price
```

### Composite Unique Constraints

```python
class UserSettings(db.Model):
    __tablename__ = 'user_settings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    setting_key = db.Column(db.String(50), nullable=False)
    setting_value = db.Column(db.String(200))

    # Composite unique constraint
    __table_args__ = (
        db.UniqueConstraint('user_id', 'setting_key', name='unique_user_setting'),
    )
```

## Hybrid Properties

### Computed Fields with Validation

```python
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    @hybrid_property
    def full_name(self):
        """Computed full name."""
        return f"{self.first_name} {self.last_name}"

    @full_name.expression
    def full_name(cls):
        """Enable querying by full_name."""
        from sqlalchemy import func
        return func.concat(cls.first_name, ' ', cls.last_name)

    @hybrid_property
    def is_premium(self):
        """Check if user has premium subscription."""
        return self.subscription_tier == 'premium'

    @hybrid_method
    def has_role(self, role):
        """Check if user has specific role."""
        return self.role == role

# Query using hybrid properties
premium_users = User.query.filter(User.is_premium == True).all()
users = User.query.filter(User.has_role('admin')).all()
```

## Relationship Validation

```python
class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationship with validation
    user = db.relationship('User', backref=db.backref('posts', lazy='dynamic'))
    comments = db.relationship('Comment', backref='post', cascade='all, delete-orphan')

    @validates('user')
    def validate_user(self, key, user):
        """Validate user relationship."""
        if not user:
            raise ValueError('Post must have an author')

        if not user.is_active:
            raise ValueError('Cannot assign post to inactive user')

        return user

    @validates('comments')
    def validate_comments(self, key, comment):
        """Validate comments."""
        if len(self.comments) >= 1000:
            raise ValueError('Post has reached maximum number of comments')

        return comment
```

## Custom Validation Methods

```python
class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False)
    items = db.relationship('OrderItem', backref='order', cascade='all, delete-orphan')

    def validate(self):
        """Comprehensive validation before saving."""
        errors = []

        # Validate total amount
        if self.total_amount < 0:
            errors.append('Total amount cannot be negative')

        # Validate items
        if not self.items:
            errors.append('Order must have at least one item')

        # Validate item total matches order total
        items_total = sum(item.price * item.quantity for item in self.items)
        if abs(items_total - self.total_amount) > 0.01:  # Allow for floating point errors
            errors.append('Order total does not match sum of items')

        # Validate status transitions
        valid_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
        if self.status not in valid_statuses:
            errors.append(f'Invalid status: {self.status}')

        if errors:
            raise ValueError('; '.join(errors))

        return True

    def can_cancel(self):
        """Check if order can be cancelled."""
        return self.status in ['pending', 'processing']

    def cancel(self):
        """Cancel order with validation."""
        if not self.can_cancel():
            raise ValueError(f'Cannot cancel order with status: {self.status}')

        self.status = 'cancelled'
        db.session.commit()

# Usage
try:
    order.validate()
    db.session.commit()
except ValueError as e:
    db.session.rollback()
    print(f'Validation error: {e}')
```

## Model Mixins for Common Validation

```python
# app/models/mixins.py
from datetime import datetime
from app.extensions import db

class TimestampMixin:
    """Add created_at and updated_at with validation."""
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    @validates('created_at', 'updated_at')
    def validate_timestamp(self, key, timestamp):
        """Ensure timestamps are not in the future."""
        if timestamp and timestamp > datetime.utcnow():
            raise ValueError(f'{key} cannot be in the future')
        return timestamp

class SoftDeleteMixin:
    """Soft delete with validation."""
    deleted_at = db.Column(db.DateTime, nullable=True)
    is_deleted = db.Column(db.Boolean, default=False, index=True)

    def soft_delete(self):
        """Mark as deleted with validation."""
        if self.is_deleted:
            raise ValueError('Record is already deleted')

        self.deleted_at = datetime.utcnow()
        self.is_deleted = True
        db.session.commit()

    def restore(self):
        """Restore deleted record."""
        if not self.is_deleted:
            raise ValueError('Record is not deleted')

        self.deleted_at = None
        self.is_deleted = False
        db.session.commit()

# Usage
class User(db.Model, TimestampMixin, SoftDeleteMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
```

## Business Rule Validation

```python
class BankAccount(db.Model):
    __tablename__ = 'bank_accounts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    balance = db.Column(db.Numeric(15, 2), default=0, nullable=False)
    account_type = db.Column(db.String(20), nullable=False)  # checking, savings
    overdraft_limit = db.Column(db.Numeric(10, 2), default=0)

    def deposit(self, amount):
        """Deposit money with validation."""
        if amount <= 0:
            raise ValueError('Deposit amount must be positive')

        if amount > 1000000:
            raise ValueError('Deposit exceeds maximum allowed amount')

        self.balance += amount
        db.session.commit()

    def withdraw(self, amount):
        """Withdraw money with validation."""
        if amount <= 0:
            raise ValueError('Withdrawal amount must be positive')

        # Check overdraft protection
        available_balance = self.balance + self.overdraft_limit

        if amount > available_balance:
            raise ValueError('Insufficient funds')

        # Savings accounts have withdrawal limits
        if self.account_type == 'savings':
            # Check withdrawal count this month
            monthly_withdrawals = self.get_monthly_withdrawal_count()
            if monthly_withdrawals >= 6:
                raise ValueError('Savings account withdrawal limit reached for this month')

        self.balance -= amount
        db.session.commit()

    def transfer(self, to_account, amount):
        """Transfer money between accounts."""
        if to_account.id == self.id:
            raise ValueError('Cannot transfer to same account')

        self.withdraw(amount)  # Validates withdrawal
        to_account.deposit(amount)  # Validates deposit
```

This skill ensures robust data validation at the model level, maintaining data integrity.
