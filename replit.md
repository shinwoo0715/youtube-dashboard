# YouTube Channel Analysis Tool

## Overview

This is a comprehensive YouTube channel analysis web application built with Streamlit. The application allows users to input YouTube channel names or URLs in various formats and performs complete data analysis of both long-form and short-form videos. It provides real-time progress tracking, error handling, and mobile-optimized responsive UI for displaying analytical results.

The system is designed to work entirely with Python-based data analysis libraries (pandas, matplotlib, plotly) without relying on external AI services like OpenAI or ChatGPT.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application
- **UI Components**: Custom CSS for mobile optimization and responsive design
- **Visualization**: Plotly for interactive charts, Matplotlib/Seaborn for static visualizations
- **Styling**: Custom CSS with YouTube-themed color scheme (#FF0000 primary)

### Backend Architecture
- **Core Components**: 
  - `YouTubeAnalyzer`: Handles YouTube Data API interactions
  - `YouTubeURLParser`: Parses various YouTube URL formats and channel identifiers
  - `DataVisualizer`: Creates comprehensive data visualizations
- **API Integration**: YouTube Data API v3 for channel and video data retrieval
- **Data Processing**: Pandas for data manipulation and analysis

## Key Components

### 1. YouTube URL Parser (`url_parser.py`)
- **Purpose**: Parse various YouTube channel input formats
- **Capabilities**:
  - Channel IDs (UC format)
  - Channel handles (@username)
  - User URLs (/user/)
  - Custom URLs (/c/)
  - Korean/Unicode URL decoding
  - Handles URL parameters like /shorts, /videos, /featured

### 2. YouTube Analyzer (`youtube_analyzer.py`)
- **Purpose**: Interface with YouTube Data API
- **Features**:
  - Channel information retrieval
  - Video data collection for both long-form and shorts
  - API error handling and rate limiting
  - Multiple channel identification methods

### 3. Data Visualizer (`data_visualizer.py`)
- **Purpose**: Create comprehensive visualizations
- **Chart Types**:
  - Views distribution histograms
  - Engagement rate analysis
  - Performance metrics visualization
  - Word clouds for title analysis

### 4. Main Application (`app.py`)
- **Purpose**: Streamlit web interface
- **Features**:
  - Mobile-optimized responsive design
  - Real-time progress tracking
  - API key input with security (password mode)
  - Error handling and user feedback

## Data Flow

1. **User Input**: Channel name or URL entered through Streamlit interface
2. **URL Parsing**: `YouTubeURLParser` processes input to extract channel identifier
3. **API Authentication**: User-provided YouTube Data API key validation
4. **Data Collection**: `YouTubeAnalyzer` fetches channel and video data
5. **Data Processing**: Pandas-based data cleaning and analysis
6. **Visualization**: `DataVisualizer` creates interactive charts and graphs
7. **Display**: Results presented through responsive Streamlit interface

## External Dependencies

### APIs
- **YouTube Data API v3**: Required for channel and video data retrieval
- **Authentication**: User-provided API key (not hardcoded for security)

### Python Libraries
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualizations
- **Matplotlib/Seaborn**: Static plotting
- **WordCloud**: Text visualization
- **Google API Client**: YouTube API integration
- **isodate**: ISO 8601 duration parsing

## Deployment Strategy

### Platform Compatibility
- **Primary**: Replit deployment
- **Mobile Optimization**: Responsive CSS for mobile devices
- **Desktop Support**: Full desktop browser compatibility

### Configuration Requirements
- Python 3.x environment
- YouTube Data API v3 access
- Required Python packages installation
- No database requirements (in-memory processing)

### Security Considerations
- API keys entered by users (not stored in code)
- Password-mode input for API key security
- No persistent storage of sensitive data

## Changelog

```
Changelog:
- July 02, 2025. Initial setup
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
```