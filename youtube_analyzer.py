import os
import time
from datetime import datetime, timedelta
import re
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import isodate
import urllib.parse

class YouTubeAnalyzer:
    def __init__(self, api_key):
        """Initialize YouTube Data API client"""
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        
    def get_channel_info(self, channel_identifier):
        """
        Get channel information from channel ID, username, or custom URL
        """
        try:
            # Try different methods to get channel info
            channel_data = None
            
            # Method 1: Direct channel ID
            if channel_identifier.startswith('UC') and len(channel_identifier) == 24:
                request = self.youtube.channels().list(
                    part='snippet,statistics,contentDetails',
                    id=channel_identifier
                )
                response = request.execute()
                if response['items']:
                    channel_data = response['items'][0]
            
            # Method 2: Channel handle (@username)
            elif channel_identifier.startswith('@'):
                request = self.youtube.channels().list(
                    part='snippet,statistics,contentDetails',
                    forHandle=channel_identifier
                )
                response = request.execute()
                if response['items']:
                    channel_data = response['items'][0]
            
            # Method 3: Search by channel name
            else:
                # First try to search for the channel
                search_request = self.youtube.search().list(
                    part='snippet',
                    q=channel_identifier,
                    type='channel',
                    maxResults=5
                )
                search_response = search_request.execute()
                
                if search_response['items']:
                    # Get the first matching channel
                    channel_id = search_response['items'][0]['snippet']['channelId']
                    request = self.youtube.channels().list(
                        part='snippet,statistics,contentDetails',
                        id=channel_id
                    )
                    response = request.execute()
                    if response['items']:
                        channel_data = response['items'][0]
            
            if not channel_data:
                return None
            
            # Extract relevant information
            snippet = channel_data['snippet']
            statistics = channel_data['statistics']
            content_details = channel_data['contentDetails']
            
            return {
                'id': channel_data['id'],
                'title': snippet.get('title', ''),
                'description': snippet.get('description', ''),
                'published_at': snippet.get('publishedAt', ''),
                'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                'subscriber_count': int(statistics.get('subscriberCount', 0)),
                'video_count': int(statistics.get('videoCount', 0)),
                'view_count': int(statistics.get('viewCount', 0)),
                'uploads_playlist_id': content_details['relatedPlaylists']['uploads']
            }
            
        except HttpError as e:
            if e.resp.status == 403:
                raise Exception("API key is invalid or quota exceeded. Please check your API key and quota limits.")
            elif e.resp.status == 404:
                raise Exception("Channel not found. Please check the channel name or URL.")
            else:
                raise Exception(f"YouTube API error: {e}")
        except Exception as e:
            raise Exception(f"Error getting channel info: {str(e)}")
    
    def collect_all_videos(self, channel_id, max_results=1000, include_shorts=True, include_long_form=True, progress_callback=None):
        """
        Collect all videos from a channel with detailed information
        """
        try:
            # Get channel info first
            channel_request = self.youtube.channels().list(
                part='contentDetails',
                id=channel_id
            )
            channel_response = channel_request.execute()
            
            if not channel_response['items']:
                raise Exception("Channel not found")
            
            uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            videos = []
            next_page_token = None
            collected_count = 0
            
            while collected_count < max_results:
                # Get playlist items (videos)
                playlist_request = self.youtube.playlistItems().list(
                    part='snippet',
                    playlistId=uploads_playlist_id,
                    maxResults=min(50, max_results - collected_count),
                    pageToken=next_page_token
                )
                playlist_response = playlist_request.execute()
                
                if not playlist_response['items']:
                    break
                
                # Get video IDs
                video_ids = [item['snippet']['resourceId']['videoId'] for item in playlist_response['items']]
                
                # Get detailed video information
                videos_request = self.youtube.videos().list(
                    part='snippet,statistics,contentDetails,status',
                    id=','.join(video_ids)
                )
                videos_response = videos_request.execute()
                
                for video in videos_response['items']:
                    try:
                        video_data = self._extract_video_data(video)
                        
                        # Filter by video type
                        if video_data['is_short'] and not include_shorts:
                            continue
                        if not video_data['is_short'] and not include_long_form:
                            continue
                        
                        videos.append(video_data)
                        collected_count += 1
                        
                        if progress_callback:
                            progress_callback(collected_count, max_results, f"Collecting video data...")
                        
                        if collected_count >= max_results:
                            break
                            
                    except Exception as e:
                        print(f"Error processing video {video.get('id', 'unknown')}: {str(e)}")
                        continue
                
                next_page_token = playlist_response.get('nextPageToken')
                if not next_page_token:
                    break
                
                # Rate limiting
                time.sleep(0.1)
            
            # Enrich videos with additional analysis
            if progress_callback:
                progress_callback(len(videos), len(videos), "Analyzing video data...")
            
            self._enrich_video_data(videos)
            
            return videos
            
        except HttpError as e:
            if e.resp.status == 403:
                raise Exception("API quota exceeded or invalid API key")
            else:
                raise Exception(f"YouTube API error: {e}")
        except Exception as e:
            raise Exception(f"Error collecting videos: {str(e)}")
    
    def _extract_video_data(self, video):
        """Extract and process individual video data"""
        snippet = video['snippet']
        statistics = video['statistics']
        content_details = video['contentDetails']
        
        # Parse duration
        duration_iso = content_details.get('duration', 'PT0S')
        duration_seconds = self._parse_duration(duration_iso)
        
        # Determine if it's a short (≤60 seconds or has #shorts in title/description)
        is_short = (
            duration_seconds <= 60 or 
            '#shorts' in snippet.get('title', '').lower() or
            '#shorts' in snippet.get('description', '').lower()
        )
        
        # Parse published date
        published_at = datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00'))
        
        # Extract tags
        tags = snippet.get('tags', [])
        
        # Extract view count, like count, comment count
        view_count = int(statistics.get('viewCount', 0))
        like_count = int(statistics.get('likeCount', 0))
        comment_count = int(statistics.get('commentCount', 0))
        
        return {
            'video_id': video['id'],
            'title': snippet.get('title', ''),
            'description': snippet.get('description', ''),
            'published_at': published_at,
            'duration_seconds': duration_seconds,
            'duration_formatted': self._format_duration(duration_seconds),
            'view_count': view_count,
            'like_count': like_count,
            'comment_count': comment_count,
            'tags': tags,
            'is_short': is_short,
            'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
            'channel_title': snippet.get('channelTitle', ''),
            'url': f"https://www.youtube.com/watch?v={video['id']}"
        }
    
    def _parse_duration(self, duration_iso):
        """Parse ISO 8601 duration to seconds"""
        try:
            duration = isodate.parse_duration(duration_iso)
            return int(duration.total_seconds())
        except:
            return 0
    
    def _format_duration(self, seconds):
        """Format duration in seconds to readable format"""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            remaining_seconds = seconds % 60
            return f"{minutes}m {remaining_seconds}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            remaining_seconds = seconds % 60
            return f"{hours}h {minutes}m {remaining_seconds}s"
    
    def _enrich_video_data(self, videos):
        """Add calculated fields and analysis to video data"""
        for video in videos:
            # Calculate engagement rate
            total_engagement = video['like_count'] + video['comment_count']
            video['engagement_rate'] = (total_engagement / video['view_count'] * 100) if video['view_count'] > 0 else 0
            
            # Add time-based features
            pub_date = video['published_at']
            video['day_of_week'] = pub_date.strftime('%A')
            video['hour_of_day'] = pub_date.hour
            video['month'] = pub_date.month
            video['year'] = pub_date.year
            video['date_str'] = pub_date.strftime('%Y-%m-%d')
            
            # Calculate views per day since upload
            days_since_upload = (datetime.now(pub_date.tzinfo) - pub_date).days + 1
            video['views_per_day'] = video['view_count'] / days_since_upload if days_since_upload > 0 else video['view_count']
            
            # Extract keywords from title
            video['title_words'] = self._extract_keywords(video['title'])
            video['description_words'] = self._extract_keywords(video['description'])
    
    def _extract_keywords(self, text):
        """Extract keywords from text"""
        if not text:
            return []
        
        # Remove special characters and convert to lowercase
        text = re.sub(r'[^\w\s가-힣]', ' ', text.lower())
        
        # Split into words and filter out short words
        words = [word.strip() for word in text.split() if len(word.strip()) > 2]
        
        # Remove common stop words (Korean and English)
        stop_words = {
            '그리고', '하지만', '그래서', '그런데', '그러나', '또한', '그냥', '정말', '진짜', '너무',
            'and', 'but', 'the', 'for', 'are', 'with', 'this', 'that', 'from', 'they', 'have',
            'been', 'will', 'what', 'when', 'where', 'how', 'why', 'can', 'could', 'would',
            'should', 'may', 'might', 'must', 'shall', 'need', 'want', 'like', 'know', 'think'
        }
        
        return [word for word in words if word not in stop_words]
