import os
import json
import base64
import requests
from typing import List, Tuple
from datetime import datetime
import random
from PIL import Image
import io
import sys

# Add parent directory to path for imports when running as script
if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from .config import Config
    from .models import Photo, Tournament, TournamentRound
except ImportError:
    from config import Config
    from models import Photo, Tournament, TournamentRound

class PhotoJudge:
    """Main class for running photo tournaments using AI evaluation"""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.tournament = None
        
    def load_photos(self, directory: str) -> List[Photo]:
        """Load photos from directory and create Photo objects"""
        photos = []
        supported_formats = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff')
        
        for filename in os.listdir(directory):
            if filename.lower().endswith(supported_formats):
                file_path = os.path.join(directory, filename)
                try:
                    photo = Photo.from_file(file_path)
                    photos.append(photo)
                except Exception as e:
                    print(f"Error loading photo {filename}: {e}")
                    
        # Sort by creation time (oldest first)
        photos.sort(key=lambda p: p.created_time)
        return photos
    
    def create_tournament(self, photos: List[Photo]) -> Tournament:
        """Create a new tournament with given photos"""
        # Create initial round with all photos
        initial_round = TournamentRound(
            round_number=0,
            photos_entered=[p.filename for p in photos],
            photos_advanced=[p.filename for p in photos],
            completed=True
        )
        
        tournament = Tournament(
            photos=photos,
            rounds=[initial_round],
            current_round=0
        )
        
        return tournament
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """Encode image to base64 for API submission"""
        try:
            with Image.open(image_path) as img:
                # Resize if too large to save on API costs
                if img.size[0] > 1024 or img.size[1] > 1024:
                    img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
                
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=85)
                img_str = base64.b64encode(buffer.getvalue()).decode()
                return f"data:image/jpeg;base64,{img_str}"
        except Exception as e:
            print(f"Error encoding image {image_path}: {e}")
            return None
    
    def evaluate_photos(self, photos: List[Photo]) -> List[Tuple[Photo, float]]:
        """Evaluate photos using AI and return sorted by score"""
        if not self.config.OPENROUTER_API_KEY:
            print("Warning: No OpenRouter API key found, using random scoring")
            return [(photo, random.random()) for photo in photos]
        
        scored_photos = []
        
        for photo in photos:
            try:
                score = self.score_photo(photo)
                scored_photos.append((photo, score))
                print(f"Scored {photo.filename}: {score:.3f}")
            except Exception as e:
                print(f"Error scoring {photo.filename}: {e}")
                scored_photos.append((photo, 0.0))
        
        # Sort by score descending
        scored_photos.sort(key=lambda x: x[1], reverse=True)
        return scored_photos
    
    def score_photo(self, photo: Photo) -> float:
        """Score a single photo using AI"""
        image_data = self.encode_image_to_base64(photo.path)
        if not image_data:
            return 0.0
        
        headers = {
            'Authorization': f'Bearer {self.config.OPENROUTER_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': self.config.DEFAULT_MODEL,
            'messages': [
                {
                    'role': 'user',
                    'content': [
                        {
                            'type': 'text',
                            'text': '''Rate this photograph on a scale of 0.0 to 1.0 based on:
                            - Composition and framing
                            - Technical quality (focus, exposure, etc.)
                            - Visual appeal and aesthetics
                            - Emotional impact
                            - Creativity and uniqueness
                            
                            Respond with just a single number between 0.0 and 1.0, no other text.'''
                        },
                        {
                            'type': 'image_url',
                            'image_url': {
                                'url': image_data
                            }
                        }
                    ]
                }
            ],
            'max_tokens': 10
        }
        
        try:
            response = requests.post(
                f'{self.config.OPENROUTER_BASE_URL}/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content'].strip()
                try:
                    score = float(content)
                    return max(0.0, min(1.0, score))  # Clamp between 0 and 1
                except ValueError:
                    print(f"Could not parse score from response: {content}")
                    return 0.0
            else:
                print(f"API request failed: {response.status_code} - {response.text}")
                return 0.0
                
        except Exception as e:
            print(f"Error making API request: {e}")
            return 0.0
    
    def run_tournament_round(self, tournament: Tournament) -> bool:
        """Run a single round of the tournament"""
        active_photos = tournament.get_active_photos()
        
        if len(active_photos) <= 1:
            tournament.completed = True
            return False
        
        print(f"Running round {tournament.current_round + 1} with {len(active_photos)} photos")
        
        # Evaluate all active photos
        scored_photos = self.evaluate_photos(active_photos)
        
        # Determine how many photos advance (at least 1, at most half)
        num_to_advance = max(1, len(active_photos) // 2)
        if num_to_advance < self.config.MIN_PHOTOS_FOR_NEXT_ROUND and len(active_photos) > 2:
            num_to_advance = self.config.MIN_PHOTOS_FOR_NEXT_ROUND
        
        # Update photo scores and elimination status
        for i, (photo, score) in enumerate(scored_photos):
            photo.score = score
            if i >= num_to_advance:
                photo.round_eliminated = tournament.current_round + 1
        
        # Create new round
        advancing_photos = [p.filename for p, _ in scored_photos[:num_to_advance]]
        new_round = TournamentRound(
            round_number=tournament.current_round + 1,
            photos_entered=[p.filename for p in active_photos],
            photos_advanced=advancing_photos,
            completed=True
        )
        
        tournament.rounds.append(new_round)
        tournament.current_round += 1
        
        print(f"Round {tournament.current_round} completed. {len(advancing_photos)} photos advance.")
        
        return True
    
    def run_full_tournament(self, directory: str = None) -> Tournament:
        """Run a complete tournament from start to finish"""
        directory = directory or self.config.PHOTO_DIRECTORY
        
        print(f"Loading photos from {directory}")
        photos = self.load_photos(directory)
        
        if not photos:
            raise ValueError(f"No photos found in {directory}")
        
        print(f"Loaded {len(photos)} photos")
        
        tournament = self.create_tournament(photos)
        
        # Run rounds until tournament is complete
        while not tournament.completed and self.run_tournament_round(tournament):
            pass
        
        print(f"Tournament completed after {tournament.current_round} rounds")
        
        # Save tournament results
        self.save_tournament(tournament)
        
        return tournament
    
    def save_tournament(self, tournament: Tournament):
        """Save tournament results to file"""
        data = {
            'photos': [
                {
                    'filename': p.filename,
                    'path': p.path,
                    'created_time': p.created_time.isoformat(),
                    'round_eliminated': p.round_eliminated,
                    'score': p.score
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
            'completed': tournament.completed
        }
        
        with open(self.config.TOURNAMENT_DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Tournament results saved to {self.config.TOURNAMENT_DATA_FILE}")
    
    def load_tournament(self) -> Tournament:
        """Load tournament results from file"""
        if not os.path.exists(self.config.TOURNAMENT_DATA_FILE):
            return None
        
        with open(self.config.TOURNAMENT_DATA_FILE, 'r') as f:
            data = json.load(f)
        
        # Reconstruct photos
        photos = []
        for photo_data in data['photos']:
            photo = Photo(
                path=photo_data['path'],
                filename=photo_data['filename'],
                created_time=datetime.fromisoformat(photo_data['created_time']),
                round_eliminated=photo_data.get('round_eliminated'),
                score=photo_data.get('score')
            )
            photos.append(photo)
        
        # Reconstruct rounds
        rounds = []
        for round_data in data['rounds']:
            round_obj = TournamentRound(
                round_number=round_data['round_number'],
                photos_entered=round_data['photos_entered'],
                photos_advanced=round_data['photos_advanced'],
                completed=round_data['completed']
            )
            rounds.append(round_obj)
        
        tournament = Tournament(
            photos=photos,
            rounds=rounds,
            current_round=data['current_round'],
            completed=data['completed']
        )
        
        return tournament