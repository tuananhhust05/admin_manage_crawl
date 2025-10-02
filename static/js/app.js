// YouTube Channels Manager - JavaScript
class YouTubeChannelsManager {
    constructor() {
        this.apiBaseUrl = window.location.origin;
        this.channels = [];
        this.filteredChannels = [];
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadChannels();
    }

    bindEvents() {
        // Add channel button
        document.getElementById('addChannelBtn').addEventListener('click', () => {
            this.showAddChannelModal();
        });

        // Search functionality
        document.getElementById('searchInput').addEventListener('input', (e) => {
            this.filterChannels(e.target.value);
        });

        // Add channel form
        document.getElementById('addChannelForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.addChannel();
        });

        // Modal close on outside click
        document.getElementById('addChannelModal').addEventListener('click', (e) => {
            if (e.target.id === 'addChannelModal') {
                this.closeAddChannelModal();
            }
        });
    }

    async loadChannels() {
        try {
            this.showLoading(true);
            const response = await fetch(`${this.apiBaseUrl}/api/youtube-channels`);
            const data = await response.json();

            if (data.success) {
                this.channels = data.data;
                this.filteredChannels = [...this.channels];
                this.renderChannels();
                this.updateStats();
            } else {
                this.showToast('error', 'Error', 'Failed to load channels');
            }
        } catch (error) {
            console.error('Error loading channels:', error);
            this.showToast('error', 'Error', 'Unable to connect to server');
        } finally {
            this.showLoading(false);
        }
    }

    renderChannels() {
        const channelsGrid = document.getElementById('channelsGrid');
        const emptyState = document.getElementById('emptyState');

        if (this.filteredChannels.length === 0) {
            channelsGrid.innerHTML = '';
            emptyState.style.display = 'block';
            return;
        }

        emptyState.style.display = 'none';
        channelsGrid.innerHTML = this.filteredChannels.map(channel => this.createChannelCard(channel)).join('');
    }

    createChannelCard(channel) {
        const createdDate = new Date(channel.created_at).toLocaleDateString('en-US');
        const updatedDate = new Date(channel.updated_at).toLocaleDateString('en-US');
        
        return `
            <div class="channel-card" data-id="${channel._id}">
                <div class="channel-header">
                    <div class="channel-info">
                        <h3>${channel.title || 'Untitled Channel'}</h3>
                        <p>${channel.url}</p>
                    </div>
                    <div class="channel-actions">
                        <button class="action-btn view-btn" onclick="channelsManager.viewChannel('${channel._id}')" title="View Details">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="action-btn edit-btn" onclick="channelsManager.editChannel('${channel._id}')" title="Edit">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="action-btn delete-btn" onclick="channelsManager.deleteChannel('${channel._id}')" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
                
                <div class="channel-stats">
                    <div class="stat-item">
                        <span class="number">${this.formatNumber(channel.subscriber_count || 0)}</span>
                        <span class="label">Subscribers</span>
                    </div>
                    <div class="stat-item">
                        <span class="number">${this.formatNumber(channel.video_count || 0)}</span>
                        <span class="label">Videos</span>
                    </div>
                </div>
                
                ${channel.description ? `<p style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-bottom: var(--spacing-md);">${channel.description}</p>` : ''}
                
                <div class="channel-meta">
                    <span>ID: ${channel.channel_id}</span>
                    <div>
                        <div>Created: ${createdDate}</div>
                        <div>Updated: ${updatedDate}</div>
                    </div>
                </div>
            </div>
        `;
    }

    updateStats() {
        const totalChannels = this.channels.length;
        const totalSubscribers = this.channels.reduce((sum, channel) => sum + (channel.subscriber_count || 0), 0);
        const totalVideos = this.channels.reduce((sum, channel) => sum + (channel.video_count || 0), 0);

        document.getElementById('totalChannels').textContent = this.formatNumber(totalChannels);
        document.getElementById('totalSubscribers').textContent = this.formatNumber(totalSubscribers);
        document.getElementById('totalVideos').textContent = this.formatNumber(totalVideos);
    }

    filterChannels(searchTerm) {
        const term = searchTerm.toLowerCase();
        this.filteredChannels = this.channels.filter(channel => 
            (channel.title && channel.title.toLowerCase().includes(term)) ||
            (channel.url && channel.url.toLowerCase().includes(term)) ||
            (channel.channel_id && channel.channel_id.toLowerCase().includes(term)) ||
            (channel.description && channel.description.toLowerCase().includes(term))
        );
        this.renderChannels();
    }

    showAddChannelModal() {
        document.getElementById('addChannelModal').classList.add('show');
        document.body.style.overflow = 'hidden';
    }

    closeAddChannelModal() {
        document.getElementById('addChannelModal').classList.remove('show');
        document.body.style.overflow = 'auto';
        document.getElementById('addChannelForm').reset();
    }

    async addChannel() {
        const form = document.getElementById('addChannelForm');
        const formData = new FormData(form);
        
        const channelData = {
            url: formData.get('url'),
            channel_id: formData.get('channel_id'),
            title: formData.get('title') || '',
            description: formData.get('description') || '',
            subscriber_count: parseInt(formData.get('subscriber_count')) || 0,
            video_count: parseInt(formData.get('video_count')) || 0
        };

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/youtube-channels`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(channelData)
            });

            const data = await response.json();

            if (data.success) {
                this.showToast('success', 'Success', 'YouTube channel added successfully');
                this.closeAddChannelModal();
                this.loadChannels(); // Reload channels
            } else {
                this.showToast('error', 'Error', data.error || 'Failed to add channel');
            }
        } catch (error) {
            console.error('Error adding channel:', error);
            this.showToast('error', 'Error', 'Unable to connect to server');
        }
    }

    async deleteChannel(channelId) {
        if (!confirm('Are you sure you want to delete this channel?')) {
            return;
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/youtube-channels/${channelId}`, {
                method: 'DELETE'
            });

            const data = await response.json();

            if (data.success) {
                this.showToast('success', 'Success', 'YouTube channel deleted successfully');
                this.loadChannels(); // Reload channels
            } else {
                this.showToast('error', 'Error', data.error || 'Failed to delete channel');
            }
        } catch (error) {
            console.error('Error deleting channel:', error);
            this.showToast('error', 'Error', 'Unable to connect to server');
        }
    }

    viewChannel(channelId) {
        // Navigate to channel detail page with MongoDB _id
        // The detail page will load channel data and get YouTube channel_id
        window.location.href = `/channel-detail?id=${channelId}`;
    }

    editChannel(channelId) {
        const channel = this.channels.find(c => c._id === channelId);
        if (!channel) return;

        // Fill form with existing data
        document.getElementById('channelUrl').value = channel.url;
        document.getElementById('channelId').value = channel.channel_id;
        document.getElementById('channelTitle').value = channel.title || '';
        document.getElementById('channelDescription').value = channel.description || '';
        document.getElementById('subscriberCount').value = channel.subscriber_count || 0;
        document.getElementById('videoCount').value = channel.video_count || 0;

        // Change form to update mode
        const form = document.getElementById('addChannelForm');
        form.dataset.mode = 'edit';
        form.dataset.channelId = channelId;

        // Update modal title and button
        document.querySelector('.modal-header h2').textContent = 'Edit YouTube Channel';
        document.querySelector('.modal-footer .btn-primary').innerHTML = '<i class="fas fa-save"></i> Update';

        this.showAddChannelModal();
    }

    showLoading(show) {
        const loading = document.getElementById('loading');
        const channelsGrid = document.getElementById('channelsGrid');
        
        if (show) {
            loading.style.display = 'block';
            channelsGrid.style.display = 'none';
        } else {
            loading.style.display = 'none';
            channelsGrid.style.display = 'grid';
        }
    }

    showToast(type, title, message) {
        const toastContainer = document.getElementById('toastContainer');
        const toastId = 'toast-' + Date.now();
        
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle'
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

// Global functions for HTML onclick events
function showAddChannelModal() {
    channelsManager.showAddChannelModal();
}

function closeAddChannelModal() {
    channelsManager.closeAddChannelModal();
}

// Initialize the application
let channelsManager;
document.addEventListener('DOMContentLoaded', () => {
    channelsManager = new YouTubeChannelsManager();
});

// Add CSS animation for toast removal
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOutRight {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(100%);
        }
    }
`;
document.head.appendChild(style);
