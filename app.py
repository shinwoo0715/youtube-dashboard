import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import numpy as np
from datetime import datetime, timedelta
import re
import io
import base64
from collections import Counter
import urllib.parse

from youtube_analyzer import YouTubeAnalyzer
from url_parser import YouTubeURLParser
from data_visualizer import DataVisualizer

# Page configuration
st.set_page_config(
    page_title="📊 YouTube Channel Complete Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for mobile optimization
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #FF0000, #FF4444);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #FF0000;
        margin: 0.5rem 0;
    }
    
    .progress-container {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .error-message {
        background: #ffebee;
        color: #c62828;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #c62828;
        margin: 1rem 0;
    }
    
    .success-message {
        background: #e8f5e8;
        color: #2e7d32;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2e7d32;
        margin: 1rem 0;
    }
    
    @media (max-width: 768px) {
        .stSelectbox, .stTextInput, .stTextArea {
            margin-bottom: 1rem;
        }
        
        .metric-card {
            font-size: 0.9rem;
        }
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = None
    if 'channel_data' not in st.session_state:
        st.session_state.channel_data = None
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'progress_messages' not in st.session_state:
        st.session_state.progress_messages = []
    if 'error_message' not in st.session_state:
        st.session_state.error_message = None

def show_progress(message):
    """Add progress message to session state"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.progress_messages.append(f"[{timestamp}] {message}")

def display_progress():
    """Display progress messages"""
    if st.session_state.progress_messages:
        st.markdown('<div class="progress-container">', unsafe_allow_html=True)
        st.subheader("📈 Analysis Progress")
        for message in st.session_state.progress_messages[-10:]:  # Show last 10 messages
            st.text(message)
        st.markdown('</div>', unsafe_allow_html=True)

def display_error(error_msg):
    """Display error message with styling"""
    st.markdown(f'<div class="error-message">❌ <strong>Error:</strong> {error_msg}</div>', unsafe_allow_html=True)

def display_success(success_msg):
    """Display success message with styling"""
    st.markdown(f'<div class="success-message">✅ <strong>Success:</strong> {success_msg}</div>', unsafe_allow_html=True)

def main():
    initialize_session_state()
    
    # Main header
    st.markdown('<div class="main-header"><h1>📊 YouTube Channel Complete Analysis</h1><p>Comprehensive data analysis for any YouTube channel</p></div>', unsafe_allow_html=True)
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # API Key input
        st.subheader("YouTube Data API Key")
        api_key = st.text_input(
            "Enter your YouTube Data API Key",
            type="password",
            help="Get your API key from Google Cloud Console - YouTube Data API v3"
        )
        
        if not api_key:
            st.warning("⚠️ Please enter your YouTube Data API key to proceed")
            st.markdown("""
            **How to get API Key:**
            1. Go to [Google Cloud Console](https://console.cloud.google.com/)
            2. Create a new project or select existing
            3. Enable YouTube Data API v3
            4. Create credentials (API Key)
            5. Copy and paste the key above
            """)
        
        # Channel input
        st.subheader("📺 Channel Information")
        channel_input = st.text_input(
            "Channel Name or URL",
            placeholder="e.g., 칙칙풉풉 or https://www.youtube.com/@칙칙풉풉",
            help="Enter channel name, @handle, or any YouTube channel URL format"
        )
        
        # Analysis options
        st.subheader("⚙️ Analysis Options")
        max_videos = st.selectbox(
            "Maximum videos to analyze",
            [50, 100, 200, 500, 1000],
            index=2,
            help="More videos = more detailed analysis but longer processing time"
        )
        
        include_shorts = st.checkbox("Include YouTube Shorts", value=True)
        include_long_form = st.checkbox("Include Long-form videos", value=True)
        
        # Analysis button
        analyze_button = st.button(
            "🚀 Start Analysis",
            type="primary",
            disabled=not (api_key and channel_input),
            use_container_width=True
        )
    
    # Main content area
    if analyze_button and api_key and channel_input:
        st.session_state.progress_messages = []
        st.session_state.error_message = None
        st.session_state.analysis_complete = False
        
        # Initialize analyzer
        show_progress("Initializing YouTube analyzer...")
        st.session_state.analyzer = YouTubeAnalyzer(api_key)
        
        # Parse channel input
        show_progress("Parsing channel information...")
        parser = YouTubeURLParser()
        
        try:
            channel_info = parser.parse_channel_input(channel_input)
            show_progress(f"Channel parsed: {channel_info}")
            
            # Get channel data
            show_progress("Fetching channel details...")
            channel_data = st.session_state.analyzer.get_channel_info(channel_info)
            
            if not channel_data:
                display_error("Channel not found. Please check the channel name or URL.")
                return
            
            show_progress(f"Found channel: {channel_data.get('title', 'Unknown')}")
            
            # Create progress container
            progress_container = st.container()
            with progress_container:
                display_progress()
            
            # Collect video data
            show_progress("Collecting video data... This may take a while.")
            
            # Create a progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def progress_callback(current, total, message):
                progress = min(current / total, 1.0) if total > 0 else 0
                progress_bar.progress(progress)
                status_text.text(f"{message} ({current}/{total})")
                show_progress(f"{message} ({current}/{total})")
            
            videos_data = st.session_state.analyzer.collect_all_videos(
                channel_data['id'],
                max_results=max_videos,
                include_shorts=include_shorts,
                include_long_form=include_long_form,
                progress_callback=progress_callback
            )
            
            if not videos_data:
                display_error("No videos found for this channel.")
                return
            
            progress_bar.progress(1.0)
            status_text.text(f"Analysis complete! Found {len(videos_data)} videos.")
            
            # Store data in session state
            st.session_state.channel_data = {
                'channel_info': channel_data,
                'videos': videos_data
            }
            st.session_state.analysis_complete = True
            
            display_success(f"Successfully analyzed {len(videos_data)} videos from {channel_data.get('title', 'Unknown')} channel!")
            
        except Exception as e:
            display_error(f"Analysis failed: {str(e)}")
            st.error(f"Detailed error: {str(e)}")
            return
    
    # Display results if analysis is complete
    if st.session_state.analysis_complete and st.session_state.channel_data:
        display_analysis_results()

def display_analysis_results():
    """Display comprehensive analysis results"""
    channel_info = st.session_state.channel_data['channel_info']
    videos_data = st.session_state.channel_data['videos']
    
    # Create visualizer
    visualizer = DataVisualizer(videos_data)
    
    st.header(f"📊 Analysis Results for: {channel_info.get('title', 'Unknown Channel')}")
    
    # Channel overview
    col1, col2, col3, col4 = st.columns(4)
    
    total_videos = len(videos_data)
    total_views = sum(video.get('view_count', 0) for video in videos_data)
    total_likes = sum(video.get('like_count', 0) for video in videos_data)
    avg_views = total_views / total_videos if total_videos > 0 else 0
    
    shorts_count = sum(1 for video in videos_data if video.get('is_short', False))
    long_form_count = total_videos - shorts_count
    
    with col1:
        st.metric("Total Videos", f"{total_videos:,}")
        st.metric("Shorts", f"{shorts_count:,}")
    
    with col2:
        st.metric("Total Views", f"{total_views:,}")
        st.metric("Average Views", f"{avg_views:,.0f}")
    
    with col3:
        st.metric("Total Likes", f"{total_likes:,}")
        st.metric("Long-form", f"{long_form_count:,}")
    
    with col4:
        subscriber_count = channel_info.get('subscriber_count', 0)
        video_count = channel_info.get('video_count', 0)
        st.metric("Subscribers", f"{subscriber_count:,}")
        st.metric("Channel Videos", f"{video_count:,}")
    
    # Create analysis tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 Performance Overview",
        "📅 Upload Patterns", 
        "🔥 Top Videos",
        "🔤 Keywords Analysis",
        "📊 Detailed Data",
        "📋 Export & Reports"
    ])
    
    with tab1:
        display_performance_overview(visualizer)
    
    with tab2:
        display_upload_patterns(visualizer)
    
    with tab3:
        display_top_videos(visualizer)
    
    with tab4:
        display_keywords_analysis(visualizer)
    
    with tab5:
        display_detailed_data()
    
    with tab6:
        display_export_options(visualizer)

def display_performance_overview(visualizer):
    """Display performance overview charts"""
    st.subheader("📈 Performance Overview")
    
    # Views distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Views Distribution")
        fig = visualizer.create_views_distribution()
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Engagement Rate")
        fig = visualizer.create_engagement_chart()
        st.plotly_chart(fig, use_container_width=True)
    
    # Performance comparison: Shorts vs Long-form
    st.subheader("📊 Shorts vs Long-form Performance")
    fig = visualizer.create_shorts_vs_longform_comparison()
    st.plotly_chart(fig, use_container_width=True)
    
    # Duration vs Views correlation
    st.subheader("⏱️ Duration vs Views Correlation")
    fig = visualizer.create_duration_views_correlation()
    st.plotly_chart(fig, use_container_width=True)

def display_upload_patterns(visualizer):
    """Display upload pattern analysis"""
    st.subheader("📅 Upload Patterns Analysis")
    
    # Monthly upload trends
    st.subheader("📊 Monthly Upload Trends")
    fig = visualizer.create_monthly_trends()
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📅 Upload by Day of Week")
        fig = visualizer.create_weekday_analysis()
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🕐 Upload by Hour")
        fig = visualizer.create_hourly_analysis()
        st.plotly_chart(fig, use_container_width=True)
    
    # Upload consistency analysis
    st.subheader("📈 Upload Consistency")
    consistency_data = visualizer.analyze_upload_consistency()
    st.json(consistency_data)

def display_top_videos(visualizer):
    """Display top performing videos"""
    st.subheader("🔥 Top Performing Videos")
    
    # Top videos by different metrics
    metric_type = st.selectbox(
        "Select metric for top videos",
        ["views", "likes", "comments", "engagement_rate"],
        format_func=lambda x: {
            "views": "👁️ Views",
            "likes": "👍 Likes", 
            "comments": "💬 Comments",
            "engagement_rate": "📊 Engagement Rate"
        }[x]
    )
    
    top_videos = visualizer.get_top_videos(metric=metric_type, count=20)
    
    # Display top videos table
    if top_videos:
        df = pd.DataFrame(top_videos)
        
        # Format the dataframe for display
        display_df = df[['title', 'published_at', 'view_count', 'like_count', 'comment_count', 'duration_formatted', 'is_short']].copy()
        display_df.columns = ['Title', 'Published', 'Views', 'Likes', 'Comments', 'Duration', 'Type']
        display_df['Type'] = display_df['Type'].map({True: 'Shorts', False: 'Long-form'})
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Top video performance chart
        st.subheader(f"📊 Top 10 Videos by {metric_type.title()}")
        fig = visualizer.create_top_videos_chart(metric=metric_type, count=10)
        st.plotly_chart(fig, use_container_width=True)

def display_keywords_analysis(visualizer):
    """Display keyword and content analysis"""
    st.subheader("🔤 Keywords & Content Analysis")
    
    # Keyword analysis options
    analysis_source = st.selectbox(
        "Analyze keywords from:",
        ["titles", "descriptions", "tags"],
        format_func=lambda x: {
            "titles": "📝 Video Titles",
            "descriptions": "📄 Descriptions",
            "tags": "🏷️ Tags"
        }[x]
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(f"☁️ Word Cloud - {analysis_source.title()}")
        wordcloud_fig = visualizer.create_wordcloud(source=analysis_source)
        if wordcloud_fig:
            st.pyplot(wordcloud_fig, use_container_width=True)
        else:
            st.info(f"No {analysis_source} data available for word cloud generation.")
    
    with col2:
        st.subheader(f"📊 Top Keywords - {analysis_source.title()}")
        keywords_fig = visualizer.create_keywords_chart(source=analysis_source, top_n=20)
        if keywords_fig:
            st.plotly_chart(keywords_fig, use_container_width=True)
        else:
            st.info(f"No {analysis_source} data available for keyword analysis.")
    
    # Successful video patterns
    st.subheader("🎯 Successful Video Patterns")
    patterns = visualizer.analyze_successful_patterns()
    
    if patterns:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔥 High-performing Keywords")
            if patterns.get('top_keywords'):
                for keyword, data in patterns['top_keywords'].items():
                    st.write(f"**{keyword}**: {data['count']} videos, avg {data['avg_views']:,.0f} views")
        
        with col2:
            st.subheader("📈 Best Upload Times")
            if patterns.get('best_times'):
                for time_info in patterns['best_times']:
                    st.write(f"**{time_info['period']}**: Avg {time_info['avg_views']:,.0f} views ({time_info['count']} videos)")

def display_detailed_data():
    """Display detailed video data with filtering and sorting"""
    st.subheader("📊 Detailed Video Data")
    
    videos_data = st.session_state.channel_data['videos']
    df = pd.DataFrame(videos_data)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        video_type_filter = st.selectbox(
            "Video Type",
            ["All", "Shorts", "Long-form"],
            key="type_filter"
        )
    
    with col2:
        min_views = st.number_input(
            "Minimum Views",
            min_value=0,
            value=0,
            key="min_views_filter"
        )
    
    with col3:
        date_range = st.date_input(
            "Date Range",
            value=[],
            key="date_filter"
        )
    
    # Apply filters
    filtered_df = df.copy()
    
    if video_type_filter != "All":
        is_short = video_type_filter == "Shorts"
        filtered_df = filtered_df[filtered_df['is_short'] == is_short]
    
    if min_views > 0:
        filtered_df = filtered_df[filtered_df['view_count'] >= min_views]
    
    # Search functionality
    search_term = st.text_input("🔍 Search in titles", key="search_filter")
    if search_term:
        filtered_df = filtered_df[filtered_df['title'].str.contains(search_term, case=False, na=False)]
    
    # Display filtered data
    st.write(f"Showing {len(filtered_df)} of {len(df)} videos")
    
    # Select columns to display
    available_columns = ['title', 'published_at', 'view_count', 'like_count', 'comment_count', 
                        'duration_formatted', 'is_short', 'tags']
    selected_columns = st.multiselect(
        "Select columns to display",
        available_columns,
        default=['title', 'published_at', 'view_count', 'like_count', 'comment_count', 'duration_formatted'],
        key="column_selector"
    )
    
    if selected_columns:
        display_df = filtered_df[selected_columns].copy()
        
        # Format column names
        column_mapping = {
            'title': 'Title',
            'published_at': 'Published',
            'view_count': 'Views',
            'like_count': 'Likes',
            'comment_count': 'Comments',
            'duration_formatted': 'Duration',
            'is_short': 'Type',
            'tags': 'Tags'
        }
        
        display_df = display_df.rename(columns=column_mapping)
        
        if 'Type' in display_df.columns:
            display_df['Type'] = display_df['Type'].map({True: 'Shorts', False: 'Long-form'})
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

def display_export_options(visualizer):
    """Display export and reporting options"""
    st.subheader("📋 Export & Reports")
    
    videos_data = st.session_state.channel_data['videos']
    channel_info = st.session_state.channel_data['channel_info']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Data Export")
        
        # CSV export
        if st.button("📄 Export to CSV", use_container_width=True):
            df = pd.DataFrame(videos_data)
            csv = df.to_csv(index=False)
            st.download_button(
                label="💾 Download CSV",
                data=csv,
                file_name=f"{channel_info.get('title', 'channel')}_analysis.csv",
                mime='text/csv',
                use_container_width=True
            )
        
        # JSON export
        if st.button("📋 Export to JSON", use_container_width=True):
            import json
            json_data = json.dumps(st.session_state.channel_data, indent=2, default=str)
            st.download_button(
                label="💾 Download JSON",
                data=json_data,
                file_name=f"{channel_info.get('title', 'channel')}_analysis.json",
                mime='application/json',
                use_container_width=True
            )
    
    with col2:
        st.subheader("📈 Analysis Summary")
        
        # Generate summary report
        summary = visualizer.generate_summary_report(channel_info)
        
        st.markdown("### 📋 Channel Analysis Summary")
        for key, value in summary.items():
            if isinstance(value, dict):
                st.markdown(f"**{key}:**")
                for sub_key, sub_value in value.items():
                    st.markdown(f"  - {sub_key}: {sub_value}")
            else:
                st.markdown(f"**{key}:** {value}")
        
        # Export summary as text
        summary_text = "\n".join([f"{k}: {v}" for k, v in summary.items()])
        st.download_button(
            label="📄 Download Summary Report",
            data=summary_text,
            file_name=f"{channel_info.get('title', 'channel')}_summary.txt",
            mime='text/plain',
            use_container_width=True
        )

if __name__ == "__main__":
    main()
