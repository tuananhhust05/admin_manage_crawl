// Search Page JavaScript
class SearchManager {
    constructor() {
        this.apiBaseUrl = window.location.origin;
        this.searchApiUrl = 'http://37.27.181.54:5009/search/relevant/advanced';
        this.currentSearchData = null;
        this.searchStartTime = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.setupAnimations();
    }

    bindEvents() {
        // Search form
        document.getElementById('searchForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.performSearch();
        });

        // Clear button
        document.getElementById('clearBtn').addEventListener('click', () => {
            this.clearSearch();
        });

        // Search input events
        const searchInput = document.getElementById('searchKeyword');
        searchInput.addEventListener('input', (e) => {
            this.toggleClearButton(e.target.value);
        });

        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.performSearch();
            }
        });

        // Auto-focus search input
        searchInput.focus();
    }

    setupAnimations() {
        // Add smooth transitions
        const style = document.createElement('style');
        style.textContent = `
            .search-input-wrapper {
                transition: all 0.3s ease;
            }
            
            .search-input-wrapper:focus-within {
                transform: scale(1.02);
                box-shadow: 0 8px 25px rgba(0, 122, 255, 0.15);
            }
            
            .result-card {
                transition: all 0.3s ease;
            }
            
            .result-card:hover {
                transform: translateY(-4px);
            }
        `;
        document.head.appendChild(style);
    }

    toggleClearButton(value) {
        const clearBtn = document.getElementById('clearBtn');
        clearBtn.style.display = value ? 'block' : 'none';
    }

    clearSearch() {
        document.getElementById('searchKeyword').value = '';
        document.getElementById('clearBtn').style.display = 'none';
        this.showEmptyState();
    }

    setKeyword(keyword) {
        document.getElementById('searchKeyword').value = keyword;
        this.toggleClearButton(keyword);
        document.getElementById('searchKeyword').focus();
    }

    async performSearch() {
        const keyword = document.getElementById('searchKeyword').value.trim();
        if (!keyword) {
            this.showToast('warning', 'Warning', 'Please enter a search keyword');
            return;
        }

        // Get form data
        const formData = new FormData(document.getElementById('searchForm'));
        const searchData = {
            keyword: keyword,
            limit: parseInt(formData.get('limit')),
            min_score: parseFloat(formData.get('min_score')),
            include_content: formData.get('include_content') === 'on',
            boost_recent: formData.get('boost_recent') === 'on'
        };

        this.currentSearchData = searchData;
        this.searchStartTime = Date.now();
        
        this.showLoading();
        this.hideResults();
        this.hideError();

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/search-documents`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(searchData)
            });

            const data = await response.json();

            if (data.success) {
                this.displayResults(data.data);
            } else {
                this.showError(data.error || 'Search failed');
            }
        } catch (error) {
            console.error('Search error:', error);
            this.showError('Unable to connect to search service');
        } finally {
            this.hideLoading();
        }
    }

    async retrySearch() {
        if (this.currentSearchData) {
            await this.performSearch();
        }
    }

    showLoading() {
        const loadingSection = document.getElementById('loadingSection');
        const loadingText = document.getElementById('loadingText');
        
        loadingSection.style.display = 'block';
        
        // Animate loading text
        const texts = [
            'Finding relevant content for your query',
            'Analyzing document relevance',
            'Ranking search results',
            'Preparing results for display'
        ];
        
        let textIndex = 0;
        this.loadingInterval = setInterval(() => {
            loadingText.textContent = texts[textIndex];
            textIndex = (textIndex + 1) % texts.length;
        }, 2000);
    }

    hideLoading() {
        const loadingSection = document.getElementById('loadingSection');
        loadingSection.style.display = 'none';
        
        if (this.loadingInterval) {
            clearInterval(this.loadingInterval);
        }
    }

    displayResults(data) {
        const resultsSection = document.getElementById('resultsSection');
        const resultsGrid = document.getElementById('resultsGrid');
        const resultsCount = document.getElementById('resultsCount');
        const searchTime = document.getElementById('searchTime');
        
        // Calculate search time
        const searchDuration = Date.now() - this.searchStartTime;
        searchTime.textContent = `Search completed in ${searchDuration}ms`;
        
        // Update results count
        const count = data.results ? data.results.length : 0;
        resultsCount.textContent = `${count} result${count !== 1 ? 's' : ''} found`;
        
        // Display results
        if (data.results && data.results.length > 0) {
            resultsGrid.innerHTML = data.results.map((result, index) => 
                this.createResultCard(result, index)
            ).join('');
            
            resultsSection.style.display = 'block';
            this.hideEmptyState();
            
            // Animate results
            this.animateResults();
        } else {
            this.showEmptyState('No results found for your search');
        }
    }

    createResultCard(result, index) {
        const score = (result.score * 100).toFixed(1);
        const contentPreview = result.content_preview || 'No preview available';
        const time = result.time || 'Unknown';
        const url = result.url || '#';
        
        return `
            <div class="result-card" style="animation-delay: ${index * 0.1}s">
                <div class="result-header">
                    <div class="result-score">
                        <div class="score-circle">
                            <span class="score-value">${score}%</span>
                        </div>
                        <span class="score-label">Relevance</span>
                    </div>
                    <div class="result-meta">
                        <span class="result-time">
                            <i class="fas fa-clock"></i>
                            ${time}
                        </span>
                        <span class="result-id">
                            <i class="fas fa-hashtag"></i>
                            ${result.id}
                        </span>
                    </div>
                </div>
                
                <div class="result-content">
                    <div class="content-preview">
                        <p>${this.highlightKeywords(contentPreview, this.currentSearchData.keyword)}</p>
                    </div>
                </div>
                
                <div class="result-footer">
                    <a href="${url}" target="_blank" class="btn btn-sm btn-primary">
                        <i class="fas fa-external-link-alt"></i>
                        View Source
                    </a>
                    <button class="btn btn-sm btn-secondary" onclick="searchManager.copyToClipboard('${result.id}')">
                        <i class="fas fa-copy"></i>
                        Copy ID
                    </button>
                </div>
            </div>
        `;
    }

    highlightKeywords(text, keyword) {
        if (!keyword) return text;
        
        const keywords = keyword.toLowerCase().split(' ');
        let highlightedText = text;
        
        keywords.forEach(keyword => {
            if (keyword.length > 2) {
                const regex = new RegExp(`(${keyword})`, 'gi');
                highlightedText = highlightedText.replace(regex, '<mark>$1</mark>');
            }
        });
        
        return highlightedText;
    }

    animateResults() {
        const resultCards = document.querySelectorAll('.result-card');
        resultCards.forEach((card, index) => {
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }

    showEmptyState(message = 'Start Your Search') {
        const emptyState = document.getElementById('emptyState');
        const emptyTitle = emptyState.querySelector('h3');
        
        emptyTitle.textContent = message;
        emptyState.style.display = 'block';
        this.hideResults();
    }

    hideEmptyState() {
        document.getElementById('emptyState').style.display = 'none';
    }

    showError(message) {
        const errorState = document.getElementById('errorState');
        const errorMessage = document.getElementById('errorMessage');
        
        errorMessage.textContent = message;
        errorState.style.display = 'block';
        this.hideResults();
    }

    hideError() {
        document.getElementById('errorState').style.display = 'none';
    }

    hideResults() {
        document.getElementById('resultsSection').style.display = 'none';
    }

    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.showToast('success', 'Copied', `ID "${text}" copied to clipboard`);
        } catch (error) {
            console.error('Copy failed:', error);
            this.showToast('error', 'Error', 'Failed to copy to clipboard');
        }
    }

    showToast(type, title, message) {
        const toastContainer = document.getElementById('toastContainer');
        const toastId = 'toast-' + Date.now();
        
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };

        const toast = document.createElement('div');
        toast.id = toastId;
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <i class="${icons[type]}"></i>
            <div class="toast-content">
                <h4>${title}</h4>
                <p>${message}</p>
            </div>
        `;

        toastContainer.appendChild(toast);

        // Auto remove after 5 seconds
        setTimeout(() => {
            this.removeToast(toastId);
        }, 5000);
    }

    removeToast(toastId) {
        const toast = document.getElementById(toastId);
        if (toast) {
            toast.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                toast.remove();
            }, 300);
        }
    }
}

// Initialize the application
let searchManager;
document.addEventListener('DOMContentLoaded', () => {
    searchManager = new SearchManager();
});
