from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
import os

@dataclass
class Photo:
    """Represents a photo in the tournament"""
    path: str
    filename: str
    created_time: datetime
    round_eliminated: Optional[int] = None
    score: Optional[float] = None
    
    @property
    def is_active(self) -> bool:
        """Returns True if photo is still active in tournament"""
        return self.round_eliminated is None
    
    @classmethod
    def from_file(cls, file_path: str) -> 'Photo':
        """Create Photo instance from file path"""
        stat = os.stat(file_path)
        created_time = datetime.fromtimestamp(stat.st_mtime)
        filename = os.path.basename(file_path)
        
        return cls(
            path=file_path,
            filename=filename,
            created_time=created_time
        )

@dataclass
class TournamentRound:
    """Represents a round in the tournament"""
    round_number: int
    photos_entered: List[str]  # photo filenames
    photos_advanced: List[str]  # photo filenames that advanced
    completed: bool = False
    
@dataclass
class Tournament:
    """Represents the complete tournament state"""
    photos: List[Photo]
    rounds: List[TournamentRound]
    current_round: int = 0
    completed: bool = False
    
    def get_photos_for_round(self, round_number: int) -> List[Photo]:
        """Get photos that were active in a specific round"""
        if round_number == 0:
            return self.photos
        
        # Get photos that were eliminated after this round or are still active
        return [p for p in self.photos if p.round_eliminated is None or p.round_eliminated >= round_number]
    
    def get_active_photos(self) -> List[Photo]:
        """Get photos that are still active in the tournament"""
        return [p for p in self.photos if p.is_active]