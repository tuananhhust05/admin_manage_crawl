import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import numpy as np
from sentence_transformers import SentenceTransformer
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ElasticsearchService:
    def __init__(self):
        """Initialize Elasticsearch service with vector embedding capabilities"""
        self.es_host = os.getenv('ELASTICSEARCH_HOST', '37.27.181.54')
        self.es_port = int(os.getenv('ELASTICSEARCH_PORT', 9200))
        self.es_user = os.getenv('ELASTICSEARCH_USER', '')
        self.es_password = os.getenv('ELASTICSEARCH_PASSWORD', '')
        self.index_name = os.getenv('ELASTICSEARCH_INDEX', 'articles')
        
        # Initialize Elasticsearch client
        self.es = self._init_elasticsearch()
        
        # Initialize sentence transformer model
        self.model = self._init_sentence_transformer()
        
        # Create index if not exists (only if both services are available)
        if self.es and self.model:
            self._create_index()
        else:
            logger.warning("⚠️ Skipping index creation - Elasticsearch or model not available")
    
    def _init_elasticsearch(self) -> Elasticsearch:
        """Initialize Elasticsearch client"""
        try:
            logger.info(f"🔄 Initializing Elasticsearch connection to {self.es_host}:{self.es_port}")
            
            if self.es_user and self.es_password:
                logger.info("🔐 Using authentication")
                es = Elasticsearch(
                    [{'host': self.es_host, 'port': self.es_port}],
                    http_auth=(self.es_user, self.es_password),
                    verify_certs=False,
                    ssl_show_warn=False
                )
            else:
                logger.info("🔓 No authentication")
                es = Elasticsearch([{'host': self.es_host, 'port': self.es_port}])
            
            # Test connection
            if es.ping():
                logger.info(f"✅ Connected to Elasticsearch at {self.es_host}:{self.es_port}")
                return es
            else:
                logger.error("❌ Failed to connect to Elasticsearch")
                return None
        except Exception as e:
            logger.error(f"❌ Elasticsearch connection error: {str(e)}")
            return None
    
    def _init_sentence_transformer(self) -> Optional[SentenceTransformer]:
        """Initialize sentence transformer model for vectorization"""
        try:
            # Use all-distilroberta-v1 model as requested
            model_name = "all-distilroberta-v1"  # High quality embeddings
            logger.info(f"🔄 Loading sentence transformer model: {model_name}")
            logger.info("⏳ This may take a few minutes on first run (downloading model)...")
            
            model = SentenceTransformer(model_name)
            logger.info("✅ Sentence transformer model loaded successfully")
            return model
        except Exception as e:
            logger.error(f"❌ Failed to load sentence transformer model: {str(e)}")
            logger.error("💡 Make sure you have internet connection and sufficient disk space")
            return None
    
    def _create_index(self):
        """Create Elasticsearch index with vector mapping"""
        if not self.es:
            logger.warning("⚠️ Cannot create index - Elasticsearch not available")
            return
        
        try:
            logger.info(f"🔄 Creating/checking index: {self.index_name}")
            # Check if index exists
            if self.es.indices.exists(index=self.index_name):
                logger.info(f"📁 Index '{self.index_name}' already exists")
                return
            
            # Define index mapping with vector field
            mapping = {
                "settings": {
                    "analysis": {
                        "analyzer": {
                            "custom_text_analyzer": {
                                "type": "custom",
                                "tokenizer": "standard",
                                "filter": ["lowercase", "stop", "snowball"]
                            }
                        }
                    }
                },
                "mappings": {
                    "properties": {
                        "url_channel": {
                            "type": "keyword",
                            "index": True
                        },
                        "url": {
                            "type": "keyword", 
                            "index": True
                        },
                        "origin_content": {
                            "type": "text",
                            "analyzer": "custom_text_analyzer",
                            "search_analyzer": "custom_text_analyzer",
                            "fields": {
                                "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        },
                        "vector": {
                            "type": "dense_vector",
                            "dims": 768,  # all-distilroberta-v1 produces 768-dimensional vectors
                            "index": True,
                            "similarity": "cosine"
                        },
                        "time": {
                            "type": "text"
                        },
                        # Additional fields for video management
                        "video_id": {
                            "type": "keyword"
                        },
                        "chunk_id": {
                            "type": "keyword"
                        },
                        "start_time": {
                            "type": "float"
                        },
                        "end_time": {
                            "type": "float"
                        },
                        "duration": {
                            "type": "float"
                        },
                        "chunk_index": {
                            "type": "integer"
                        },
                        "video_title": {
                            "type": "text",
                            "analyzer": "custom_text_analyzer"
                        },
                        "channel_name": {
                            "type": "keyword"
                        },
                        "created_at": {
                            "type": "date"
                        },
                        "updated_at": {
                            "type": "date"
                        }
                    }
                },
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0,
                    "index": {
                        "knn": True,
                        "knn.algo_param.ef_search": 100
                    }
                }
            }
            
            # Create index
            self.es.indices.create(index=self.index_name, body=mapping)
            logger.info(f"✅ Created Elasticsearch index: {self.index_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to create index: {str(e)}")
            logger.error("💡 Check Elasticsearch connection and permissions")
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate vector embeddings for a list of texts"""
        if not self.model:
            logger.error("❌ Sentence transformer model not available")
            return []
        
        try:
            logger.info(f"🔄 Generating embeddings for {len(texts)} texts...")
            embeddings = self.model.encode(texts, convert_to_tensor=False)
            
            # Convert numpy arrays to lists
            embeddings_list = [embedding.tolist() for embedding in embeddings]
            logger.info(f"✅ Generated {len(embeddings_list)} embeddings")
            
            return embeddings_list
        except Exception as e:
            logger.error(f"❌ Failed to generate embeddings: {str(e)}")
            return []
    
    def index_chunks(self, chunks_data: List[Dict[str, Any]], video_info: Dict[str, Any]) -> Dict[str, Any]:
        """Index video chunks with vector embeddings to Elasticsearch"""
        if not self.es or not self.model:
            return {
                'success': False,
                'message': 'Elasticsearch or model not available',
                'indexed_count': 0
            }
        
        try:
            logger.info(f"🔄 Indexing {len(chunks_data)} chunks to Elasticsearch...")
            
            # Prepare documents for indexing
            documents = []
            texts_for_embedding = []
            
            for chunk in chunks_data:
                # Prepare text for embedding (combine multiple fields for better search)
                search_text = f"{chunk.get('text', '')} {video_info.get('title', '')} {video_info.get('channel_name', '')}"
                texts_for_embedding.append(search_text)
                
                # Prepare document with correct structure
                doc = {
                    '_index': self.index_name,
                    '_id': f"{video_info['video_id']}_{chunk['chunk_id']}",
                    '_source': {
                        # Main fields theo yêu cầu
                        'url_channel': video_info.get('channel_url', ''),  # Link channel
                        'url': video_info.get('url', ''),  # Link video
                        'origin_content': chunk.get('text', ''),  # Nội dung gốc
                        'time': str(chunk.get('start_time', 0)),  # Thời gian dạng text
                        
                        # Additional fields for video management
                        'video_id': video_info['video_id'],
                        'chunk_id': chunk['chunk_id'],
                        'start_time': chunk.get('start_time', 0),
                        'end_time': chunk.get('end_time', 0),
                        'duration': chunk.get('duration', 0),
                        'chunk_index': chunk.get('chunk_index', 0),
                        'video_title': video_info.get('title', ''),
                        'channel_name': video_info.get('channel_name', ''),
                        'created_at': datetime.utcnow().isoformat(),
                        'updated_at': datetime.utcnow().isoformat()
                    }
                }
                documents.append(doc)
            
            # Generate embeddings for all texts
            embeddings = self.generate_embeddings(texts_for_embedding)
            
            if not embeddings:
                return {
                    'success': False,
                    'message': 'Failed to generate embeddings',
                    'indexed_count': 0
                }
            
            # Add embeddings to documents
            for i, doc in enumerate(documents):
                if i < len(embeddings):
                    doc['_source']['vector'] = embeddings[i]  # Sử dụng field name 'vector' theo yêu cầu
            
            # Bulk index documents
            success_count, failed_items = bulk(self.es, documents, chunk_size=100)
            
            logger.info(f"✅ Successfully indexed {success_count} chunks to Elasticsearch")
            
            return {
                'success': True,
                'message': f'Successfully indexed {success_count} chunks',
                'indexed_count': success_count,
                'failed_count': len(failed_items) if failed_items else 0
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to index chunks: {str(e)}")
            logger.error("💡 Check Elasticsearch connection and index mapping")
            return {
                'success': False,
                'message': f'Indexing failed: {str(e)}',
                'indexed_count': 0
            }
    
    def search_chunks(self, query: str, video_id: Optional[str] = None, 
                     size: int = 10, from_: int = 0) -> Dict[str, Any]:
        """Search chunks using semantic similarity"""
        if not self.es or not self.model:
            return {
                'success': False,
                'message': 'Elasticsearch or model not available',
                'results': []
            }
        
        try:
            logger.info(f"🔍 Searching for: '{query}'")
            
            # Generate embedding for search query
            query_embedding = self.model.encode([query], convert_to_tensor=False)[0].tolist()
            
            # Build search query
            search_body = {
                "size": size,
                "from": from_,
                "query": {
                    "bool": {
                        "must": [
                            {
                                "knn": {
                                    "vector": {
                                        "vector": query_embedding,
                                        "k": size
                                    }
                                }
                            }
                        ]
                    }
                },
                "_source": [
                    "url_channel", "url", "origin_content", "time", "vector",
                    "video_id", "chunk_id", "start_time", "end_time", 
                    "duration", "chunk_index", "video_title", "channel_name"
                ],
                "highlight": {
                    "fields": {
                        "origin_content": {
                            "fragment_size": 150,
                            "number_of_fragments": 3
                        }
                    }
                }
            }
            
            # Add video filter if specified
            if video_id:
                search_body["query"]["bool"]["filter"] = [
                    {"term": {"video_id": video_id}}
                ]
            
            # Execute search
            response = self.es.search(index=self.index_name, body=search_body)
            
            # Process results
            results = []
            for hit in response['hits']['hits']:
                result = {
                    # Main fields theo yêu cầu
                    'url_channel': hit['_source'].get('url_channel', ''),
                    'url': hit['_source'].get('url', ''),
                    'origin_content': hit['_source'].get('origin_content', ''),
                    'time': hit['_source'].get('time', ''),
                    
                    # Additional fields
                    'video_id': hit['_source'].get('video_id', ''),
                    'chunk_id': hit['_source'].get('chunk_id', ''),
                    'start_time': hit['_source'].get('start_time', 0),
                    'end_time': hit['_source'].get('end_time', 0),
                    'duration': hit['_source'].get('duration', 0),
                    'chunk_index': hit['_source'].get('chunk_index', 0),
                    'video_title': hit['_source'].get('video_title', ''),
                    'channel_name': hit['_source'].get('channel_name', ''),
                    'score': hit['_score'],
                    'highlights': hit.get('highlight', {})
                }
                results.append(result)
            
            logger.info(f"✅ Found {len(results)} results for query: '{query}'")
            
            return {
                'success': True,
                'message': f'Found {len(results)} results',
                'results': results,
                'total': response['hits']['total']['value'],
                'took': response['took']
            }
            
        except Exception as e:
            logger.error(f"❌ Search failed: {str(e)}")
            return {
                'success': False,
                'message': f'Search failed: {str(e)}',
                'results': []
            }
    
    def delete_video_chunks(self, video_id: str) -> Dict[str, Any]:
        """Delete all chunks for a specific video"""
        if not self.es:
            return {
                'success': False,
                'message': 'Elasticsearch not available'
            }
        
        try:
            logger.info(f"🗑️ Deleting chunks for video: {video_id}")
            
            # Delete by query
            delete_body = {
                "query": {
                    "term": {
                        "video_id": video_id
                    }
                }
            }
            
            response = self.es.delete_by_query(
                index=self.index_name,
                body=delete_body,
                refresh=True
            )
            
            deleted_count = response['deleted']
            logger.info(f"✅ Deleted {deleted_count} chunks for video: {video_id}")
            
            return {
                'success': True,
                'message': f'Deleted {deleted_count} chunks',
                'deleted_count': deleted_count
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to delete chunks: {str(e)}")
            return {
                'success': False,
                'message': f'Delete failed: {str(e)}'
            }
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get Elasticsearch index statistics"""
        if not self.es:
            return {
                'success': False,
                'message': 'Elasticsearch not available'
            }
        
        try:
            # Get index stats
            stats = self.es.indices.stats(index=self.index_name)
            
            # Get index info
            info = self.es.indices.get(index=self.index_name)
            
            # Get cluster health
            health = self.es.cluster.health(index=self.index_name)
            
            return {
                'success': True,
                'index_name': self.index_name,
                'document_count': stats['indices'][self.index_name]['total']['docs']['count'],
                'index_size': stats['indices'][self.index_name]['total']['store']['size_in_bytes'],
                'health': health['status'],
                'shards': health['active_shards'],
                'created': info[self.index_name]['settings']['index']['creation_date']
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get stats: {str(e)}")
            return {
                'success': False,
                'message': f'Failed to get stats: {str(e)}'
            }
    
    def health_check(self) -> Dict[str, Any]:
        """Check Elasticsearch and model health"""
        es_healthy = self.es and self.es.ping()
        model_healthy = self.model is not None
        
        logger.info(f"🔍 Health check - ES: {es_healthy}, Model: {model_healthy}")
        
        return {
            'elasticsearch': es_healthy,
            'sentence_transformer': model_healthy,
            'overall': es_healthy and model_healthy
        }

# Global instance
logger.info("🚀 Initializing Elasticsearch service...")
elasticsearch_service = ElasticsearchService()
logger.info("✅ Elasticsearch service initialized")
