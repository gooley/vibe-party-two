// Photo Judge Tournament JavaScript

class PhotoTournament {
    constructor() {
        this.tournament = null;
        this.currentRound = 0;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadTournamentData();
    }

    bindEvents() {
        // Button events
        document.getElementById('runTournament').addEventListener('click', () => this.runTournament());
        document.getElementById('refreshData').addEventListener('click', () => this.loadTournamentData());
        
        // Slider events
        document.getElementById('roundSlider').addEventListener('input', (e) => {
            this.currentRound = parseInt(e.target.value);
            this.updateSliderLabel();
            this.loadPhotosForRound(this.currentRound);
        });
    }

    async loadTournamentData() {
        try {
            this.showLoading(true);
            const response = await fetch('/api/tournament');
            
            if (response.ok) {
                this.tournament = await response.json();
                this.updateTournamentInfo();
                this.updateSlider();
                this.loadPhotosForRound(this.currentRound);
            } else {
                console.log('No tournament data found');
                this.showStatus('No tournament data found. Run a tournament first.', 'warning');
            }
        } catch (error) {
            console.error('Error loading tournament data:', error);
            this.showStatus('Error loading tournament data', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async runTournament() {
        if (!confirm('This will start a new tournament. Are you sure?')) {
            return;
        }

        try {
            this.showLoading(true);
            this.showStatus('Running tournament... This may take a while.', 'warning');
            
            const response = await fetch('/api/run-tournament', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const result = await response.json();
            
            if (response.ok) {
                this.showStatus(`Tournament completed! ${result.total_photos} photos, ${result.total_rounds} rounds`, 'success');
                await this.loadTournamentData();
            } else {
                this.showStatus(`Error: ${result.error}`, 'error');
            }
        } catch (error) {
            console.error('Error running tournament:', error);
            this.showStatus('Error running tournament', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async loadPhotosForRound(roundNumber) {
        try {
            const response = await fetch(`/api/photos/${roundNumber}`);
            
            if (response.ok) {
                const data = await response.json();
                this.displayPhotos(data.photos, roundNumber);
                this.updatePhotoCount(data.photo_count);
            } else {
                console.error('Error loading photos for round:', roundNumber);
            }
        } catch (error) {
            console.error('Error loading photos:', error);
        }
    }

    displayPhotos(photos, roundNumber) {
        const grid = document.getElementById('photoGrid');
        grid.innerHTML = '';

        // Sort photos by creation time (oldest first)
        photos.sort((a, b) => new Date(a.created_time) - new Date(b.created_time));

        photos.forEach(photo => {
            const photoElement = this.createPhotoElement(photo, roundNumber);
            grid.appendChild(photoElement);
        });
    }

    createPhotoElement(photo, roundNumber) {
        const div = document.createElement('div');
        div.className = 'photo-item';
        
        // Determine photo status
        let statusClass = '';
        let statusText = '';
        
        if (photo.is_active) {
            statusClass = 'photo-active';
            statusText = 'Active';
        } else if (photo.round_eliminated) {
            statusClass = 'photo-eliminated';
            statusText = `Eliminated Round ${photo.round_eliminated}`;
        }

        const scoreDisplay = photo.score ? `Score: ${photo.score.toFixed(3)}` : '';
        const createdDate = new Date(photo.created_time).toLocaleDateString();

        div.innerHTML = `
            <img src="/api/image/${encodeURIComponent(photo.filename)}" alt="${photo.filename}" loading="lazy">
            <div class="photo-info">
                <h4>${photo.filename}</h4>
                <div class="photo-details">
                    <span>Date: ${createdDate}</span>
                    <span class="photo-score">${scoreDisplay}</span>
                </div>
                <div class="photo-details">
                    <span class="${statusClass}">${statusText}</span>
                </div>
            </div>
        `;

        return div;
    }

    updateTournamentInfo() {
        if (!this.tournament) return;

        document.getElementById('tournamentStatus').textContent = 
            this.tournament.completed ? 'Completed' : 'In Progress';
        
        document.getElementById('currentRound').textContent = this.tournament.current_round;
        document.getElementById('activePhotos').textContent = 
            this.tournament.photos.filter(p => p.is_active).length;
    }

    updateSlider() {
        if (!this.tournament) return;

        const slider = document.getElementById('roundSlider');
        const maxRound = this.tournament.total_rounds;
        
        slider.max = maxRound;
        slider.value = this.currentRound;
        
        this.updateSliderLabel();
    }

    updateSliderLabel() {
        const label = document.getElementById('sliderLabel');
        
        if (this.currentRound === 0) {
            label.textContent = 'Round 0 (All Photos)';
        } else {
            label.textContent = `Round ${this.currentRound}`;
        }
    }

    updatePhotoCount(count) {
        document.getElementById('photoCount').textContent = `${count} photos`;
    }

    showStatus(message, type = 'info') {
        const statusElement = document.getElementById('status');
        statusElement.textContent = message;
        statusElement.className = `status ${type}`;
        
        // Clear status after 5 seconds
        setTimeout(() => {
            statusElement.textContent = '';
            statusElement.className = 'status';
        }, 5000);
    }

    showLoading(show) {
        const loadingElement = document.getElementById('loading');
        if (show) {
            loadingElement.classList.remove('hidden');
        } else {
            loadingElement.classList.add('hidden');
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PhotoTournament();
});