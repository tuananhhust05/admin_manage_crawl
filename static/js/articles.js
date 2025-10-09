/**
 * Articles Page Manager
 * Handles type filtering, article display, and modal functionality
 */
class ArticlesManager {
    constructor() {
        this.typeFilter = document.getElementById('type-filter');
        this.searchInput = document.getElementById('search-input');
        this.clearSearchBtn = document.getElementById('clear-search');
        this.statsCount = document.getElementById('articles-count');
        this.currentType = document.getElementById('current-type');
        this.selectedCount = document.getElementById('selected-count');
        this.selectionActions = document.getElementById('selection-actions');
        this.clearSelectionBtn = document.getElementById('clear-selection-btn');
        this.generateArticleBtn = document.getElementById('generate-article-btn');
        this.articlesGrid = document.getElementById('articles-grid');
        this.loadingState = document.getElementById('loading-state');
        this.errorState = document.getElementById('error-state');
        this.emptyState = document.getElementById('empty-state');
        this.modal = document.getElementById('article-modal');
        this.modalTitle = document.getElementById('modal-title');
        this.modalContent = document.getElementById('modal-content');
        this.generatedModal = document.getElementById('generated-article-modal');
        this.generatedContent = document.getElementById('generated-content');
        this.currentTypeFilter = 'fotmob';
        this.currentSearchQuery = '';
        this.selectedArticles = new Set();
        this.allArticles = [];
        this.searchTimeout = null;
    }

    init() {
        this.bindEvents();
        this.loadArticles();
    }

    bindEvents() {
        // Type filter change event
        if (this.typeFilter) {
            this.typeFilter.addEventListener('change', (e) => {
                this.filterByType(e.target.value);
            });
        }

        // Search input events
        if (this.searchInput) {
            this.searchInput.addEventListener('input', (e) => {
                this.handleSearch(e.target.value);
            });
        }

        // Clear search button
        if (this.clearSearchBtn) {
            this.clearSearchBtn.addEventListener('click', () => {
                this.clearSearch();
            });
        }

        // Selection buttons

        if (this.clearSelectionBtn) {
            this.clearSelectionBtn.addEventListener('click', () => {
                this.clearSelection();
            });
        }

        if (this.generateArticleBtn) {
            this.generateArticleBtn.addEventListener('click', () => {
                this.generateArticle();
            });
        }

        // Modal close events
        if (this.modal) {
            this.modal.addEventListener('click', (e) => {
                if (e.target === this.modal) {
                    this.closeModal();
                }
            });
        }

        if (this.generatedModal) {
            this.generatedModal.addEventListener('click', (e) => {
                if (e.target === this.generatedModal) {
                    this.closeGeneratedModal();
                }
            });
        }

        // Close modal with Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                if (this.modal.classList.contains('show')) {
                    this.closeModal();
                } else if (this.generatedModal.classList.contains('show')) {
                    this.closeGeneratedModal();
                }
            }
        });
    }

    async loadArticles() {
        try {
            this.showLoading();
            
            const url = new URL('/api/articles', window.location.origin);
            if (this.currentTypeFilter !== 'all') {
                url.searchParams.set('type', this.currentTypeFilter);
            }
            if (this.currentSearchQuery) {
                url.searchParams.set('search', this.currentSearchQuery);
            }
            
            console.log('🔍 Loading articles from:', url.toString());
            
            const response = await fetch(url.toString());
            const data = await response.json();
            
            console.log('📊 API Response:', data);
            
            if (data.success) {
                this.allArticles = data.articles;
                this.renderArticles(data.articles);
                this.updateStats(data.total_count, data.selected_type);
                this.updateTypeFilter(data.available_types);
                this.updateSearchUI(data.search_query);
            } else {
                this.showError(data.error || 'Failed to load articles');
            }
        } catch (error) {
            console.error('❌ Error loading articles:', error);
            this.showError('Network error: ' + error.message);
        }
    }

    filterByType(type) {
        this.currentTypeFilter = type;
        this.loadArticles();
    }

    handleSearch(query) {
        // Clear previous timeout
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }

        // Set new timeout for debounced search
        this.searchTimeout = setTimeout(() => {
            this.currentSearchQuery = query;
            this.loadArticles();
        }, 300);
    }

    clearSearch() {
        this.searchInput.value = '';
        this.currentSearchQuery = '';
        this.clearSearchBtn.style.display = 'none';
        this.loadArticles();
    }

    updateSearchUI(searchQuery) {
        if (this.clearSearchBtn) {
            this.clearSearchBtn.style.display = searchQuery ? 'block' : 'none';
        }
    }

    showLoading() {
        this.loadingState.style.display = 'block';
        this.errorState.style.display = 'none';
        this.articlesGrid.style.display = 'none';
        this.emptyState.style.display = 'none';
    }

    showError(message) {
        this.loadingState.style.display = 'none';
        this.errorState.style.display = 'block';
        this.articlesGrid.style.display = 'none';
        this.emptyState.style.display = 'none';
        
        const errorMessage = document.getElementById('error-message');
        if (errorMessage) {
            errorMessage.textContent = message;
        }
    }

    renderArticles(articles) {
        this.loadingState.style.display = 'none';
        this.errorState.style.display = 'none';
        
        if (articles.length === 0) {
            this.emptyState.style.display = 'block';
            this.articlesGrid.style.display = 'none';
        } else {
            this.emptyState.style.display = 'none';
            this.articlesGrid.style.display = 'grid';
            
            this.articlesGrid.innerHTML = articles.map(article => {
                const articleType = article.source || article.type || 'unknown';
                const typeDisplay = articleType.charAt(0).toUpperCase() + articleType.slice(1);
                const isSelected = this.selectedArticles.has(article._id);
                
                // Get full content and highlight search terms
                const fullContent = article.content || article.summary || 'No content available';
                const highlightedContent = this.highlightSearchTerms(fullContent);
                const highlightedTitle = this.highlightSearchTerms(article.title || 'Untitled Article');
                
                // Check if selection is disabled (already at limit and not selected)
                const isDisabled = !isSelected && this.selectedArticles.size >= 3;
                
                return `
                <article class="apple-card ${isSelected ? 'selected' : ''} ${isDisabled ? 'disabled' : ''}" data-article-id="${article._id}">
                    <div class="card-header">
                        <div class="card-selection">
                            <input type="checkbox" class="article-checkbox" ${isSelected ? 'checked' : ''} ${isDisabled ? 'disabled' : ''}
                                   onchange="window.articlesManager.toggleSelection('${article._id}')">
                        </div>
                        <div class="card-type">
                            <span class="apple-badge apple-badge-${articleType}">${typeDisplay}</span>
                        </div>
                        <div class="card-date">
                            ${article.created_at ? article.created_at.substring(0, 10) : 'N/A'}
                        </div>
                    </div>
                    
                    <div class="card-body">
                        <h2 class="card-title">${highlightedTitle}</h2>
                        <div class="card-text">${highlightedContent.replace(/\n/g, '<br>')}</div>
                    </div>
                    
                    <div class="card-footer">
                        ${article.url ? `
                            <a href="${article.url}" target="_blank" class="apple-link">
                                <span>View Source</span>
                                <i class="fas fa-arrow-up-right-from-square"></i>
                            </a>
                        ` : ''}
                        <button class="apple-button apple-button-primary" onclick="viewArticle('${article._id}')">
                            <span>View Details</span>
                        </button>
                    </div>
                </article>
                `;
            }).join('');
        }
    }

    highlightSearchTerms(text) {
        if (!this.currentSearchQuery || !text) {
            return text;
        }
        
        const searchTerms = this.currentSearchQuery.trim().split(/\s+/);
        let highlightedText = text;
        
        searchTerms.forEach(term => {
            if (term.length > 2) { // Only highlight terms longer than 2 characters
                const regex = new RegExp(`(${term})`, 'gi');
                highlightedText = highlightedText.replace(regex, '<mark class="search-highlight">$1</mark>');
            }
        });
        
        return highlightedText;
    }

    updateStats(count, type) {
        if (this.statsCount) {
            this.statsCount.textContent = `${count} article${count !== 1 ? 's' : ''}`;
        }
        if (this.currentType) {
            this.currentType.textContent = type === 'all' ? 'All Types' : type.charAt(0).toUpperCase() + type.slice(1);
        }
        this.updateSelectionUI();
    }

    updateSelectionUI() {
        const selectedCount = this.selectedArticles.size;
        if (this.selectedCount) {
            this.selectedCount.textContent = `${selectedCount} selected`;
        }
        if (this.selectionActions) {
            this.selectionActions.style.display = selectedCount > 0 ? 'flex' : 'none';
        }
        if (this.generateArticleBtn) {
            this.generateArticleBtn.disabled = selectedCount === 0 || selectedCount > 3;
        }
    }

    toggleSelection(articleId) {
        if (this.selectedArticles.has(articleId)) {
            this.selectedArticles.delete(articleId);
        } else {
            if (this.selectedArticles.size >= 3) {
                this.showToast('warning', 'Selection Limit', 'You can select maximum 3 articles');
                return;
            }
            this.selectedArticles.add(articleId);
        }
        this.updateSelectionUI();
        this.updateCardSelection(articleId);
    }

    updateCardSelection(articleId) {
        const card = document.querySelector(`[data-article-id="${articleId}"]`);
        const checkbox = card?.querySelector('.article-checkbox');
        if (card && checkbox) {
            const isSelected = this.selectedArticles.has(articleId);
            card.classList.toggle('selected', isSelected);
            checkbox.checked = isSelected;
        }
    }


    clearSelection() {
        this.selectedArticles.clear();
        this.updateSelectionUI();
        this.renderArticles(this.allArticles);
    }

    async generateArticle() {
        if (this.selectedArticles.size === 0) {
            this.showToast('warning', 'No Selection', 'Please select at least one article');
            return;
        }

        if (this.selectedArticles.size > 3) {
            this.showToast('warning', 'Too Many Articles', 'Please select maximum 3 articles');
            return;
        }

        try {
            // Get selected articles content
            const selectedArticlesData = this.allArticles.filter(article => 
                this.selectedArticles.has(article._id)
            );

            const articlesContent = selectedArticlesData.map(article => 
                article.content || article.summary || ''
            );

            // Show loading
            this.generateArticleBtn.disabled = true;
            this.generateArticleBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';

            // Call external API directly
            const response = await fetch('http://46.62.152.241:5002/generate-article', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    articles: articlesContent
                })
            });

            const result = await response.json();

            if (response.ok) {
                this.showGeneratedArticle(result);
                this.showToast('success', 'Article Generated', 'New article has been generated successfully!');
            } else {
                this.showToast('error', 'Generation Failed', result.error || 'Failed to generate article');
            }

        } catch (error) {
            console.error('Error generating article:', error);
            this.showToast('error', 'Network Error', 'Failed to generate article: ' + error.message);
        } finally {
            this.generateArticleBtn.disabled = false;
            this.generateArticleBtn.innerHTML = '<i class="fas fa-magic"></i> <span>Generate Article</span>';
        }
    }

    showGeneratedArticle(data) {
        if (this.generatedContent) {
            let content = '';
            
            // Handle different response formats
            if (typeof data === 'string') {
                content = data;
            } else if (data.article) {
                content = data.article;
            } else if (data.generated_article) {
                content = data.generated_article;
            } else {
                content = JSON.stringify(data);
            }
            
            // Remove markdown formatting and split by paragraphs
            content = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            content = content.replace(/\*(.*?)\*/g, '<em>$1</em>');
            
            const paragraphs = content.split('\n').filter(p => p.trim());
            this.generatedContent.innerHTML = paragraphs.map(paragraph => 
                `<p class="generated-paragraph">${paragraph.trim()}</p>`
            ).join('');
            
            // Show elapsed time if available
            if (data.elapsed_seconds) {
                const timeInfo = document.createElement('div');
                timeInfo.className = 'generation-time';
                timeInfo.innerHTML = `<small>Generated in ${data.elapsed_seconds}s</small>`;
                this.generatedContent.insertBefore(timeInfo, this.generatedContent.firstChild);
            }
        }
        
        if (this.generatedModal) {
            this.generatedModal.classList.add('show');
            document.body.style.overflow = 'hidden';
        }
    }

    closeGeneratedModal() {
        if (this.generatedModal) {
            this.generatedModal.classList.remove('show');
            document.body.style.overflow = '';
        }
    }

    updateTypeFilter(availableTypes) {
        if (this.typeFilter && availableTypes) {
            // Update the select options if needed
            const currentOptions = Array.from(this.typeFilter.options).map(opt => opt.value);
            const newTypes = ['all', ...availableTypes];
            
            if (JSON.stringify(currentOptions) !== JSON.stringify(newTypes)) {
                this.typeFilter.innerHTML = newTypes.map(type => 
                    `<option value="${type}" ${type === this.currentTypeFilter ? 'selected' : ''}>${type === 'all' ? 'All Types' : type.charAt(0).toUpperCase() + type.slice(1)}</option>`
                ).join('');
            }
        }
    }

    showModal(articleId) {
        if (!this.modal) return;

        // Show loading state
        this.modalTitle.textContent = 'Loading...';
        this.modalContent.innerHTML = '<div class="loading-spinner"><i class="fas fa-spinner fa-spin"></i> Loading article details...</div>';
        this.modal.classList.add('show');

        // Fetch article details (you can implement this API endpoint)
        this.fetchArticleDetails(articleId)
            .then(article => {
                this.displayArticleInModal(article);
            })
            .catch(error => {
                this.modalContent.innerHTML = `
                    <div class="error-message">
                        <i class="fas fa-exclamation-triangle"></i>
                        <span>Error loading article: ${error.message}</span>
                    </div>
                `;
            });
    }

    closeModal() {
        if (this.modal) {
            this.modal.classList.remove('show');
        }
    }

    async fetchArticleDetails(articleId) {
        // For now, we'll extract article data from the existing card
        // In a real implementation, you'd make an API call
        const articleCard = document.querySelector(`[data-article-id="${articleId}"]`);
        if (!articleCard) {
            throw new Error('Article not found');
        }

        // Extract data from the card
        const title = articleCard.querySelector('.card-title')?.textContent || 'Untitled';
        const summary = articleCard.querySelector('.card-text')?.textContent || 'No summary available';
        const source = articleCard.querySelector('.apple-badge')?.textContent || 'Unknown';
        const date = articleCard.querySelector('.card-date')?.textContent || 'Unknown date';
        const link = articleCard.querySelector('.apple-link')?.href || '';

        return {
            id: articleId,
            title: title,
            summary: summary,
            source: source,
            date: date,
            link: link
        };
    }

    displayArticleInModal(article) {
        this.modalTitle.textContent = article.title;
        
        this.modalContent.innerHTML = `
            <div class="apple-article-detail">
                <div class="detail-header">
                    <div class="detail-meta">
                        <span class="apple-badge apple-badge-${article.source.toLowerCase()}">${article.source}</span>
                        <span class="detail-date">${article.date}</span>
                    </div>
                </div>
                
                <div class="detail-content">
                    <h3 class="detail-section-title">Summary</h3>
                    <p class="detail-text">${article.summary}</p>
                    
                    ${article.link ? `
                        <div class="detail-actions">
                            <a href="${article.link}" target="_blank" class="apple-button apple-button-primary">
                                <span>View Full Article</span>
                                <i class="fas fa-arrow-up-right-from-square"></i>
                            </a>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    showToast(type, title, message, duration = 5000) {
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <div class="toast-title">${title}</div>
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;

        // Add to page
        document.body.appendChild(toast);

        // Show toast
        setTimeout(() => toast.classList.add('show'), 100);

        // Auto remove
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }
}

// Global functions for template usage
function viewArticle(articleId) {
    if (window.articlesManager) {
        window.articlesManager.showModal(articleId);
    }
}

function closeModal() {
    if (window.articlesManager) {
        window.articlesManager.closeModal();
    }
}

function closeGeneratedModal() {
    if (window.articlesManager) {
        window.articlesManager.closeGeneratedModal();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.articlesManager = new ArticlesManager();
    if (window.articlesManager && typeof window.articlesManager.init === 'function') {
        window.articlesManager.init();
    } else {
        console.error('ArticlesManager not properly initialized');
    }
});

// Add some additional CSS for the modal content
const additionalStyles = `
    .loading-spinner {
        text-align: center;
        padding: 40px 20px;
        color: var(--text-secondary);
    }
    
    .loading-spinner i {
        font-size: 24px;
        margin-bottom: 16px;
    }
    
    .apple-article-detail {
        max-width: 100%;
    }
    
    .detail-header {
        margin-bottom: 24px;
    }
    
    .detail-meta {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 16px;
    }
    
    .detail-date {
        color: var(--text-secondary);
        font-size: 14px;
        font-weight: 500;
    }
    
    .detail-content h3 {
        font-size: 16px;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 12px;
        letter-spacing: -0.2px;
    }
    
    .detail-text {
        color: var(--text-primary);
        line-height: 1.6;
        margin-bottom: 24px;
        font-size: 15px;
    }
    
    .detail-actions {
        display: flex;
        gap: 12px;
        padding-top: 16px;
        border-top: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    .toast {
        position: fixed;
        top: var(--spacing-lg);
        right: var(--spacing-lg);
        background: var(--background-card);
        backdrop-filter: blur(20px);
        border: 1px solid var(--border-color-light);
        border-radius: var(--border-radius);
        box-shadow: var(--shadow-large);
        padding: var(--spacing-md);
        max-width: 400px;
        z-index: 10001;
        transform: translateX(100%);
        transition: transform 0.3s ease;
        display: flex;
        align-items: flex-start;
        gap: var(--spacing-sm);
    }
    
    .toast.show {
        transform: translateX(0);
    }
    
    .toast-content {
        flex: 1;
    }
    
    .toast-title {
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: var(--spacing-xs);
    }
    
    .toast-message {
        color: var(--text-secondary);
        font-size: var(--font-size-sm);
    }
    
    .toast-close {
        background: none;
        border: none;
        color: var(--text-secondary);
        cursor: pointer;
        padding: var(--spacing-xs);
        border-radius: var(--border-radius-small);
        transition: all 0.2s ease;
    }
    
    .toast-close:hover {
        background: var(--background-secondary);
        color: var(--text-primary);
    }
    
    .toast-success {
        border-left: 4px solid var(--success-color);
    }
    
    .toast-error {
        border-left: 4px solid var(--error-color);
    }
    
    .toast-warning {
        border-left: 4px solid var(--warning-color);
    }
    
    .toast-info {
        border-left: 4px solid var(--primary-color);
    }
`;

// Inject additional styles
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);
