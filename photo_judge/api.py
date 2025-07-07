from flask import Flask, jsonify, send_from_directory, request
import os
import json
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from photo_judge.photo_judge import PhotoJudge
from photo_judge.config import Config

app = Flask(__name__)

# Get web directory path
WEB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'web')

# Initialize photo judge
config = Config()
judge = PhotoJudge(config)

@app.route('/')
def index():
    """Serve the main web interface"""
    return send_from_directory(WEB_DIR, 'index.html')

@app.route('/styles.css')
def styles():
    """Serve CSS file"""
    return send_from_directory(WEB_DIR, 'styles.css')

@app.route('/script.js')
def script():
    """Serve JavaScript file"""
    return send_from_directory(WEB_DIR, 'script.js')

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    print(f"Looking for static file: {filename} in {WEB_DIR}")
    file_path = os.path.join(WEB_DIR, filename)
    print(f"Full path: {file_path}")
    print(f"File exists: {os.path.exists(file_path)}")
    return send_from_directory(WEB_DIR, filename)

@app.route('/api/tournament')
def get_tournament():
    """Get current tournament data"""
    tournament = judge.load_tournament()
    if not tournament:
        return jsonify({'error': 'No tournament data found'}), 404
    
    # Convert tournament to JSON-serializable format
    tournament_data = {
        'photos': [
            {
                'filename': p.filename,
                'path': p.path,
                'created_time': p.created_time.isoformat(),
                'round_eliminated': p.round_eliminated,
                'score': p.score,
                'is_active': p.is_active
            }
            for p in tournament.photos
        ],
        'rounds': [
            {
                'round_number': r.round_number,
                'photos_entered': r.photos_entered,
                'photos_advanced': r.photos_advanced,
                'completed': r.completed
            }
            for r in tournament.rounds
        ],
        'current_round': tournament.current_round,
        'completed': tournament.completed,
        'total_rounds': len(tournament.rounds) - 1  # Exclude initial round
    }
    
    return jsonify(tournament_data)

@app.route('/api/photos/<int:round_number>')
def get_photos_for_round(round_number):
    """Get photos for a specific round"""
    tournament = judge.load_tournament()
    if not tournament:
        return jsonify({'error': 'No tournament data found'}), 404
    
    photos = tournament.get_photos_for_round(round_number)
    
    photo_data = [
        {
            'filename': p.filename,
            'path': p.path,
            'created_time': p.created_time.isoformat(),
            'round_eliminated': p.round_eliminated,
            'score': p.score,
            'is_active': p.is_active
        }
        for p in photos
    ]
    
    return jsonify({
        'round_number': round_number,
        'photos': photo_data,
        'photo_count': len(photo_data)
    })

@app.route('/api/image/<path:filename>')
def serve_image(filename):
    """Serve image files"""
    tournament = judge.load_tournament()
    if not tournament:
        return jsonify({'error': 'No tournament data found'}), 404
    
    # Find the photo by filename
    photo = None
    for p in tournament.photos:
        if p.filename == filename:
            photo = p
            break
    
    if not photo:
        return jsonify({'error': 'Photo not found'}), 404
    
    # Extract directory from photo path
    photo_dir = os.path.dirname(photo.path)
    
    try:
        return send_from_directory(photo_dir, filename)
    except FileNotFoundError:
        return jsonify({'error': 'Image file not found'}), 404

@app.route('/api/status')
def get_status():
    """Get application status"""
    tournament = judge.load_tournament()
    
    status = {
        'has_tournament': tournament is not None,
        'photo_directory': config.PHOTO_DIRECTORY,
        'photo_directory_exists': os.path.exists(config.PHOTO_DIRECTORY),
        'api_key_configured': bool(config.OPENROUTER_API_KEY),
        'model': config.DEFAULT_MODEL
    }
    
    if tournament:
        status.update({
            'tournament_completed': tournament.completed,
            'total_photos': len(tournament.photos),
            'current_round': tournament.current_round,
            'active_photos': len(tournament.get_active_photos())
        })
    
    return jsonify(status)

@app.route('/api/run-tournament', methods=['POST'])
def run_tournament():
    """Run a new tournament"""
    try:
        # Get photo directory from request or use default
        data = request.get_json() or {}
        photo_dir = data.get('photo_directory', config.PHOTO_DIRECTORY)
        
        if not os.path.exists(photo_dir):
            return jsonify({'error': f'Photo directory not found: {photo_dir}'}), 400
        
        # Run tournament
        tournament = judge.run_full_tournament(photo_dir)
        
        return jsonify({
            'success': True,
            'message': 'Tournament completed successfully',
            'total_photos': len(tournament.photos),
            'total_rounds': tournament.current_round,
            'winners': [p.filename for p in tournament.get_active_photos()]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)