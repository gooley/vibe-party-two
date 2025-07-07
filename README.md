# Photo Judge Tournament

An AI-powered photo tournament app that evaluates photos using AI models and runs tournament-style competitions to find the best photos.

## Features

- **AI-Powered Evaluation**: Uses OpenRouter API with models like Gemini 2.0 Flash for photo scoring
- **Tournament System**: Progressive elimination tournament with multiple rounds
- **Web Interface**: Simple web UI with slider to view different tournament rounds
- **CLI Interface**: Command-line tool for running tournaments
- **Time-Sorted Display**: Photos displayed in chronological order
- **Progressive Filtering**: Slider allows viewing photos from different tournament rounds

## Setup

### Prerequisites

- Python 3.8+
- OpenRouter API key (optional, will use random scoring without it)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd vibe-party-two
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
OPENROUTER_API_KEY=your_openrouter_api_key_here
PHOTO_DIRECTORY=/path/to/your/photos
```

### Configuration

Edit the configuration in `photo_judge/config.py`:

- `OPENROUTER_API_KEY`: Your OpenRouter API key
- `DEFAULT_MODEL`: AI model to use (default: `google/gemini-2.0-flash-exp`)
- `PHOTO_DIRECTORY`: Directory containing your photos
- `TOURNAMENT_BRACKET_SIZE`: Number of photos per comparison round
- `MIN_PHOTOS_FOR_NEXT_ROUND`: Minimum photos to advance to next round

## Usage

### Running a Tournament (CLI)

```bash
# Run tournament with default settings
python run_tournament.py

# Specify photo directory
python run_tournament.py --photo-dir /path/to/photos

# Use different AI model
python run_tournament.py --model google/gemini-2.0-flash-exp

# Show existing tournament results
python run_tournament.py --show-results
```

### Web Interface

1. Start the web server:
```bash
python photo_judge/api.py
```

2. Open your browser to `http://localhost:5000`

3. Use the web interface to:
   - Run tournaments
   - View tournament results
   - Use the slider to see photos from different rounds
   - Progressive filtering from all photos to final winners

### Web Interface Features

- **Tournament Controls**: Run new tournaments or refresh data
- **Round Slider**: 
  - Left (Round 0): Shows all photos in time-sorted order
  - Right (Later Rounds): Shows progressively filtered photos
- **Photo Display**: Shows photos with scores, elimination status, and creation dates
- **Tournament Info**: Displays current tournament status and statistics

## How It Works

1. **Photo Loading**: Loads all photos from specified directory, sorted by creation time
2. **AI Evaluation**: Each photo is scored by AI based on:
   - Composition and framing
   - Technical quality (focus, exposure, etc.)
   - Visual appeal and aesthetics
   - Emotional impact
   - Creativity and uniqueness
3. **Tournament Rounds**: 
   - Photos compete in elimination rounds
   - Top-scoring photos advance to next round
   - Process continues until winners are determined
4. **Results Storage**: Tournament results saved to `tournament_results.json`

## File Structure

```
vibe-party-two/
├── photo_judge/
│   ├── __init__.py
│   ├── config.py          # Configuration settings
│   ├── models.py          # Data models
│   ├── photo_judge.py     # Core tournament logic
│   └── api.py            # Web API server
├── web/
│   ├── index.html        # Web interface
│   ├── styles.css        # CSS styles
│   └── script.js         # JavaScript functionality
├── run_tournament.py     # CLI interface
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## API Endpoints

- `GET /` - Web interface
- `GET /api/tournament` - Get tournament data
- `GET /api/photos/<round>` - Get photos for specific round
- `GET /api/image/<filename>` - Serve photo files
- `GET /api/status` - Application status
- `POST /api/run-tournament` - Run new tournament

## Development

### Testing Without API Key

The app will use random scoring if no OpenRouter API key is provided, allowing you to test the tournament mechanics.

### Adding New Models

Edit `config.py` to change the `DEFAULT_MODEL` setting. Any OpenRouter-compatible model can be used.

### Customizing Tournament Logic

Modify `photo_judge.py` to adjust:
- Scoring criteria
- Elimination rules
- Round progression logic
- Photo selection algorithms

## License

MIT License - see LICENSE file for details.