from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from dateutil.relativedelta import relativedelta  # pip install python-dateutil
import json

db = SQLAlchemy()

# --------------------------- User ---------------------------

class User(db.Model):
    __tablename__ = "user"  # explicit for FK clarity

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    # Profile and KYC data stored as JSON strings (kept as-is for compatibility)
    profile_data = db.Column(db.Text, nullable=True)   # JSON string
    kyc_status = db.Column(db.String(20), default="pending")  # pending, approved, rejected
    kyc_documents = db.Column(db.Text, nullable=True)  # JSON string for document paths

    # Investor-specific fields
    is_investor = db.Column(db.Boolean, default=True)
    investor_id = db.Column(db.String(50), unique=True, nullable=True)

    # NEW: role for admin portal (client | admin | superadmin)
    role = db.Column(db.String(16), nullable=False, default="client")

    def __repr__(self):
        return f"<User {self.username}>"

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "profile_data": json.loads(self.profile_data) if self.profile_data else {},
            "kyc_status": self.kyc_status,
            "is_investor": self.is_investor,
            "investor_id": self.investor_id,
            "role": self.role,
        }

    def update_profile_data(self, data):
        """Update profile data with new information"""
        current_data = json.loads(self.profile_data) if self.profile_data else {}
        current_data.update(data)
        self.profile_data = json.dumps(current_data)

    def get_profile_data(self):
        """Get profile data as dictionary"""
        return json.loads(self.profile_data) if self.profile_data else {}


# ----------------------- InvestorData -----------------------

class InvestorData(db.Model):
    """
    Investor-specific financial data (one row per user).
    Currency fields use NUMERIC (exact) instead of float.
    Lock schedule: next lock date is computed from lock_anchor_date every N months.
    """
    __tablename__ = "investor_data"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        unique=True,              # enforce 1:1 with user
        nullable=False,
    )

    # Editable metrics
    current_value = db.Column(db.Numeric(18, 2))
    total_contributions = db.Column(db.Numeric(18, 2))

    # Charts & allocation (stored as JSON)
    # Example allocation: {"Equities":45,"Fixed Income":25,"Real Estate":15,"Commodities":10,"Cash":5}
    asset_allocation = db.Column(db.JSON)
    # Example series: {"points":[{"date":"2025-01-31","value":81234.56}, ...]}
    nav_history = db.Column(db.JSON)

    # Lock schedule
    lock_anchor_date = db.Column(db.Date)                 # first lock date you choose
    lock_interval_months = db.Column(db.SmallInteger, default=3)

    # Bookkeeping
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = db.relationship("User", backref=db.backref("investor_data", uselist=False, cascade="all, delete-orphan"))

    # -------- Computed metrics --------
    @property
    def profit_loss(self):
        if self.current_value is None or self.total_contributions is None:
            return None
        return float(self.current_value) - float(self.total_contributions)

    @property
    def profit_loss_percentage(self):
        if not self.total_contributions:
            return 0.0
        if self.profit_loss is None:
            return 0.0
        try:
            return (self.profit_loss / float(self.total_contributions)) * 100.0
        except ZeroDivisionError:
            return 0.0

    def next_lock_date(self, today: date | None = None):
        """
        Next lock date >= today, repeating every lock_interval_months from lock_anchor_date.
        """
        if not self.lock_anchor_date:
            return None
        if today is None:
            today = date.today()
        months = max(1, int(self.lock_interval_months or 3))
        d = self.lock_anchor_date
        while d < today:
            d = d + relativedelta(months=+months)
        return d

    # -------- Serialization helpers --------
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "current_value": float(self.current_value) if self.current_value is not None else None,
            "total_contributions": float(self.total_contributions) if self.total_contributions is not None else None,
            "profit_loss": self.profit_loss,
            "profit_loss_percentage": self.profit_loss_percentage,
            "lock_anchor_date": self.lock_anchor_date.isoformat() if self.lock_anchor_date else None,
            "lock_interval_months": int(self.lock_interval_months or 3),
            "next_lock_date": self.next_lock_date().isoformat() if self.next_lock_date() else None,
            "nav_history": self.nav_history or [],   # list of points
            "asset_allocation": self.asset_allocation or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    # -------- Mutators --------
    def update_nav_history(self, nav_data_point: dict):
        """
        Append a new NAV data point to history.
        Keeps the last 365 points.
        nav_data_point example: {"date": "2025-08-31", "value": 81234.56}
        """
        history = self.nav_history or []
        history.append(nav_data_point)
        if len(history) > 365:
            history = history[-365:]
        self.nav_history = history
