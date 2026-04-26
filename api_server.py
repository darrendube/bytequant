"""
ByteQuant API Server
Provides REST endpoints for the dashboard frontend
Runs on EC2 instance and exposes portfolio, strategies, and equity curve data
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Import ByteQuant modules
from src.data.db import crud
from src.data.db.session import engine
from src.data.db.models import Base
from src.exec.broker import AlpacaClient

# Initialize database
Base.metadata.create_all(bind=engine)
broker = AlpacaClient()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}), 200


@app.route('/api/bytequant/portfolio', methods=['GET'])
def get_portfolio():
    """
    Get current portfolio snapshot
    Returns: total_value, cash, positions_count, account_status
    """
    try:
        # Get account info from Alpaca
        account_summary = broker.account_summary()
        
        # Get active positions count from database
        active_positions = crud.get_positions(status='active')
        positions_count = len(active_positions) if active_positions else 0
        
        # Get latest equity curve entry from database
        from src.data.db.models import EquityCurve
        from src.data.db.session import SessionLocal
        db_session = SessionLocal()
        latest_equity = db_session.query(EquityCurve).order_by(
            EquityCurve.timestamp.desc()
        ).first()
        db_session.close()
        
        total_value = float(account_summary['equity']) if latest_equity is None else float(latest_equity.total_value)
        cash = float(account_summary['cash'])
        
        return jsonify({
            'total_value': total_value,
            'cash': cash,
            'positions_count': positions_count,
            'account_status': account_summary['status'],
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching portfolio: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/bytequant/equity-curve', methods=['GET'])
def get_equity_curve():
    """
    Get historical equity curve data
    Query params:
        - days: number of days to return (default: 30)
        - interval: data point interval in minutes (default: 60)
    """
    try:
        days = request.args.get('days', 30, type=int)
        
        from src.data.db.models import EquityCurve
        from src.data.db.session import SessionLocal
        
        db_session = SessionLocal()
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        equity_history = db_session.query(EquityCurve).filter(
            EquityCurve.timestamp >= cutoff_date
        ).order_by(EquityCurve.timestamp).all()
        
        db_session.close()
        
        data = [
            {
                'timestamp': point.timestamp.isoformat() if point.timestamp else datetime.utcnow().isoformat(),
                'total_value': float(point.total_value),
                'cash': float(point.cash) if point.cash else 0
            }
            for point in equity_history
        ]
        
        return jsonify({'data': data}), 200
        
    except Exception as e:
        logger.error(f"Error fetching equity curve: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/bytequant/strategies', methods=['GET'])
def get_strategies():
    """
    Get all active strategies
    """
    try:
        strategies = crud.get_strategies()
        
        if not strategies:
            return jsonify({'data': []}), 200
        
        from src.data.db.models import Strategy
        
        # Filter for active strategies if it's a list
        if isinstance(strategies, list):
            active_strategies = [s for s in strategies if s.status == 'active']
        else:
            # Single strategy returned
            active_strategies = [strategies] if strategies.status == 'active' else []
        
        data = [
            {
                'strategy_id': s.strategy_id,
                'name': s.name,
                'status': s.status,
                'parameters': s.parameters if s.parameters else {},
                'started_at': s.started_at.isoformat() if s.started_at else None
            }
            for s in active_strategies
        ]
        
        return jsonify({'data': data}), 200
        
    except Exception as e:
        logger.error(f"Error fetching strategies: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/bytequant/positions', methods=['GET'])
def get_positions():
    """
    Get all active positions with current market prices
    """
    try:
        active_positions = crud.get_positions(status='active')
        
        if not active_positions:
            return jsonify({'data': []}), 200
        
        positions_data = []
        for pos in active_positions:
            try:
                current_price = broker.get_market_price(pos.symbol)
                current_value = current_price * pos.qty if current_price else 0
                entry_value = pos.entry_price * pos.qty
                pnl = current_value - entry_value if current_price else 0
                pnl_percent = (pnl / entry_value * 100) if entry_value > 0 else 0
                
                positions_data.append({
                    'symbol': pos.symbol,
                    'side': pos.side,
                    'qty': pos.qty,
                    'entry_price': float(pos.entry_price),
                    'current_price': float(current_price) if current_price else 0,
                    'current_value': float(current_value),
                    'pnl': float(pnl),
                    'pnl_percent': float(pnl_percent)
                })
            except Exception as e:
                logger.warning(f"Error fetching price for {pos.symbol}: {str(e)}")
                positions_data.append({
                    'symbol': pos.symbol,
                    'side': pos.side,
                    'qty': pos.qty,
                    'entry_price': float(pos.entry_price),
                    'current_price': 0,
                    'current_value': 0,
                    'pnl': 0,
                    'pnl_percent': 0,
                    'error': 'Unable to fetch current price'
                })
        
        return jsonify({'data': positions_data}), 200
        
    except Exception as e:
        logger.error(f"Error fetching positions: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/bytequant/trades', methods=['GET'])
def get_trades():
    """
    Get recent trades
    Query params:
        - limit: number of trades to return (default: 50)
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        
        from src.data.db.models import Trade
        from src.data.db.session import SessionLocal
        
        db_session = SessionLocal()
        trades = db_session.query(Trade).order_by(
            Trade.time.desc()
        ).limit(limit).all()
        
        db_session.close()
        
        data = [
            {
                'trade_id': t.trade_id,
                'symbol': t.symbol,
                'qty': t.qty,
                'price': float(t.price),
                'commission': float(t.commission) if t.commission else 0,
                'timestamp': t.time.isoformat() if t.time else None
            }
            for t in trades
        ]
        
        return jsonify({'data': data}), 200
        
    except Exception as e:
        logger.error(f"Error fetching trades: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    port = int(os.getenv('API_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting ByteQuant API Server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
