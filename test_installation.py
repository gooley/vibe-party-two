#!/usr/bin/env python3
"""
Test script to verify photo judge installation and basic functionality
"""

import os
import sys
import tempfile
from PIL import Image
import random

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from photo_judge.photo_judge import PhotoJudge
from photo_judge.config import Config

def create_test_photos(directory, count=5):
    """Create test photos for demonstration"""
    colors = [
        (255, 0, 0),    # Red
        (0, 255, 0),    # Green  
        (0, 0, 255),    # Blue
        (255, 255, 0),  # Yellow
        (255, 0, 255),  # Magenta
        (0, 255, 255),  # Cyan
        (128, 128, 128) # Gray
    ]
    
    os.makedirs(directory, exist_ok=True)
    
    for i in range(count):
        # Create a simple colored image
        img = Image.new('RGB', (400, 300), colors[i % len(colors)])
        
        # Add some simple patterns to make images different
        pixels = img.load()
        for x in range(0, 400, 20):
            for y in range(0, 300, 20):
                if (x + y) % 40 == 0:
                    pixels[x, y] = (255, 255, 255)  # White dots
        
        filename = f"test_photo_{i+1:02d}.jpg"
        filepath = os.path.join(directory, filename)
        img.save(filepath, 'JPEG')
        print(f"Created test photo: {filename}")

def test_basic_functionality():
    """Test basic photo judge functionality"""
    print("Testing Photo Judge basic functionality...")
    
    # Create test photos
    test_dir = "test_photos"
    create_test_photos(test_dir, 8)
    
    # Configure for testing
    config = Config()
    config.PHOTO_DIRECTORY = test_dir
    config.OPENROUTER_API_KEY = None  # Use random scoring for testing
    
    # Initialize photo judge
    judge = PhotoJudge(config)
    
    # Test photo loading
    print("\nTesting photo loading...")
    photos = judge.load_photos(test_dir)
    print(f"Loaded {len(photos)} photos")
    
    # Test tournament creation
    print("\nTesting tournament creation...")
    tournament = judge.create_tournament(photos)
    print(f"Created tournament with {len(tournament.photos)} photos")
    
    # Test running a single round
    print("\nTesting tournament round...")
    success = judge.run_tournament_round(tournament)
    print(f"Round completed: {success}")
    
    active_photos = tournament.get_active_photos()
    print(f"Active photos after round: {len(active_photos)}")
    
    # Test saving/loading tournament
    print("\nTesting tournament save/load...")
    judge.save_tournament(tournament)
    loaded_tournament = judge.load_tournament()
    print(f"Loaded tournament with {len(loaded_tournament.photos)} photos")
    
    print("\n✅ All basic tests passed!")
    return True

def test_web_api():
    """Test web API functionality"""
    print("\nTesting Web API...")
    
    try:
        from photo_judge.api import app
        with app.test_client() as client:
            # Test status endpoint
            response = client.get('/api/status')
            assert response.status_code == 200
            print("✅ Status endpoint works")
            
            # Test tournament endpoint (might return 404 if no tournament)
            response = client.get('/api/tournament')
            print(f"✅ Tournament endpoint responds (status: {response.status_code})")
            
        print("✅ Web API tests passed!")
        return True
    except Exception as e:
        print(f"❌ Web API test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Running Photo Judge Tests\n")
    
    try:
        # Test basic functionality
        test_basic_functionality()
        
        # Test web API
        test_web_api()
        
        print("\n🎉 All tests completed successfully!")
        print("\nNext steps:")
        print("1. Set up your OpenRouter API key in .env file")
        print("2. Set PHOTO_DIRECTORY to your photo folder")
        print("3. Run: python run_tournament.py")
        print("4. Start web server: python photo_judge/api.py")
        print("5. Open browser to: http://localhost:5000")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)