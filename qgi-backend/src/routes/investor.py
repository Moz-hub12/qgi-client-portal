from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import date
from src.models.user import InvestorData, db

investor_bp = Blueprint("investor", __name__)

def ensure_investor_data(user_id: int) -> InvestorData:
    inv = InvestorData.query.filter_by(user_id=user_id).first()
    if not inv:
        inv = InvestorData(
            user_id=user_id,
            current_value=0,
            total_contributions=0,
            asset_allocation={"Equities":0,"Fixed Income":0,"Real Estate":0,"Commodities":0,"Cash":0},
            nav_history={"points":[]},
            lock_anchor_date=None,
            lock_interval_months=3,
        )
        db.session.add(inv)
        db.session.commit()
    return inv

@investor_bp.get("/dashboard")
@jwt_required()
def get_dashboard():
    uid = int(get_jwt_identity())  # Convert string to int
    inv = ensure_investor_data(uid)
    d = inv.to_dict()
    return jsonify({
        "current_value": d["current_value"],
        "total_contributions": d["total_contributions"],
        "profit_loss": d["profit_loss"],
        "profit_loss_percentage": d["profit_loss_percentage"],
        "asset_allocation": d["asset_allocation"],
        "performance_series": d.get("nav_history") or {"points":[]},
        "next_lock_date": d["next_lock_date"],
        "lock_anchor_date": d["lock_anchor_date"],
    })
