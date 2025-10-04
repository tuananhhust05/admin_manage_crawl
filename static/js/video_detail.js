// Video Detail Page JavaScript
class VideoDetailManager {
    constructor() {
        this.apiBaseUrl = window.location.origin;
        this.videoId = this.getVideoIdFromUrl();
        this.videoData = null;
        this.srtFiles = [];
        this.chunks = [];
        this.filteredChunks = [];
        this.init();
    }

    async init() {
        this.bindEvents();
        await this.loadVideoData();
        this.loadSrtFiles();
        this.loadTranscription();
    }

    getVideoIdFromUrl() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('id');
    }

    bindEvents() {
        // 🔄 FULL PROCESS button - Delete old data → Crawl SRT → Chunk → Vectorize → Save to Elasticsearch
        document.getElementById('fullProcessBtn').addEventListener('click', () => {
            this.fullProcessVideo();
        });

        // Refresh SRT button
        document.getElementById('refreshSrtBtn').addEventListener('click', () => {
            this.loadSrtFiles();
        });

        // Transcription search
        document.getElementById('transcriptionSearch').addEventListener('input', (e) => {
            this.filterTranscription(e.target.value);
        });

        // Export transcription
        document.getElementById('exportTranscriptionBtn').addEventListener('click', () => {
            this.exportTranscription();
        });
    }

    async loadVideoData() {
        if (!this.videoId) {
            this.showToast('error', 'Error', 'Video ID not found');
            return;
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/videos/${this.videoId}`);
            const data = await response.json();

            if (data.success) {
                this.videoData = data.data.video;
                this.srtFiles = data.data.srt_files || [];
                this.chunks = data.data.chunks || [];
                this.filteredChunks = [...this.chunks];
                this.updateVideoInfo();
                this.renderTranscription();
            } else {
                this.showToast('error', 'Error', 'Failed to load video data');
            }
        } catch (error) {
            console.error('Error loading video data:', error);
            this.showToast('error', 'Error', 'Unable to connect to server');
        }
    }

    updateVideoInfo() {
        if (!this.videoData) return;

        const video = this.videoData;

        document.getElementById('videoTitle').textContent = video.title || 'Video Details';
        document.getElementById('videoName').textContent = video.title || 'Untitled Video';
        document.getElementById('videoUrl').textContent = video.url;
        document.getElementById('videoDescription').textContent = video.description || 'No description available';
        
        // Update thumbnail
        const thumbnailImg = document.getElementById('videoThumbnail');
        if (video.thumbnail_url) {
            thumbnailImg.src = video.thumbnail_url;
            thumbnailImg.style.display = 'block';
        } else {
            thumbnailImg.style.display = 'none';
        }

        // Update stats
        document.getElementById('viewCount').textContent = this.formatNumber(video.view_count || 0);
        document.getElementById('likeCount').textContent = this.formatNumber(video.like_count || 0);
        document.getElementById('chunksCount').textContent = this.chunks.length || 0;
        document.getElementById('videoDuration').textContent = video.duration || 'N/A';
        
        // Update SRT status
        const srtStatus = this.getSrtStatusText(this.videoData.srt_status);
        document.getElementById('srtStatus').textContent = srtStatus;
    }

    getSrtStatusText(status) {
        switch (status) {
            case 0: return 'Pending';
            case 1: return 'Processed';
            case 2: return 'Completed';
            default: return 'Pending';
        }
    }

    updateVideoStatus(status) {
        // Cập nhật status hiển thị trong UI
        const srtStatus = this.getSrtStatusText(status);
        document.getElementById('srtStatus').textContent = srtStatus;
        
        // Cập nhật video data
        if (this.videoData) {
            this.videoData.srt_status = status;
        }
        
        // Trigger event để parent page có thể cập nhật
        window.dispatchEvent(new CustomEvent('videoStatusUpdated', {
            detail: {
                videoId: this.videoId,
                status: status
            }
        }));
    }

    async loadSrtFiles() {
        if (!this.videoData) return;

        try {
            this.showSrtLoading(true);
            const response = await fetch(`${this.apiBaseUrl}/api/srt-files`);
            const data = await response.json();

            if (data.success) {
                // Filter SRT files for this video
                this.srtFiles = data.data.filter(srt => srt.video_url === this.videoData.url);
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
                            `<button class="btn btn-sm btn-warning" onclick="videoDetailManager.processSrtFile('${srtFile._id}')">
                                <i class="fas fa-cogs"></i>
                                Process
                            </button>` : 
                            `<button class="btn btn-sm btn-info" onclick="videoDetailManager.viewSrtChunks('${srtFile._id}')">
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
            case 2: return 'status-completed';
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


    async crawlVideoSrt() {
        if (!this.videoId) {
            this.showToast('error', 'Error', 'Video ID not found');
            return;
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/crawl-video-srt`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    video_id: this.videoId
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showToast('success', 'Success', 'SRT file downloaded successfully');
                this.loadVideoData(); // Reload video data
                this.loadSrtFiles(); // Reload SRT files
            } else {
                this.showToast('error', 'Error', data.error || 'Failed to download SRT');
            }
        } catch (error) {
            console.error('Error crawling video SRT:', error);
            this.showToast('error', 'Error', 'Unable to connect to server');
        }
    }

    async processVideoSrt() {
        if (!this.videoId) {
            this.showToast('error', 'Error', 'Video ID not found');
            return;
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/process-video-srt`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    video_id: this.videoId
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showToast('success', 'Success', 
                    `Successfully processed ${data.processed_files} SRT files with ${data.chunks_count} chunks`);
                this.loadVideoData(); // Reload video data
                this.loadSrtFiles(); // Reload SRT files
                this.loadTranscription(); // Reload transcription
            } else {
                this.showToast('error', 'Error', data.error || 'Failed to process SRT');
            }
        } catch (error) {
            console.error('Error processing video SRT:', error);
            this.showToast('error', 'Error', 'Unable to connect to server');
        }
    }

    async processSrtFile(srtId) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/process-srt`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    srt_id: srtId
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showToast('success', 'Success', 
                    `Successfully processed SRT file with ${data.chunks_count} chunks`);
                this.loadVideoData(); // Reload video data
                this.loadSrtFiles(); // Reload SRT files
                this.loadTranscription(); // Reload transcription
            } else {
                this.showToast('error', 'Error', data.error || 'Failed to process SRT file');
            }
        } catch (error) {
            console.error('Error processing SRT file:', error);
            this.showToast('error', 'Error', 'Unable to connect to server');
        }
    }

    async viewSrtChunks(srtId) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/srt-chunks/${srtId}`);
            const data = await response.json();

            if (data.success) {
                this.showSrtChunksModal(data.data);
            } else {
                this.showToast('error', 'Error', 'Failed to load SRT chunks');
            }
        } catch (error) {
            console.error('Error loading SRT chunks:', error);
            this.showToast('error', 'Error', 'Unable to connect to server');
        }
    }

    showSrtChunksModal(chunks) {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>SRT Chunks (${chunks.length} total)</h3>
                    <button class="modal-close" onclick="this.closest('.modal').remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="chunks-list">
                        ${chunks.map((chunk, index) => `
                            <div class="chunk-item">
                                <div class="chunk-header">
                                    <span class="chunk-index">Chunk ${index + 1}</span>
                                    <span class="chunk-time">${chunk.time}</span>
                                </div>
                                <div class="chunk-text">${chunk.text}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
    }

    async loadTranscription() {
        if (!this.videoData) return;

        try {
            this.showTranscriptionLoading(true);
            // Transcription data is already loaded in loadVideoData()
            this.renderTranscription();
        } catch (error) {
            console.error('Error loading transcription:', error);
            this.showToast('error', 'Error', 'Unable to load transcription');
        } finally {
            this.showTranscriptionLoading(false);
        }
    }

    renderTranscription() {
        const transcriptionContent = document.getElementById('transcriptionContent');
        const emptyState = document.getElementById('transcriptionEmptyState');

        if (this.filteredChunks.length === 0) {
            transcriptionContent.innerHTML = '';
            emptyState.style.display = 'block';
            return;
        }

        emptyState.style.display = 'none';
        transcriptionContent.innerHTML = this.filteredChunks.map((chunk, index) => `
            <div class="transcription-chunk" data-index="${index}">
                <div class="chunk-header">
                    <span class="chunk-index">Chunk ${chunk.chunk_index + 1}</span>
                    <span class="chunk-time">${chunk.time}</span>
                </div>
                <div class="chunk-text">${chunk.text}</div>
            </div>
        `).join('');
    }

    filterTranscription(searchTerm) {
        const term = searchTerm.toLowerCase();
        
        this.filteredChunks = this.chunks.filter(chunk => 
            chunk.text.toLowerCase().includes(term)
        );
        
        this.renderTranscription();
    }

    exportTranscription() {
        if (this.chunks.length === 0) {
            this.showToast('warning', 'Warning', 'No transcription to export');
            return;
        }

        const transcriptionText = this.chunks.map(chunk => 
            `[${chunk.time}] ${chunk.text}`
        ).join('\n\n');

        const blob = new Blob([transcriptionText], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `transcription_${this.videoId}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this.showToast('success', 'Success', 'Transcription exported successfully');
    }

    showSrtLoading(show) {
        const loading = document.getElementById('srtLoading');
        const srtGrid = document.getElementById('srtGrid');
        
        if (show) {
            loading.style.display = 'block';
            srtGrid.style.display = 'none';
        } else {
            loading.style.display = 'none';
            srtGrid.style.display = 'grid';
        }
    }

    showTranscriptionLoading(show) {
        const loading = document.getElementById('transcriptionLoading');
        const transcriptionContent = document.getElementById('transcriptionContent');
        
        if (show) {
            loading.style.display = 'block';
            transcriptionContent.style.display = 'none';
        } else {
            loading.style.display = 'none';
            transcriptionContent.style.display = 'block';
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

    // 🔄 FULL PROCESS: Delete old data → Crawl SRT → Chunk → Vectorize → Save to Elasticsearch
    async fullProcessVideo() {
        try {
            // Hiển thị thông báo bắt đầu
            this.showToast('info', '🔄 Full Process Started', 'Deleting old data → Crawling SRT → Chunking → Vector Encoding → Elasticsearch Indexing...');
            
            // Disable button để tránh click nhiều lần
            const fullProcessBtn = document.getElementById('fullProcessBtn');
            const originalText = fullProcessBtn.innerHTML;
            fullProcessBtn.disabled = true;
            fullProcessBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';

            // BƯỚC 1: XÓA DỮ LIỆU CŨ
            this.showToast('info', '🗑️ Step 1: Cleaning old data', 'Deleting old SRT files, chunks, and Elasticsearch records...');
            
            const cleanupResponse = await fetch(`${this.apiBaseUrl}/api/cleanup-video-data`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    video_id: this.videoId
                })
            });

            const cleanupResult = await cleanupResponse.json();
            if (!cleanupResult.success) {
                console.warn('Cleanup warning:', cleanupResult.message);
            }

            // BƯỚC 2: CRAWL & CHUNK & VECTORIZE & INDEX
            this.showToast('info', '🎬 Step 2: Processing video', 'Crawling SRT → Chunking → Vector Encoding → Elasticsearch Indexing...');

            const response = await fetch(`${this.apiBaseUrl}/api/crawl-and-chunk-video`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    video_id: this.videoId
                })
            });

            const result = await response.json();

            if (result.success) {
                // Hiển thị kết quả chi tiết
                const message = `
                    ✅ Full Process Complete!<br>
                    🗑️ Old data: Cleaned<br>
                    📄 SRT Chunks: ${result.chunks_count}<br>
                    🤖 Vector Embeddings: Generated (768D)<br>
                    💾 Elasticsearch: ${result.elasticsearch.indexed_count} chunks indexed<br>
                    🔍 Ready for semantic search!
                `;
                
                this.showToast('success', '🎉 Full Process Complete!', message, 8000);
                
                // Reload data để cập nhật UI
                await this.loadVideoData();
                await this.loadTranscription();
                
            } else {
                this.showToast('error', 'Full Process Failed', result.message || 'Unknown error occurred');
            }

        } catch (error) {
            console.error('Full Process error:', error);
            this.showToast('error', 'Processing Error', `Failed to process video: ${error.message}`);
        } finally {
            // Re-enable button
            const fullProcessBtn = document.getElementById('fullProcessBtn');
            fullProcessBtn.disabled = false;
            fullProcessBtn.innerHTML = '<i class="fas fa-sync-alt"></i> Full Process';
        }
    }

}

// Initialize the application
let videoDetailManager;
document.addEventListener('DOMContentLoaded', () => {
    videoDetailManager = new VideoDetailManager();
});

