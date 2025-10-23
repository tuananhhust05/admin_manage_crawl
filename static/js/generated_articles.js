class GeneratedArticlesManager {
    constructor() {
        // Pagination properties
        this.currentPage = 1;
        this.perPage = 20;
        this.totalPages = 1;
        this.totalCount = 0;
        this.hasMore = false;
        this.isLoadingMore = false;
        this.articles = [];
        this.filteredArticles = [];
        
        // DOM elements
        this.loadingState = document.getElementById('loading-state');
        this.errorState = document.getElementById('error-state');
        this.emptyState = document.getElementById('empty-state');
        this.articlesContainer = document.getElementById('articles-container');
        this.articlesTableBody = document.getElementById('articles-table-body');
        
        // Stats elements
        this.totalArticles = document.getElementById('total-articles');
        this.todayArticles = document.getElementById('today-articles');
        this.uniqueFixtures = document.getElementById('unique-fixtures');
        this.avgSources = document.getElementById('avg-sources');
        
        // Filter elements
        this.fixtureFilter = document.getElementById('fixture-filter');
        this.dateFilter = document.getElementById('date-filter');
        this.clearFiltersBtn = document.getElementById('clear-filters');
        this.refreshBtn = document.getElementById('refresh-data');
        
        // Pagination elements
        this.prevPageBtn = document.getElementById('prev-page');
        this.nextPageBtn = document.getElementById('next-page');
        this.pageNumbers = document.getElementById('page-numbers');
        this.paginationInfo = document.getElementById('pagination-info');
        
        // Create load more button
        this.createLoadMoreButton();
        
        // Modal elements
        this.articleModal = document.getElementById('article-modal');
        this.modalTitle = document.getElementById('modal-title');
        this.modalFixtureId = document.getElementById('modal-fixture-id');
        this.modalSourcesCount = document.getElementById('modal-sources-count');
        this.modalGeneratedAt = document.getElementById('modal-generated-at');
        this.modalArticleLength = document.getElementById('modal-article-length');
        this.modalArticleContent = document.getElementById('modal-article-content');
        this.closeModalBtn = document.getElementById('close-modal');
        this.closeModalBtn2 = document.getElementById('close-modal-btn');
        this.copyArticleBtn = document.getElementById('copy-article');
        
        // Error elements
        this.errorMessage = document.getElementById('error-message');
        this.retryBtn = document.getElementById('retry-btn');
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadArticles();
    }

    createLoadMoreButton() {
        // Create load more button container
        const loadMoreContainer = document.createElement('div');
        loadMoreContainer.id = 'load-more-container';
        loadMoreContainer.className = 'load-more-container';
        loadMoreContainer.style.display = 'none';
        
        const loadMoreBtn = document.createElement('button');
        loadMoreBtn.id = 'load-more-btn';
        loadMoreBtn.className = 'btn btn-secondary load-more-btn';
        loadMoreBtn.innerHTML = '<i class="fas fa-plus"></i> Load More Articles';
        loadMoreBtn.addEventListener('click', () => this.loadMoreArticles());
        
        loadMoreContainer.appendChild(loadMoreBtn);
        
        // Insert after articles container
        if (this.articlesContainer && this.articlesContainer.parentNode) {
            this.articlesContainer.parentNode.insertBefore(loadMoreContainer, this.articlesContainer.nextSibling);
        }
        
        this.loadMoreContainer = loadMoreContainer;
        this.loadMoreBtn = loadMoreBtn;
    }
    
    bindEvents() {
        // Filter events
        this.fixtureFilter.addEventListener('input', () => this.handleFilter());
        this.dateFilter.addEventListener('change', () => this.handleFilter());
        this.clearFiltersBtn.addEventListener('click', () => this.clearFilters());
        this.refreshBtn.addEventListener('click', () => this.loadArticles());
        
        // Pagination events
        this.prevPageBtn.addEventListener('click', () => this.goToPage(this.currentPage - 1));
        this.nextPageBtn.addEventListener('click', () => this.goToPage(this.currentPage + 1));
        
        // Modal events
        this.closeModalBtn.addEventListener('click', () => this.closeModal());
        this.closeModalBtn2.addEventListener('click', () => this.closeModal());
        this.copyArticleBtn.addEventListener('click', () => this.copyArticle());
        
        // Close modal when clicking outside
        this.articleModal.addEventListener('click', (e) => {
            if (e.target === this.articleModal) {
                this.closeModal();
            }
        });
        
        // Prevent modal from closing when clicking inside modal content
        const modalContent = this.articleModal.querySelector('.modal-content');
        if (modalContent) {
            modalContent.addEventListener('click', (e) => {
                e.stopPropagation();
            });
        }
        
        // Close modal with Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.articleModal.style.display === 'flex') {
                this.closeModal();
            }
        });
        
        // Retry button
        this.retryBtn.addEventListener('click', () => this.loadArticles());
    }
    
    async loadArticles(resetPagination = true) {
        try {
            if (resetPagination) {
                this.currentPage = 1;
                this.showLoading();
            } else {
                this.isLoadingMore = true;
                this.updateLoadMoreButton();
            }
            
            const url = new URL('/api/generated-articles', window.location.origin);
            url.searchParams.set('page', this.currentPage);
            url.searchParams.set('per_page', this.perPage);
            
            const response = await fetch(url.toString());
            const data = await response.json();
            
            if (data.success) {
                if (resetPagination) {
                    this.articles = data.articles;
                } else {
                    this.articles = [...this.articles, ...data.articles];
                }
                
                this.updatePaginationInfo(data.pagination);
                this.updateStats();
                this.renderArticles();
            } else {
                throw new Error(data.error || 'Failed to load articles');
            }
            
        } catch (error) {
            console.error('Error loading articles:', error);
            this.showError(error.message);
        } finally {
            this.isLoadingMore = false;
            this.updateLoadMoreButton();
        }
    }

    async loadMoreArticles() {
        if (this.isLoadingMore || !this.hasMore) return;
        
        this.currentPage++;
        await this.loadArticles(false);
    }

    updatePaginationInfo(pagination) {
        this.totalPages = pagination.total_pages;
        this.totalCount = pagination.total_count;
        this.hasMore = pagination.has_next;
        
        // Show/hide load more button
        if (this.loadMoreContainer) {
            this.loadMoreContainer.style.display = this.hasMore ? 'block' : 'none';
        }
    }

    updateLoadMoreButton() {
        if (this.loadMoreBtn) {
            if (this.isLoadingMore) {
                this.loadMoreBtn.disabled = true;
                this.loadMoreBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
            } else {
                this.loadMoreBtn.disabled = false;
                this.loadMoreBtn.innerHTML = '<i class="fas fa-plus"></i> Load More Articles';
            }
        }
    }
    
    updateStats() {
        const today = new Date().toISOString().split('T')[0];
        const todayArticles = this.articles.filter(article => 
            article.generated_at && article.generated_at.startsWith(today)
        );
        
        const uniqueFixtures = new Set(this.articles.map(article => article.fixture_id)).size;
        const avgSources = this.articles.length > 0 
            ? (this.articles.reduce((sum, article) => sum + (article.source_requests_count || 0), 0) / this.articles.length).toFixed(1)
            : 0;
        
        this.totalArticles.textContent = this.articles.length;
        this.todayArticles.textContent = todayArticles.length;
        this.uniqueFixtures.textContent = uniqueFixtures;
        this.avgSources.textContent = avgSources;
    }
    
    handleFilter() {
        const fixtureFilter = this.fixtureFilter.value.trim().toLowerCase();
        const dateFilter = this.dateFilter.value;
        
        this.filteredArticles = this.articles.filter(article => {
            const matchesFixture = !fixtureFilter || 
                (article.fixture_id && article.fixture_id.toLowerCase().includes(fixtureFilter));
            
            const matchesDate = !dateFilter || 
                (article.generated_at && article.generated_at.startsWith(dateFilter));
            
            return matchesFixture && matchesDate;
        });
        
        this.currentPage = 1;
        this.updatePagination();
        this.renderArticles();
    }
    
    clearFilters() {
        this.fixtureFilter.value = '';
        this.dateFilter.value = '';
        this.handleFilter();
    }
    
    updatePagination() {
        this.totalItems = this.filteredArticles.length;
        this.totalPages = Math.ceil(this.totalItems / this.itemsPerPage);
        
        // Update pagination info
        const startItem = (this.currentPage - 1) * this.itemsPerPage + 1;
        const endItem = Math.min(this.currentPage * this.itemsPerPage, this.totalItems);
        this.paginationInfo.textContent = `Showing ${startItem}-${endItem} of ${this.totalItems} articles`;
        
        // Update pagination buttons
        this.prevPageBtn.disabled = this.currentPage <= 1;
        this.nextPageBtn.disabled = this.currentPage >= this.totalPages;
        
        // Generate page numbers
        this.generatePageNumbers();
    }
    
    generatePageNumbers() {
        this.pageNumbers.innerHTML = '';
        
        const maxVisiblePages = 5;
        let startPage = Math.max(1, this.currentPage - Math.floor(maxVisiblePages / 2));
        let endPage = Math.min(this.totalPages, startPage + maxVisiblePages - 1);
        
        if (endPage - startPage + 1 < maxVisiblePages) {
            startPage = Math.max(1, endPage - maxVisiblePages + 1);
        }
        
        for (let i = startPage; i <= endPage; i++) {
            const pageBtn = document.createElement('button');
            pageBtn.className = `page-btn ${i === this.currentPage ? 'active' : ''}`;
            pageBtn.textContent = i;
            pageBtn.addEventListener('click', () => this.goToPage(i));
            this.pageNumbers.appendChild(pageBtn);
        }
    }
    
    goToPage(page) {
        if (page >= 1 && page <= this.totalPages) {
            this.currentPage = page;
            this.updatePagination();
            this.renderArticles();
        }
    }
    
    renderArticles() {
        if (this.filteredArticles.length === 0) {
            this.showEmpty();
            return;
        }
        
        this.showArticles();
        
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const pageArticles = this.filteredArticles.slice(startIndex, endIndex);
        
        this.articlesTableBody.innerHTML = '';
        
        pageArticles.forEach(article => {
            const row = this.createArticleRow(article);
            this.articlesTableBody.appendChild(row);
        });
    }
    
    createArticleRow(article) {
        const row = document.createElement('tr');
        row.className = 'article-row';
        
        const generatedDate = new Date(article.generated_at).toLocaleString();
        
        row.innerHTML = `
            <td class="article-title">
                <div class="title-content">
                    <strong>${article.title || 'Untitled Article'}</strong>
                </div>
            </td>
            <td class="fixture-id">
                <span class="fixture-badge">${article.fixture_id || 'N/A'}</span>
            </td>
            <td class="sources-count">
                <span class="sources-badge">${article.source_requests_count || 0}</span>
            </td>
            <td class="generated-date">
                <span class="date-text">${generatedDate}</span>
            </td>
            <td class="actions">
                <button class="btn btn-primary btn-sm view-btn" data-article-id="${article._id}">
                    <i class="bi bi-eye"></i> View
                </button>
            </td>
        `;
        
        // Add click event to view button
        const viewBtn = row.querySelector('.view-btn');
        viewBtn.addEventListener('click', () => this.showArticleModal(article));
        
        return row;
    }
    
    async showArticleModal(article) {
        try {
            // Populate modal with article data
            this.modalTitle.textContent = article.title || 'Article Details';
            this.modalFixtureId.textContent = article.fixture_id || 'N/A';
            this.modalSourcesCount.textContent = article.source_requests_count || 0;
            this.modalGeneratedAt.textContent = new Date(article.generated_at).toLocaleString();
            this.modalArticleLength.textContent = article.content ? article.content.length : 0;
            
            // Format article content
            if (article.content) {
                this.modalArticleContent.innerHTML = this.formatArticleContent(article.content);
            } else {
                this.modalArticleContent.innerHTML = '<p class="no-content">No content available</p>';
            }
            
            // Add related articles section if available
            this.addRelatedArticlesSection(article);
            
            // Show modal with animation
            this.articleModal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
            
            // Add a small delay to ensure modal is visible
            setTimeout(() => {
                this.articleModal.classList.add('modal-show');
            }, 10);
            
        } catch (error) {
            console.error('Error showing article modal:', error);
            this.showToast('error', 'Error', 'Failed to load article details');
        }
    }

    addRelatedArticlesSection(article) {
        // Remove existing related articles section if any
        const existingSection = document.getElementById('related-articles-section');
        if (existingSection) {
            existingSection.remove();
        }

        // Check if article has related articles data
        if (!article.related_articles_details || article.related_articles_details.length === 0) {
            return;
        }

        // Create related articles section
        const relatedSection = document.createElement('div');
        relatedSection.id = 'related-articles-section';
        relatedSection.className = 'related-articles-section';
        
        relatedSection.innerHTML = `
            <div class="section-header">
                <h4>Related Articles Used</h4>
                <span class="badge badge-info">${article.related_articles_details.length} articles</span>
            </div>
            <div class="related-articles-list">
                ${article.related_articles_details.map((relatedArticle, index) => `
                    <div class="related-article-item">
                        <div class="article-header">
                            <h5 class="article-title">${relatedArticle.title || 'Untitled'}</h5>
                            <span class="article-source badge badge-secondary">${relatedArticle.source || 'Unknown'}</span>
                        </div>
                        <div class="article-meta">
                            <span class="article-date">${new Date(relatedArticle.created_at).toLocaleDateString()}</span>
                            ${relatedArticle.url ? `<a href="${relatedArticle.url}" target="_blank" class="article-link">View Original <i class="fas fa-external-link-alt"></i></a>` : ''}
                        </div>
                        <div class="article-preview">
                            ${relatedArticle.content_preview || 'No preview available'}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;

        // Insert after article content
        this.modalArticleContent.parentNode.insertBefore(relatedSection, this.modalArticleContent.nextSibling);
    }
    
    formatArticleContent(content) {
        // Convert line breaks to HTML
        return content
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>')
            .replace(/^/, '<p>')
            .replace(/$/, '</p>');
    }
    
    closeModal() {
        // Remove show class first
        this.articleModal.classList.remove('modal-show');
        
        // Wait for animation to complete before hiding
        setTimeout(() => {
            this.articleModal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }, 300);
    }
    
    async copyArticle() {
        try {
            const content = this.modalArticleContent.textContent;
            await navigator.clipboard.writeText(content);
            this.showToast('success', 'Copied', 'Article content copied to clipboard');
        } catch (error) {
            console.error('Error copying article:', error);
            this.showToast('error', 'Error', 'Failed to copy article content');
        }
    }
    
    showLoading() {
        this.loadingState.style.display = 'flex';
        this.errorState.style.display = 'none';
        this.emptyState.style.display = 'none';
        this.articlesContainer.style.display = 'none';
    }
    
    showError(message) {
        this.loadingState.style.display = 'none';
        this.errorState.style.display = 'flex';
        this.emptyState.style.display = 'none';
        this.articlesContainer.style.display = 'none';
        this.errorMessage.textContent = message;
    }
    
    showEmpty() {
        this.loadingState.style.display = 'none';
        this.errorState.style.display = 'none';
        this.emptyState.style.display = 'flex';
        this.articlesContainer.style.display = 'none';
    }
    
    showArticles() {
        this.loadingState.style.display = 'none';
        this.errorState.style.display = 'none';
        this.emptyState.style.display = 'none';
        this.articlesContainer.style.display = 'block';
    }
    
    showToast(type, title, message) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <div class="toast-title">${title}</div>
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        const container = document.getElementById('toast-container');
        container.appendChild(toast);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 5000);
        
        // Close button
        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        });
    }
}

// Add CSS for related articles section
const additionalStyles = `
    .related-articles-section {
        margin-top: 2rem;
        padding: 1.5rem;
        background: #f8f9fa;
        border-radius: 8px;
        border: 1px solid #e9ecef;
    }
    
    .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #dee2e6;
    }
    
    .section-header h4 {
        margin: 0;
        color: #495057;
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    .related-articles-list {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    
    .related-article-item {
        background: white;
        padding: 1rem;
        border-radius: 6px;
        border: 1px solid #e9ecef;
        transition: box-shadow 0.2s ease;
    }
    
    .related-article-item:hover {
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .article-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 0.5rem;
    }
    
    .article-title {
        margin: 0;
        font-size: 0.95rem;
        font-weight: 600;
        color: #212529;
        flex: 1;
        margin-right: 1rem;
    }
    
    .article-source {
        font-size: 0.75rem;
        padding: 0.25rem 0.5rem;
    }
    
    .article-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.75rem;
        font-size: 0.85rem;
        color: #6c757d;
    }
    
    .article-link {
        color: #007bff;
        text-decoration: none;
        font-weight: 500;
    }
    
    .article-link:hover {
        text-decoration: underline;
    }
    
    .article-preview {
        font-size: 0.85rem;
        color: #495057;
        line-height: 1.4;
        max-height: 4rem;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
    }
    
    .load-more-container {
        display: flex;
        justify-content: center;
        margin: 2rem 0;
        padding: 1rem;
    }
    
    .load-more-btn {
        min-width: 200px;
        transition: all 0.3s ease;
    }
    
    .load-more-btn:hover:not(:disabled) {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .load-more-btn:disabled {
        opacity: 0.6;
        cursor: not-allowed;
        transform: none;
    }
`;

// Inject additional styles
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new GeneratedArticlesManager();
});
