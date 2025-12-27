// NFL Game Outcome Predictor - Frontend JavaScript

// API base URL (adjust if backend runs on different port)
const API_BASE_URL = 'http://localhost:8000';

// State
let currentSeason = null;
let teams = [];

// DOM elements
const seasonSelect = document.getElementById('season');
const homeTeamSelect = document.getElementById('homeTeam');
const awayTeamSelect = document.getElementById('awayTeam');
const predictionForm = document.getElementById('predictionForm');
const loading = document.getElementById('loading');
const error = document.getElementById('error');
const errorMessage = document.getElementById('errorMessage');
const results = document.getElementById('results');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkAPIHealth();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    seasonSelect.addEventListener('change', handleSeasonChange);
    predictionForm.addEventListener('submit', handlePredictionSubmit);
    
    // Prevent selecting same team
    homeTeamSelect.addEventListener('change', updateAwayTeamOptions);
    awayTeamSelect.addEventListener('change', updateHomeTeamOptions);
}

// Check if API is healthy
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        
        if (!data.model_loaded) {
            showError('Model not loaded. Please train the model first by running: python src/train_model.py');
        }
    } catch (err) {
        showError('Cannot connect to API. Make sure the backend is running: uvicorn backend.app:app --reload');
    }
}

// Handle season change
async function handleSeasonChange(e) {
    const season = e.target.value;
    
    if (!season) {
        homeTeamSelect.disabled = true;
        awayTeamSelect.disabled = true;
        return;
    }
    
    currentSeason = parseInt(season);
    
    try {
        showLoading();
        const response = await fetch(`${API_BASE_URL}/teams?season=${season}`);
        
        if (!response.ok) {
            throw new Error('Failed to fetch teams');
        }
        
        const data = await response.json();
        teams = data.teams;
        
        populateTeamDropdowns();
        hideLoading();
        
    } catch (err) {
        hideLoading();
        showError(`Error loading teams: ${err.message}`);
    }
}

// Populate team dropdowns
function populateTeamDropdowns() {
    // Clear existing options
    homeTeamSelect.innerHTML = '<option value="">Select Home Team</option>';
    awayTeamSelect.innerHTML = '<option value="">Select Away Team</option>';
    
    // Add team options
    teams.forEach(team => {
        const homeOption = new Option(team, team);
        const awayOption = new Option(team, team);
        homeTeamSelect.add(homeOption);
        awayTeamSelect.add(awayOption);
    });
    
    // Enable dropdowns
    homeTeamSelect.disabled = false;
    awayTeamSelect.disabled = false;
}

// Update away team options (prevent same team selection)
function updateAwayTeamOptions() {
    const selectedHome = homeTeamSelect.value;
    const currentAway = awayTeamSelect.value;
    
    // Rebuild away team dropdown
    awayTeamSelect.innerHTML = '<option value="">Select Away Team</option>';
    
    teams.forEach(team => {
        if (team !== selectedHome) {
            const option = new Option(team, team);
            awayTeamSelect.add(option);
        }
    });
    
    // Restore selection if still valid
    if (currentAway && currentAway !== selectedHome) {
        awayTeamSelect.value = currentAway;
    }
}

// Update home team options (prevent same team selection)
function updateHomeTeamOptions() {
    const selectedAway = awayTeamSelect.value;
    const currentHome = homeTeamSelect.value;
    
    // Rebuild home team dropdown
    homeTeamSelect.innerHTML = '<option value="">Select Home Team</option>';
    
    teams.forEach(team => {
        if (team !== selectedAway) {
            const option = new Option(team, team);
            homeTeamSelect.add(option);
        }
    });
    
    // Restore selection if still valid
    if (currentHome && currentHome !== selectedAway) {
        homeTeamSelect.value = currentHome;
    }
}

// Handle prediction form submission
async function handlePredictionSubmit(e) {
    e.preventDefault();
    
    const homeTeam = homeTeamSelect.value;
    const awayTeam = awayTeamSelect.value;
    const season = seasonSelect.value ? parseInt(seasonSelect.value) : null;
    
    if (!homeTeam || !awayTeam) {
        showError('Please select both home and away teams');
        return;
    }
    
    if (homeTeam === awayTeam) {
        showError('Home and away teams must be different');
        return;
    }
    
    try {
        showLoading();
        hideError();
        hideResults();
        
        const response = await fetch(`${API_BASE_URL}/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                home_team: homeTeam,
                away_team: awayTeam,
                season: season
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Prediction failed');
        }
        
        const data = await response.json();
        displayResults(data);
        hideLoading();
        
    } catch (err) {
        hideLoading();
        showError(`Prediction error: ${err.message}`);
    }
}

// Display prediction results
function displayResults(data) {
    // Winner section
    document.getElementById('winnerName').textContent = data.predicted_winner;
    
    const confidenceBadge = document.getElementById('confidenceBadge');
    confidenceBadge.textContent = `${data.confidence} Confidence`;
    confidenceBadge.className = 'confidence-badge ' + data.confidence.toLowerCase();
    
    // Team names
    document.getElementById('homeTeamName').textContent = data.home_team;
    document.getElementById('awayTeamName').textContent = data.away_team;
    
    // Probabilities
    document.getElementById('homeProbability').textContent = 
        `${(data.home_win_probability * 100).toFixed(1)}%`;
    document.getElementById('awayProbability').textContent = 
        `${(data.away_win_probability * 100).toFixed(1)}%`;
    
    // Home team stats
    document.getElementById('homePointsFor').textContent = 
        data.home_stats.avg_points_for.toFixed(1);
    document.getElementById('homePointsAgainst').textContent = 
        data.home_stats.avg_points_against.toFixed(1);
    document.getElementById('homeRecentForm').textContent = 
        data.home_stats.recent_form.toFixed(1);
    
    // Away team stats
    document.getElementById('awayPointsFor').textContent = 
        data.away_stats.avg_points_for.toFixed(1);
    document.getElementById('awayPointsAgainst').textContent = 
        data.away_stats.avg_points_against.toFixed(1);
    document.getElementById('awayRecentForm').textContent = 
        data.away_stats.recent_form.toFixed(1);
    
    // Context info
    let contextText = '';
    if (data.season) {
        contextText = `${data.season} Season`;
        if (data.current_week) {
            contextText += ` • Current Week: ${data.current_week}`;
        }
    } else {
        contextText = 'Historical matchup analysis';
    }
    document.getElementById('contextInfo').textContent = contextText;
    
    // Show results
    showResults();
}

// Show/hide functions
function showLoading() {
    loading.classList.remove('hidden');
}

function hideLoading() {
    loading.classList.add('hidden');
}

function showError(message) {
    errorMessage.textContent = message;
    error.classList.remove('hidden');
}

function hideError() {
    error.classList.add('hidden');
}

function showResults() {
    results.classList.remove('hidden');
    // Scroll to results
    results.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function hideResults() {
    results.classList.add('hidden');
}

// Reset form for new prediction
function resetForm() {
    hideResults();
    hideError();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}
