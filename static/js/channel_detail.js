// Channel Detail Page JavaScript
class ChannelDetailManager {
    constructor() {
        this.apiBaseUrl = window.location.origin;
        this.channelId = this.getChannelIdFromUrl();
        this.videos = [];
        this.filteredVideos = [];
        this.channelData = null;
        this.init();
    }

    async init() {
        this.bindEvents();
        await this.loadChannelData();
        this.loadVideos();
    }

    getChannelIdFromUrl() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('id'); // This is MongoDB _id
    }

    getYouTubeChannelId() {
        // Return the actual YouTube channel_id from channelData
        return this.channelData ? this.channelData.channel_id : null;
    }

    bindEvents() {
        // Crawl videos button
        document.getElementById('crawlVideosBtn').addEventListener('click', () => {
            this.crawlVideos();
        });

        document.getElementById('crawlVideosBtnEmpty').addEventListener('click', () => {
            this.crawlVideos();
        });

        // Video search
        document.getElementById('videoSearchInput').addEventListener('input', (e) => {
            this.filterVideos(e.target.value);
        });

        // Status filter
        document.getElementById('statusFilter').addEventListener('change', (e) => {
            this.filterVideos(document.getElementById('videoSearchInput').value, e.target.value);
        });
    }

    async loadChannelData() {
        if (!this.channelId) {
            this.showToast('error', 'Error', 'Channel ID not found');
            return;
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/youtube-channels/${this.channelId}`);
            const data = await response.json();

            if (data.success) {
                this.channelData = data.data;
                this.updateChannelInfo();
            } else {
                this.showToast('error', 'Error', 'Failed to load channel data');
            }
        } catch (error) {
            console.error('Error loading channel data:', error);
            this.showToast('error', 'Error', 'Unable to connect to server');
        }
    }

    updateChannelInfo() {
        if (!this.channelData) return;

        document.getElementById('channelTitle').textContent = this.channelData.title || 'Channel Details';
        document.getElementById('channelName').textContent = this.channelData.title || 'Untitled Channel';
        document.getElementById('channelUrl').textContent = this.channelData.url;
        document.getElementById('channelDescription').textContent = this.channelData.description || 'No description available';
        document.getElementById('subscriberCount').textContent = this.formatNumber(this.channelData.subscriber_count || 0);
        document.getElementById('videoCount').textContent = this.formatNumber(this.channelData.video_count || 0);
    }

    async loadVideos() {
        const youtubeChannelId = this.getYouTubeChannelId();
        if (!youtubeChannelId) return;

        try {
            this.showLoading(true);
            const response = await fetch(`${this.apiBaseUrl}/api/videos?channel_id=${youtubeChannelId}`);
            const data = await response.json();

            if (data.success) {
                this.videos = data.data;
                this.filteredVideos = [...this.videos];
                this.renderVideos();
                this.updateCrawledVideosCount();
            } else {
                this.showToast('error', 'Error', 'Failed to load videos');
            }
        } catch (error) {
            console.error('Error loading videos:', error);
            this.showToast('error', 'Error', 'Unable to connect to server');
        } finally {
            this.showLoading(false);
        }
    }

    renderVideos() {
        const videosGrid = document.getElementById('videosGrid');
        const emptyState = document.getElementById('emptyState');

        if (this.filteredVideos.length === 0) {
            videosGrid.innerHTML = '';
            emptyState.style.display = 'block';
            return;
        }

        emptyState.style.display = 'none';
        videosGrid.innerHTML = this.filteredVideos.map(video => this.createVideoCard(video)).join('');
    }

    createVideoCard(video) {
        const publishedDate = new Date(video.published_at).toLocaleDateString('en-US');
        const statusClass = this.getStatusClass(video.status);
        const statusText = this.getStatusText(video.status);
        
        return `
            <div class="video-card" data-id="${video._id}">
                <div class="video-thumbnail">
                    ${video.thumbnail_url ? 
                        `<img src="${video.thumbnail_url}" alt="${video.title}" onerror="this.style.display='none'">` :
                        `<div class="thumbnail-placeholder"><i class="fas fa-video"></i></div>`
                    }
                    <div class="video-duration">${video.duration || 'N/A'}</div>
                </div>
                
                <div class="video-content">
                    <h3 class="video-title">${video.title || 'Untitled Video'}</h3>
                    <p class="video-description">${video.description ? video.description.substring(0, 100) + '...' : 'No description'}</p>
                    
                    <div class="video-stats">
                        <div class="stat-item">
                            <i class="fas fa-eye"></i>
                            <span>${this.formatNumber(video.view_count || 0)}</span>
                        </div>
                        <div class="stat-item">
                            <i class="fas fa-thumbs-up"></i>
                            <span>${this.formatNumber(video.like_count || 0)}</span>
                        </div>
                    </div>
                    
                    <div class="video-meta">
                        <div class="video-status ${statusClass}">
                            <i class="fas fa-circle"></i>
                            ${statusText}
                        </div>
                        <div class="video-date">${publishedDate}</div>
                    </div>
                    
                    <div class="video-actions">
                        <a href="${video.url}" target="_blank" class="btn btn-sm btn-primary">
                            <i class="fab fa-youtube"></i>
                            Watch
                        </a>
                        <button class="btn btn-sm btn-secondary" onclick="channelDetailManager.deleteVideo('${video._id}')">
                            <i class="fas fa-trash"></i>
                            Delete
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    getStatusClass(status) {
        switch (status) {
            case 0: return 'status-pending';
            case 1: return 'status-processed';
            case 2: return 'status-error';
            default: return 'status-pending';
        }
    }

    getStatusText(status) {
        switch (status) {
            case 0: return 'Pending';
            case 1: return 'Processed';
            case 2: return 'Error';
            default: return 'Unknown';
        }
    }

    filterVideos(searchTerm, statusFilter = '') {
        const term = searchTerm.toLowerCase();
        const status = statusFilter;
        
        this.filteredVideos = this.videos.filter(video => {
            const matchesSearch = !term || 
                (video.title && video.title.toLowerCase().includes(term)) ||
                (video.description && video.description.toLowerCase().includes(term));
            
            const matchesStatus = !status || video.status.toString() === status;
            
            return matchesSearch && matchesStatus;
        });
        
        this.renderVideos();
    }

    async crawlVideos() {
        const youtubeChannelId = this.getYouTubeChannelId();
        console.log('MongoDB ID:', this.channelId);
        console.log('YouTube Channel ID:', youtubeChannelId);
        console.log('Channel Data:', this.channelData);
        
        if (!youtubeChannelId) {
            this.showToast('error', 'Error', 'YouTube Channel ID not found');
            return;
        }

        try {
            this.showToast('info', 'Info', `Starting to crawl videos for channel: ${youtubeChannelId}`);
            
            const response = await fetch(`${this.apiBaseUrl}/api/crawl-videos`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    channel_id: youtubeChannelId
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showToast('success', 'Success', `Successfully crawled ${data.crawled_count} videos`);
                this.loadVideos(); // Reload videos
            } else {
                this.showToast('error', 'Error', data.error || 'Failed to crawl videos');
            }
        } catch (error) {
            console.error('Error crawling videos:', error);
            this.showToast('error', 'Error', 'Unable to connect to server');
        }
    }

    async deleteVideo(videoId) {
        if (!confirm('Are you sure you want to delete this video?')) {
            return;
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/videos/${videoId}`, {
                method: 'DELETE'
            });

            const data = await response.json();

            if (data.success) {
                this.showToast('success', 'Success', 'Video deleted successfully');
                this.loadVideos(); // Reload videos
            } else {
                this.showToast('error', 'Error', data.error || 'Failed to delete video');
            }
        } catch (error) {
            console.error('Error deleting video:', error);
            this.showToast('error', 'Error', 'Unable to connect to server');
        }
    }

    updateCrawledVideosCount() {
        const crawledCount = this.videos.length;
        document.getElementById('crawledVideos').textContent = this.formatNumber(crawledCount);
    }

    showLoading(show) {
        const loading = document.getElementById('loading');
        const videosGrid = document.getElementById('videosGrid');
        
        if (show) {
            loading.style.display = 'block';
            videosGrid.style.display = 'none';
        } else {
            loading.style.display = 'none';
            videosGrid.style.display = 'grid';
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

    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }
}

// Initialize the application
let channelDetailManager;
document.addEventListener('DOMContentLoaded', () => {
    channelDetailManager = new ChannelDetailManager();
});
