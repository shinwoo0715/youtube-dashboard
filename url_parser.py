import re
import urllib.parse

class YouTubeURLParser:
    """Parser for various YouTube channel URL formats and channel names"""
    
    def __init__(self):
        # Regex patterns for different YouTube URL formats
        self.patterns = {
            'channel_id': r'youtube\.com/channel/([a-zA-Z0-9_-]+)',
            'channel_handle': r'youtube\.com/@([^/?&\s]+)',
            'user': r'youtube\.com/user/([^/?&\s]+)',
            'custom_url': r'youtube\.com/c/([^/?&\s]+)',
        }
    
    def parse_channel_input(self, input_str):
        """
        Parse various forms of YouTube channel input
        Returns the most appropriate identifier for API calls
        """
        if not input_str:
            raise ValueError("Input cannot be empty")
        
        input_str = input_str.strip()
        
        # If it's just a channel name or handle without URL
        if not input_str.startswith('http'):
            # If it starts with @, it's a handle
            if input_str.startswith('@'):
                return input_str
            else:
                # Treat as channel name for search
                return input_str
        
        # URL parsing
        try:
            # Decode URL-encoded characters (like Korean text)
            decoded_url = urllib.parse.unquote(input_str)
            
            # Extract the main part after domain
            parsed_url = urllib.parse.urlparse(input_str)
            
            # Handle channel ID format
            if '/channel/' in input_str:
                match = re.search(self.patterns['channel_id'], input_str)
                if match:
                    return match.group(1)  # Return channel ID directly
            
            # Handle @username format
            elif '/@' in input_str:
                match = re.search(self.patterns['channel_handle'], decoded_url)
                if match:
                    username = match.group(1)
                    # Remove any trailing path elements
                    username = username.split('/')[0]
                    return f"@{username}"
            
            # Handle user format
            elif '/user/' in input_str:
                match = re.search(self.patterns['user'], input_str)
                if match:
                    return match.group(1)  # Return username for search
            
            # Handle custom URL format
            elif '/c/' in input_str:
                match = re.search(self.patterns['custom_url'], input_str)
                if match:
                    return match.group(1)  # Return custom name for search
            
            # If no pattern matches, try to extract from the path
            path_parts = parsed_url.path.strip('/').split('/')
            if path_parts and path_parts[0]:
                # If first part looks like a channel identifier
                first_part = path_parts[0]
                
                # Check if it's a handle (starts with @)
                if first_part.startswith('@'):
                    return first_part
                
                # Check if it's a channel ID
                if first_part.startswith('UC') and len(first_part) == 24:
                    return first_part
                
                # Otherwise, treat as channel name
                return first_part
            
            raise ValueError("Could not parse channel information from URL")
            
        except Exception as e:
            raise ValueError(f"Error parsing URL: {str(e)}")
    
    def validate_channel_id(self, channel_id):
        """Validate if a string is a valid YouTube channel ID"""
        if not channel_id:
            return False
        
        # YouTube channel IDs are 24 characters long and start with UC
        return (
            len(channel_id) == 24 and 
            channel_id.startswith('UC') and 
            channel_id.replace('UC', '').replace('-', '').replace('_', '').isalnum()
        )
    
    def validate_handle(self, handle):
        """Validate if a string is a valid YouTube handle"""
        if not handle:
            return False
        
        # Handles start with @ and contain valid characters
        if not handle.startswith('@'):
            return False
        
        username = handle[1:]  # Remove @
        
        # Username should be 3-30 characters, alphanumeric, underscore, hyphen, period
        return (
            3 <= len(username) <= 30 and
            re.match(r'^[a-zA-Z0-9._-]+$', username)
        )
    
    def clean_channel_name(self, name):
        """Clean channel name for search"""
        if not name:
            return ""
        
        # Remove extra whitespace
        name = name.strip()
        
        # Remove common URL artifacts
        name = name.replace('%20', ' ')
        
        # Decode URL encoding
        name = urllib.parse.unquote(name)
        
        return name
    
    def extract_channel_info_from_url(self, url):
        """
        Extract detailed information from YouTube URL
        Returns dict with parsed components
        """
        if not url:
            return {}
        
        try:
            parsed = urllib.parse.urlparse(url)
            decoded_url = urllib.parse.unquote(url)
            
            result = {
                'original_url': url,
                'decoded_url': decoded_url,
                'domain': parsed.netloc,
                'path': parsed.path,
                'query': dict(urllib.parse.parse_qsl(parsed.query)),
                'fragment': parsed.fragment
            }
            
            # Extract channel identifier
            channel_identifier = self.parse_channel_input(url)
            result['channel_identifier'] = channel_identifier
            
            # Determine the type of identifier
            if self.validate_channel_id(channel_identifier):
                result['identifier_type'] = 'channel_id'
            elif self.validate_handle(channel_identifier):
                result['identifier_type'] = 'handle'
            else:
                result['identifier_type'] = 'name_or_username'
            
            return result
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_clean_channel_url(self, channel_info):
        """
        Generate a clean YouTube channel URL from channel info
        """
        if not channel_info:
            return None
        
        channel_id = channel_info.get('id')
        if channel_id:
            return f"https://www.youtube.com/channel/{channel_id}"
        
        return None
    
    def is_youtube_url(self, url):
        """Check if URL is a valid YouTube URL"""
        if not url:
            return False
        
        youtube_domains = ['youtube.com', 'www.youtube.com', 'm.youtube.com']
        
        try:
            parsed = urllib.parse.urlparse(url)
            return parsed.netloc.lower() in youtube_domains
        except:
            return False
    
    def normalize_input(self, input_str):
        """
        Normalize various input formats to a standard form
        """
        if not input_str:
            return ""
        
        input_str = input_str.strip()
        
        # If it's a URL, parse it
        if self.is_youtube_url(input_str):
            return self.parse_channel_input(input_str)
        
        # If it's just text, clean it
        return self.clean_channel_name(input_str)
