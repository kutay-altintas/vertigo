from flask import Blueprint, request, jsonify
from .models import Clan
from . import db

bp = Blueprint('clans', __name__)

def clan_to_dict(clan: Clan) -> dict:
    return {
        "id": clan.id,
        "name": clan.name,
        "region": clan.region,
        "created_at": clan.created_at.isoformat()
    }

@bp.route('/clans', methods=['POST'])
def create_clan():
    data = request.get_json(silent=True) or {}

    name = data.get("name")
    region = data.get("region")

    if not name:
        return jsonify({"error": "Clan name is required"}), 400
    
    if not region or len(region) != 2:
        return jsonify({"error": "Region code must be a 2-letter string"}), 400
    
    clan = Clan(name=name, region=region)
    db.session.add(clan)
    db.session.commit()

    return jsonify(clan_to_dict(clan)), 201

@bp.route('/clans', methods=['GET'])
def list_clans():
    clans = Clan.query.order_by(Clan.created_at.desc()).all()
    return jsonify([clan_to_dict(clan) for clan in clans]), 200


@bp.route('/clans/search', methods=['GET'])
def search_clans():
    q = request.args.get('name', '', type=str)

    if len(q) < 3:
        return jsonify({"error": "Search query must be at least 3 characters long"}), 400
    
    #ILIKE is case-insensitive in many databases like PostgreSQL
    clans = Clan.query.filter(Clan.name.ilike(f'%{q}%')).order_by(Clan.created_at.desc()).all()
    return jsonify([clan_to_dict(clan) for clan in clans]), 200


@bp.route('/clans/<string:clan_id>', methods=['DELETE'])
def delete_clan(clan_id: str):
    clan = Clan.query.get(clan_id)
    if not clan:
        return jsonify({"error": "Clan not found"}), 404
    
    db.session.delete(clan)
    db.session.commit()
    return jsonify({"message": "Clan deleted successfully"}), 200