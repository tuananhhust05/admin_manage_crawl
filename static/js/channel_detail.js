// Channel Detail Page JavaScript
class ChannelDetailManager {
    constructor() {
        this.apiBaseUrl = window.location.origin;
        this.channelId = this.getChannelIdFromUrl();
        this.videos = [];
        this.filteredVideos = [];
        this.srtFiles = [];
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

    handleVideoStatusUpdate(detail) {
        // Cập nhật status của video trong danh sách
        const videoIndex = this.videos.findIndex(video => video._id === detail.videoId);
        if (videoIndex !== -1) {
            this.videos[videoIndex].srt_status = detail.status;
            this.filteredVideos = [...this.videos];
            this.renderVideos();
            
            // Show notification
            this.showToast('success', 'Status Updated', 
                `Video status updated to ${this.getSrtStatusText(detail.status)}`);
        }
    }

    bindEvents() {
        // Crawl videos button
        const crawlVideosBtn = document.getElementById('crawlVideosBtn');
        if (crawlVideosBtn) {
            crawlVideosBtn.addEventListener('click', () => {
            this.crawlVideos();
        });
        }

        const crawlVideosBtnEmpty = document.getElementById('crawlVideosBtnEmpty');
        if (crawlVideosBtnEmpty) {
            crawlVideosBtnEmpty.addEventListener('click', () => {
            this.crawlVideos();
        });
        }


        // Listen for video status updates from video detail page
        window.addEventListener('videoStatusUpdated', (event) => {
            this.handleVideoStatusUpdate(event.detail);
        });

        // Video search
        const videoSearchInput = document.getElementById('videoSearchInput');
        if (videoSearchInput) {
            videoSearchInput.addEventListener('input', (e) => {
            this.filterVideos(e.target.value);
        });
        }

        // Status filter
        const statusFilter = document.getElementById('statusFilter');
        if (statusFilter) {
            statusFilter.addEventListener('change', (e) => {
                this.filterVideos(document.getElementById('videoSearchInput')?.value || '', e.target.value);
            });
        }
    }

    async loadChannelData() {
        if (!this.channelId) {
            this.showToast('error', 'Error', 'Channel ID not found');
            return;
        }

        try {
            console.log('Loading channel data for ID:', this.channelId);
            const response = await fetch(`${this.apiBaseUrl}/api/youtube-channels/${this.channelId}`);
            const data = await response.json();
            
            console.log('Channel API response:', data);

            if (data.success) {
                this.channelData = data.data;
                console.log('Channel data loaded:', this.channelData);
                this.updateChannelInfo();
            } else {
                console.error('Failed to load channel data:', data.error);
                this.showToast('error', 'Error', `Failed to load channel data: ${data.error}`);
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
                        <a href="/video-detail?id=${video._id}" class="btn btn-sm btn-info">
                            <i class="fas fa-info-circle"></i>
                            Details
                        </a>
                        <button class="btn btn-sm btn-success" onclick="channelDetailManager.crawlVideoSrt('${video._id}')">
                            <i class="fas fa-closed-captioning"></i>
                            SRT
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

    // ==============================================================================
    // SRT FUNCTIONS
    // ==============================================================================

    async loadSrtFiles() {
        try {
            this.showSrtLoading(true);
            const response = await fetch(`${this.apiBaseUrl}/api/srt-files`);
            const data = await response.json();

            if (data.success) {
                this.srtFiles = data.data;
                this.renderSrtFiles();
            } else {
                this.showToast('error', 'Error', 'Failed to load SRT files');
            }
        } catch (error) {
            console.error('Error loading SRT files:', error);
            this.showToast('error', 'Error', 'Unable to connect to server');
        } finally {
            this.showSrtLoading(false);
        }
    }

    renderSrtFiles() {
        const srtGrid = document.getElementById('srtGrid');
        const emptyState = document.getElementById('srtEmptyState');

        if (this.srtFiles.length === 0) {
            srtGrid.innerHTML = '';
            emptyState.style.display = 'block';
            return;
        }

        emptyState.style.display = 'none';
        srtGrid.innerHTML = this.srtFiles.map(srtFile => this.createSrtCard(srtFile)).join('');
    }

    createSrtCard(srtFile) {
        const createdDate = new Date(srtFile.created_at).toLocaleDateString('en-US');
        const statusClass = this.getSrtStatusClass(srtFile.status);
        const statusText = this.getSrtStatusText(srtFile.status);
        
        return `
            <div class="srt-card" data-id="${srtFile._id}">
                <div class="srt-header">
                    <div class="srt-icon">
                        <i class="fas fa-closed-captioning"></i>
                    </div>
                    <div class="srt-info">
                        <h4 class="srt-filename">${srtFile.srt_filename}</h4>
                        <p class="srt-url">${srtFile.video_url}</p>
                    </div>
                </div>
                
                <div class="srt-content">
                    <div class="srt-stats">
                        <div class="stat-item">
                            <i class="fas fa-file-alt"></i>
                            <span>${srtFile.chunks_count || 0} chunks</span>
                        </div>
                        <div class="stat-item">
                            <i class="fas fa-calendar"></i>
                            <span>${createdDate}</span>
                        </div>
                    </div>
                    
                    <div class="srt-meta">
                        <div class="srt-status ${statusClass}">
                            <i class="fas fa-circle"></i>
                            ${statusText}
                        </div>
                    </div>
                    
                    <div class="srt-actions">
                        ${srtFile.status === 0 ? 
                            `<button class="btn btn-sm btn-warning" onclick="channelDetailManager.processSrtFile('${srtFile._id}')">
                                <i class="fas fa-cogs"></i>
                                Process
                            </button>` : 
                            `<button class="btn btn-sm btn-info" onclick="channelDetailManager.viewSrtChunks('${srtFile._id}')">
                                <i class="fas fa-eye"></i>
                                View Chunks
                            </button>`
                        }
                    </div>
                </div>
            </div>
        `;
    }

    getSrtStatusClass(status) {
        switch (status) {
            case 0: return 'status-pending';
            case 1: return 'status-processed';
            case 2: return 'status-error';
            default: return 'status-pending';
        }
    }

    getSrtStatusText(status) {
        switch (status) {
            case 0: return 'Pending';
            case 1: return 'Processed';
            case 2: return 'Completed';
            default: return 'Pending';
        }
    }


    async crawlVideoSrt(videoId) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/crawl-and-chunk-video`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    video_id: videoId
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showToast('success', 'Success', 
                    `Successfully crawled and chunked video with ${data.chunks_count} chunks`);
                this.loadVideos(); // Reload videos to update status
            } else {
                this.showToast('error', 'Error', data.error || 'Failed to crawl and chunk video');
            }
        } catch (error) {
            console.error('Error crawling video SRT:', error);
            this.showToast('error', 'Error', 'Unable to connect to server');
        }
    }
}

// Initialize the application
let channelDetailManager;
document.addEventListener('DOMContentLoaded', () => {
    channelDetailManager = new ChannelDetailManager();
});
