#!/usr/bin/env python3
"""
Photo Judge Tournament CLI

Run photo tournaments using AI evaluation.
"""

import argparse
import sys
import os

from photo_judge.photo_judge import PhotoJudge
from photo_judge.config import Config

def main():
    parser = argparse.ArgumentParser(description='Run photo tournament using AI evaluation')
    parser.add_argument('--photo-dir', '-d', 
                       help='Directory containing photos to evaluate',
                       default=None)
    parser.add_argument('--model', '-m',
                       help='AI model to use for evaluation',
                       default='google/gemini-2.0-flash-exp')
    parser.add_argument('--show-results', '-s',
                       help='Show tournament results',
                       action='store_true')
    
    args = parser.parse_args()
    
    # Create config
    config = Config()
    if args.photo_dir:
        config.PHOTO_DIRECTORY = args.photo_dir
    if args.model:
        config.DEFAULT_MODEL = args.model
    
    # Initialize photo judge
    judge = PhotoJudge(config)
    
    if args.show_results:
        # Load and display existing tournament results
        tournament = judge.load_tournament()
        if tournament:
            print_tournament_results(tournament)
        else:
            print("No tournament results found.")
        return
    
    # Verify photo directory exists
    if not os.path.exists(config.PHOTO_DIRECTORY):
        print(f"Error: Photo directory '{config.PHOTO_DIRECTORY}' not found.")
        print("Please specify a valid photo directory with --photo-dir")
        sys.exit(1)
    
    # Verify API key
    if not config.OPENROUTER_API_KEY:
        print("Warning: OPENROUTER_API_KEY not found in environment variables.")
        print("Tournament will use random scoring for testing.")
        print("Set OPENROUTER_API_KEY environment variable to use AI evaluation.")
    
    try:
        print("Starting photo tournament...")
        tournament = judge.run_full_tournament()
        print_tournament_results(tournament)
        
    except Exception as e:
        print(f"Error running tournament: {e}")
        sys.exit(1)

def print_tournament_results(tournament):
    """Print tournament results in a nice format"""
    print(f"\n{'='*60}")
    print(f"TOURNAMENT RESULTS")
    print(f"{'='*60}")
    print(f"Total Photos: {len(tournament.photos)}")
    print(f"Total Rounds: {tournament.current_round}")
    print(f"Status: {'Completed' if tournament.completed else 'In Progress'}")
    
    # Show final standings
    active_photos = tournament.get_active_photos()
    if active_photos:
        print(f"\nFINAL WINNERS:")
        for i, photo in enumerate(active_photos, 1):
            score_str = f" (Score: {photo.score:.3f})" if photo.score else ""
            print(f"  {i}. {photo.filename}{score_str}")
    
    # Show round-by-round results
    print(f"\nROUND-BY-ROUND RESULTS:")
    for round_obj in tournament.rounds:
        if round_obj.round_number == 0:
            print(f"  Round {round_obj.round_number} (Initial): {len(round_obj.photos_entered)} photos")
        else:
            print(f"  Round {round_obj.round_number}: {len(round_obj.photos_entered)} → {len(round_obj.photos_advanced)} photos")
    
    # Show eliminated photos by round
    print(f"\nELIMINATION BREAKDOWN:")
    for round_num in range(1, tournament.current_round + 1):
        eliminated = [p for p in tournament.photos if p.round_eliminated == round_num]
        if eliminated:
            print(f"  Round {round_num}: {len(eliminated)} eliminated")
            for photo in eliminated:
                score_str = f" (Score: {photo.score:.3f})" if photo.score else ""
                print(f"    - {photo.filename}{score_str}")

if __name__ == '__main__':
    main()