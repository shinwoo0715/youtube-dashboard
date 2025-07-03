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
    page_title="📊 유튜브 채널 완전 분석",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Revolutionary UI/UX Design System
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
    
    :root {
        --primary: #FF0000;
        --primary-light: #FF6B6B;
        --primary-dark: #CC0000;
        --secondary: #4ECDC4;
        --accent: #FFD93D;
        --bg-primary: #FFFFFF;
        --bg-secondary: #F8FAFC;
        --bg-tertiary: #F1F5F9;
        --text-primary: #1E293B;
        --text-secondary: #64748B;
        --border: #E2E8F0;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        --shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    }
    
    /* Global Styles */
    .main {
        font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Glassmorphism Header */
    .main-header {
        text-align: center;
        padding: 4rem 3rem;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 30px;
        margin: 2rem 0 3rem 0;
        position: relative;
        overflow: hidden;
        box-shadow: var(--shadow-2xl);
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    .main-header h1 {
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #FF0000, #FF6B6B, #FFD93D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: none;
        letter-spacing: -0.02em;
    }
    
    .main-header p {
        font-size: 1.25rem;
        color: rgba(255, 255, 255, 0.9);
        font-weight: 400;
        letter-spacing: 0.01em;
    }
    
    /* Sidebar Design */
    .sidebar .stSelectbox, .sidebar .stTextInput, .sidebar .stTextArea, .sidebar .stNumberInput {
        margin-bottom: 1rem;
    }
    
    .sidebar .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 12px;
        backdrop-filter: blur(10px);
    }
    
    .sidebar .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 12px;
        backdrop-filter: blur(10px);
        padding: 12px 16px;
        font-weight: 500;
    }
    
    .sidebar .stButton > button {
        width: 100%;
        height: 3.5rem;
        border-radius: 16px;
        font-weight: 700;
        font-size: 1.1rem;
        background: linear-gradient(135deg, #FF0000 0%, #FF6B6B 100%);
        border: none;
        color: white;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: var(--shadow-lg);
        position: relative;
        overflow: hidden;
    }
    
    .sidebar .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    .sidebar .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow-xl);
    }
    
    .sidebar .stButton > button:hover::before {
        left: 100%;
    }
    
    /* Enhanced Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: rgba(255, 255, 255, 0.1);
        padding: 8px;
        border-radius: 20px;
        backdrop-filter: blur(10px);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 3.5rem;
        padding: 12px 24px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(10px);
        color: rgba(255, 255, 255, 0.8);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #FF0000 0%, #FF6B6B 100%);
        color: white !important;
        box-shadow: var(--shadow-lg);
        border: 1px solid rgba(255, 255, 255, 0.3);
        transform: translateY(-2px);
    }
    
    /* Glassmorphism Cards */
    .metric-card, .element-container .stMetric {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(20px);
        padding: 2rem;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin: 1rem 0;
        box-shadow: var(--shadow-lg);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #FF0000, #FF6B6B, #FFD93D, #4ECDC4);
    }
    
    .metric-card:hover, .element-container .stMetric:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: var(--shadow-2xl);
        background: rgba(255, 255, 255, 0.2);
    }
    
    /* Data Tables */
    .stDataFrame {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        overflow: hidden;
        box-shadow: var(--shadow-lg);
        backdrop-filter: blur(20px);
    }
    
    .stDataFrame thead tr th {
        background: linear-gradient(135deg, #FF0000 0%, #FF6B6B 100%);
        color: white;
        font-weight: 700;
        padding: 16px;
        border: none;
    }
    
    .stDataFrame tbody tr:nth-child(even) {
        background: rgba(248, 250, 252, 0.5);
    }
    
    .stDataFrame tbody tr:hover {
        background: rgba(255, 107, 107, 0.1);
        transform: scale(1.01);
        transition: all 0.2s ease;
    }
    
    /* Progress and Status */
    .progress-container {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(20px);
        padding: 2rem;
        border-radius: 20px;
        margin: 2rem 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: var(--shadow-lg);
    }
    
    .error-message {
        background: rgba(255, 235, 238, 0.9);
        backdrop-filter: blur(10px);
        color: #c62828;
        padding: 2rem;
        border-radius: 20px;
        border-left: 5px solid #FF4444;
        margin: 2rem 0;
        box-shadow: var(--shadow-lg);
        animation: slideInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .success-message {
        background: rgba(232, 245, 232, 0.9);
        backdrop-filter: blur(10px);
        color: #2e7d32;
        padding: 2rem;
        border-radius: 20px;
        border-left: 5px solid #4CAF50;
        margin: 2rem 0;
        box-shadow: var(--shadow-lg);
        animation: slideInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Enhanced Expanders */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 16px 20px;
        font-weight: 600;
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
    }
    
    .streamlit-expanderContent {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 0 0 16px 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    
    /* Floating Action Elements */
    .floating-widget {
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        background: linear-gradient(135deg, #FF0000 0%, #FF6B6B 100%);
        color: white;
        padding: 1rem;
        border-radius: 50%;
        box-shadow: var(--shadow-xl);
        cursor: pointer;
        transition: all 0.3s ease;
        z-index: 1000;
    }
    
    .floating-widget:hover {
        transform: scale(1.1) rotate(5deg);
        box-shadow: var(--shadow-2xl);
    }
    
    /* Plotly Chart Container */
    .plotly-graph-div {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 1rem;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin: 1rem 0;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #FF0000, #FF6B6B);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #CC0000, #FF4444);
    }
    
    /* Mobile Optimizations */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2.5rem;
        }
        
        .main-header {
            padding: 3rem 2rem;
            margin: 1rem 0 2rem 0;
        }
        
        .metric-card {
            padding: 1.5rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 10px 16px;
            font-size: 0.9rem;
        }
        
        .floating-widget {
            bottom: 1rem;
            right: 1rem;
        }
    }
    
    /* Loading Animations */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    @keyframes bounce {
        0%, 20%, 53%, 80%, 100% { transform: translateY(0); }
        40%, 43% { transform: translateY(-10px); }
        70% { transform: translateY(-5px); }
        90% { transform: translateY(-2px); }
    }
    
    .loading {
        animation: pulse 2s infinite;
    }
    
    .bounce {
        animation: bounce 1s infinite;
    }
    
    /* Dark Mode Support */
    @media (prefers-color-scheme: dark) {
        :root {
            --bg-primary: #0F172A;
            --bg-secondary: #1E293B;
            --bg-tertiary: #334155;
            --text-primary: #F8FAFC;
            --text-secondary: #CBD5E1;
            --border: #475569;
        }
        
        .main {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
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
        st.subheader("📈 분석 진행 상황")
        for message in st.session_state.progress_messages[-10:]:  # Show last 10 messages
            st.text(message)
        st.markdown('</div>', unsafe_allow_html=True)

def display_error(error_msg):
    """Display error message with styling"""
    st.markdown(f'<div class="error-message">❌ <strong>오류:</strong> {error_msg}</div>', unsafe_allow_html=True)

def display_success(success_msg):
    """Display success message with styling"""
    st.markdown(f'<div class="success-message">✅ <strong>성공:</strong> {success_msg}</div>', unsafe_allow_html=True)

def main():
    initialize_session_state()
    st.title("유튜브 데이터 대시보드")
    st.write("앱이 정상적으로 실행되었습니다.")

    # Main header with enhanced features
    st.markdown("""
    <div class="main-header">
        <h1>📊 유튜브 채널 완전 분석</h1>
        <p>AI 기반 데이터 분석 · 실시간 트렌드 예측 · 성과 최적화</p>
        <div style="margin-top: 2rem; display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;">
            <span style="background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 20px; font-size: 0.9rem;">✨ 실시간 분석</span>
            <span style="background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 20px; font-size: 0.9rem;">🎯 성공 패턴 AI</span>
            <span style="background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 20px; font-size: 0.9rem;">📈 트렌드 예측</span>
            <span style="background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 20px; font-size: 0.9rem;">🔮 수익 예상</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Add floating help button
    st.markdown("""
    <div class="floating-widget" title="도움말">
        <div style="font-size: 1.5rem;">❓</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("🔧 설정")
        
        # API Key input
        st.subheader("🔑 YouTube Data API 키")
        api_key = st.text_input(
            "YouTube Data API 키를 입력하세요",
            type="password",
            help="Google Cloud Console에서 YouTube Data API v3 키를 발급받으세요"
        )
        
        if not api_key:
            st.warning("⚠️ 진행하려면 YouTube Data API 키를 입력하세요")
            st.markdown("""
            **API 키 발급 방법:**
            1. [Google Cloud Console](https://console.cloud.google.com/) 접속
            2. 새 프로젝트 생성 또는 기존 프로젝트 선택
            3. YouTube Data API v3 활성화
            4. 사용자 인증 정보 생성 (API 키)
            5. 위에 키를 복사해서 붙여넣기
            """)
        
        # Channel input
        st.subheader("📺 채널 정보")
        channel_input = st.text_input(
            "채널명 또는 URL",
            placeholder="예: 칙칙풉풉 또는 https://www.youtube.com/@칙칙풉풉",
            help="채널명, @핸들, 또는 모든 형태의 유튜브 채널 URL을 입력하세요"
        )
        
        # Advanced Analysis options
        st.subheader("⚙️ 고급 분석 옵션")
        
        # Basic options
        with st.expander("📊 기본 설정", expanded=True):
            max_videos = st.selectbox(
                "분석할 최대 영상 수",
                [10, 20, 50, 100, 200, 500, 1000, 2000, 5000],
                index=4,
                help="더 많은 영상 = 더 정확한 분석 (처리 시간 증가)"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                include_shorts = st.checkbox("쇼츠 포함", value=True)
            with col2:
                include_long_form = st.checkbox("롱폼 포함", value=True)
        
        # Date range filter
        with st.expander("📅 날짜 필터"):
            use_date_filter = st.checkbox("날짜 범위 설정")
            if use_date_filter:
                date_from = st.date_input("시작 날짜", value=datetime.now() - timedelta(days=365))
                date_to = st.date_input("종료 날짜", value=datetime.now())
        
        # Performance filters
        with st.expander("🎯 성과 필터"):
            min_views = st.number_input("최소 조회수", min_value=0, value=0)
            min_likes = st.number_input("최소 좋아요 수", min_value=0, value=0)
            
        # Analysis depth
        with st.expander("🔍 분석 깊이"):
            analyze_thumbnails = st.checkbox("썸네일 색상 분석", value=True)
            analyze_sentiment = st.checkbox("제목 감정 분석", value=True)
            predict_trends = st.checkbox("트렌드 예측", value=True)
            competitor_analysis = st.checkbox("경쟁자 분석 (베타)", value=False)
        
        # Export options
        with st.expander("💾 내보내기 설정"):
            export_format = st.selectbox("내보내기 형식", ["Excel", "CSV", "JSON"])
            include_charts = st.checkbox("차트 이미지 포함", value=True)
        
        st.divider()
        
        # Analysis button
        analyze_button = st.button(
            "🚀 분석 시작",
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
        show_progress("유튜브 분석기 초기화 중...")
        st.session_state.analyzer = YouTubeAnalyzer(api_key)
        
        # Parse channel input
        show_progress("채널 정보 파싱 중...")
        parser = YouTubeURLParser()
        
        try:
            channel_info = parser.parse_channel_input(channel_input)
            show_progress(f"채널 파싱 완료: {channel_info}")
            
            # Get channel data
            show_progress("채널 세부 정보 가져오는 중...")
            channel_data = st.session_state.analyzer.get_channel_info(channel_info)
            
            if not channel_data:
                display_error("채널을 찾을 수 없습니다. 채널명이나 URL을 확인해주세요.")
                return
            
            show_progress(f"채널 발견: {channel_data.get('title', '알 수 없음')}")
            
            # Create progress container
            progress_container = st.container()
            with progress_container:
                display_progress()
            
            # Collect video data
            show_progress("영상 데이터 수집 중... 시간이 소요될 수 있습니다.")
            
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
                display_error("이 채널에서 영상을 찾을 수 없습니다.")
                return
            
            progress_bar.progress(1.0)
            status_text.text(f"분석 완료! {len(videos_data)}개 영상을 발견했습니다.")
            
            # Store data in session state
            st.session_state.channel_data = {
                'channel_info': channel_data,
                'videos': videos_data
            }
            st.session_state.analysis_complete = True
            
            display_success(f"{channel_data.get('title', '알 수 없는')} 채널의 {len(videos_data)}개 영상 분석을 성공적으로 완료했습니다!")
            
        except Exception as e:
            display_error(f"분석 실패: {str(e)}")
            st.error(f"상세 오류: {str(e)}")
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
    
    st.header(f"📊 {channel_info.get('title', '알 수 없는 채널')} 분석 결과")
    
    # Channel overview with enhanced metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_videos = len(videos_data)
    total_views = sum(video.get('view_count', 0) for video in videos_data)
    total_likes = sum(video.get('like_count', 0) for video in videos_data)
    total_comments = sum(video.get('comment_count', 0) for video in videos_data)
    avg_views = total_views / total_videos if total_videos > 0 else 0
    
    shorts_count = sum(1 for video in videos_data if video.get('is_short', False))
    long_form_count = total_videos - shorts_count
    
    # Calculate engagement metrics
    total_engagement = total_likes + total_comments
    avg_engagement_rate = (total_engagement / total_views * 100) if total_views > 0 else 0
    
    with col1:
        st.metric("총 영상 수", f"{total_videos:,}")
        st.metric("쇼츠", f"{shorts_count:,}")
    
    with col2:
        st.metric("총 조회수", f"{total_views:,}")
        st.metric("평균 조회수", f"{avg_views:,.0f}")
    
    with col3:
        st.metric("총 좋아요", f"{total_likes:,}")
        st.metric("롱폼", f"{long_form_count:,}")
    
    with col4:
        subscriber_count = channel_info.get('subscriber_count', 0)
        video_count = channel_info.get('video_count', 0)
        st.metric("구독자 수", f"{subscriber_count:,}")
        st.metric("채널 총 영상", f"{video_count:,}")
    
    # Additional metrics row
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        st.metric("총 댓글", f"{total_comments:,}")
    
    with col6:
        st.metric("평균 참여율", f"{avg_engagement_rate:.2f}%")
    
    with col7:
        # Calculate average upload frequency
        if total_videos > 1:
            date_range = (max(video['published_at'] for video in videos_data) - 
                         min(video['published_at'] for video in videos_data)).days
            upload_frequency = date_range / total_videos if date_range > 0 else 0
            st.metric("평균 업로드 간격", f"{upload_frequency:.1f}일")
        else:
            st.metric("평균 업로드 간격", "N/A")
    
    with col8:
        # Most successful video
        if videos_data:
            best_video = max(videos_data, key=lambda x: x.get('view_count', 0))
            st.metric("최고 조회수", f"{best_video.get('view_count', 0):,}")
    
    # Create enhanced analysis tabs with new features
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
        "📈 성과 개요",
        "📅 업로드 패턴", 
        "🔥 인기 영상",
        "🔤 키워드 분석",
        "🎯 성공 패턴",
        "💰 수익 분석",
        "🤖 AI 추천",
        "📊 상세 데이터",
        "🔮 트렌드 예측",
        "📋 내보내기 & 리포트"
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
        display_success_patterns(visualizer)
    
    with tab6:
        display_revenue_analysis(visualizer, channel_info)
    
    with tab7:
        display_ai_recommendations(visualizer, channel_info)
    
    with tab8:
        display_detailed_data()
    
    with tab9:
        display_trend_prediction(visualizer)
    
    with tab10:
        display_export_options(visualizer)

def display_performance_overview(visualizer):
    """Display performance overview charts"""
    st.subheader("📈 성과 개요")
    
    # Views distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("조회수 분포")
        fig = visualizer.create_views_distribution()
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("참여율 분석")
        fig = visualizer.create_engagement_chart()
        st.plotly_chart(fig, use_container_width=True)
    
    # Performance comparison: Shorts vs Long-form
    st.subheader("📊 쇼츠 vs 롱폼 성과 비교")
    fig = visualizer.create_shorts_vs_longform_comparison()
    st.plotly_chart(fig, use_container_width=True)
    
    # Duration vs Views correlation
    st.subheader("⏱️ 영상 길이와 조회수 상관관계")
    fig = visualizer.create_duration_views_correlation()
    st.plotly_chart(fig, use_container_width=True)

def display_upload_patterns(visualizer):
    """Display upload pattern analysis"""
    st.subheader("📅 업로드 패턴 분석")
    
    # Monthly upload trends
    st.subheader("📊 월별 업로드 트렌드")
    fig = visualizer.create_monthly_trends()
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📅 요일별 업로드 패턴")
        fig = visualizer.create_weekday_analysis()
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🕐 시간대별 업로드 패턴")
        fig = visualizer.create_hourly_analysis()
        st.plotly_chart(fig, use_container_width=True)
    
    # Upload consistency analysis
    st.subheader("📈 업로드 일관성 분석")
    consistency_data = visualizer.analyze_upload_consistency()
    
    # Display consistency data in a more user-friendly format
    if 'error' not in consistency_data:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("총 영상 수", f"{consistency_data['total_videos']:,}")
            st.metric("활동 기간", f"{consistency_data['date_range']['days_active']}일")
        
        with col2:
            st.metric("평균 업로드 간격", f"{consistency_data['upload_frequency']['average_gap_days']:.1f}일")
            st.metric("주당 업로드 수", f"{consistency_data['upload_patterns']['uploads_per_week']:.1f}개")
        
        with col3:
            st.metric("가장 활발한 요일", consistency_data['upload_patterns']['most_active_day'])
            st.metric("주요 업로드 시간", f"{consistency_data['upload_patterns']['most_active_hour']}시")
    else:
        st.error("데이터 분석 중 오류가 발생했습니다.")

def display_top_videos(visualizer):
    """Display top performing videos"""
    st.subheader("🔥 인기 영상 분석")
    
    # Top videos by different metrics
    metric_type = st.selectbox(
        "상위 영상 정렬 기준 선택",
        ["view_count", "like_count", "comment_count", "engagement_rate"],
        format_func=lambda x: {
            "view_count": "👁️ 조회수",
            "like_count": "👍 좋아요", 
            "comment_count": "💬 댓글수",
            "engagement_rate": "📊 참여율"
        }[x]
    )
    
    # Number of top videos to display
    top_count = st.slider("표시할 상위 영상 수", min_value=5, max_value=50, value=20)
    
    top_videos = visualizer.get_top_videos(metric=metric_type, count=top_count)
    
    # Display top videos table
    if top_videos:
        df = pd.DataFrame(top_videos)
        
        # Format the dataframe for display
        display_df = df[['title', 'published_at', 'view_count', 'like_count', 'comment_count', 'duration_formatted', 'is_short']].copy()
        display_df.columns = ['제목', '업로드일', '조회수', '좋아요', '댓글수', '길이', '유형']
        display_df['유형'] = ['쇼츠' if x else '롱폼' for x in display_df['유형']]
        
        # Format numbers with commas
        for col in ['조회수', '좋아요', '댓글수']:
            if col in display_df.columns:
                display_df[col] = [f"{x:,}" if isinstance(x, (int, float)) else x for x in display_df[col]]
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Top video performance chart
        metric_name = {
            "view_count": "조회수",
            "like_count": "좋아요",
            "comment_count": "댓글수",
            "engagement_rate": "참여율"
        }[metric_type]
        
        st.subheader(f"📊 {metric_name} 기준 상위 10개 영상")
        fig = visualizer.create_top_videos_chart(metric=metric_type, count=10)
        st.plotly_chart(fig, use_container_width=True)
        
        # Performance insights
        if len(top_videos) >= 3:
            st.subheader("💡 인기 영상 인사이트")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**상위 3개 영상 평균 성과:**")
                top_3 = top_videos[:3]
                avg_views = sum(v['view_count'] for v in top_3) / 3
                avg_likes = sum(v['like_count'] for v in top_3) / 3
                avg_comments = sum(v['comment_count'] for v in top_3) / 3
                
                st.metric("평균 조회수", f"{avg_views:,.0f}")
                st.metric("평균 좋아요", f"{avg_likes:,.0f}")
                st.metric("평균 댓글", f"{avg_comments:,.0f}")
            
            with col2:
                st.write("**인기 영상 유형 분포:**")
                shorts_in_top = sum(1 for v in top_videos[:10] if v.get('is_short', False))
                longform_in_top = 10 - shorts_in_top
                
                st.metric("상위 10개 중 쇼츠", f"{shorts_in_top}개")
                st.metric("상위 10개 중 롱폼", f"{longform_in_top}개")
    else:
        st.info("표시할 영상 데이터가 없습니다.")

def display_success_patterns(visualizer):
    """Display analysis of successful video patterns"""
    st.subheader("🎯 성공 패턴 분석")
    
    # Get successful patterns
    patterns = visualizer.analyze_successful_patterns()
    
    if patterns and 'top_keywords' in patterns:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔥 고성과 키워드")
            if patterns.get('top_keywords'):
                keywords_data = []
                for keyword, data in list(patterns['top_keywords'].items())[:10]:
                    keywords_data.append({
                        '키워드': keyword,
                        '영상수': data['count'],
                        '평균 조회수': f"{data['avg_views']:,.0f}"
                    })
                
                if keywords_data:
                    st.dataframe(pd.DataFrame(keywords_data), use_container_width=True, hide_index=True)
                else:
                    st.info("키워드 데이터가 없습니다.")
            else:
                st.info("분석할 키워드가 없습니다.")
        
        with col2:
            st.subheader("📈 최적 업로드 시간")
            if patterns.get('best_times'):
                times_data = []
                for time_info in patterns['best_times'][:5]:
                    # Handle both dict and other formats safely
                    if isinstance(time_info, dict):
                        hour = time_info.get('hour', 0)
                        count = time_info.get('count', 0)
                        avg_views = time_info.get('avg_views', 0)
                        times_data.append({
                            '시간대': f"{hour}시",
                            '영상수': count,
                            '평균 조회수': f"{avg_views:,.0f}"
                        })
                
                if times_data:
                    st.dataframe(pd.DataFrame(times_data), use_container_width=True, hide_index=True)
                else:
                    st.info("시간대 데이터가 없습니다.")
            else:
                st.info("업로드 시간 패턴을 찾을 수 없습니다.")
    
    # Best performing video length analysis
    st.subheader("⏱️ 최적 영상 길이 분석")
    videos_data = visualizer.videos_data
    if videos_data:
        # Group by duration ranges
        duration_ranges = []
        for video in videos_data:
            duration = video.get('duration_seconds', 0)
            if duration <= 60:
                range_name = "쇼츠 (≤60초)"
            elif duration <= 300:
                range_name = "단편 (1-5분)"
            elif duration <= 600:
                range_name = "중편 (5-10분)"
            elif duration <= 1200:
                range_name = "장편 (10-20분)"
            else:
                range_name = "장시간 (>20분)"
            
            duration_ranges.append({
                'range': range_name,
                'views': video.get('view_count', 0),
                'likes': video.get('like_count', 0),
                'comments': video.get('comment_count', 0)
            })
        
        if duration_ranges:
            df_duration = pd.DataFrame(duration_ranges)
            duration_summary = df_duration.groupby('range').agg({
                'views': ['count', 'mean', 'median'],
                'likes': 'mean',
                'comments': 'mean'
            }).round(0)
            
            duration_summary.columns = ['영상수', '평균조회수', '중간조회수', '평균좋아요', '평균댓글']
            duration_summary = duration_summary.reset_index()
            duration_summary.columns = ['길이범위', '영상수', '평균조회수', '중간조회수', '평균좋아요', '평균댓글']
            
            # Format numbers
            for col in ['영상수', '평균조회수', '중간조회수', '평균좋아요', '평균댓글']:
                duration_summary[col] = duration_summary[col].apply(lambda x: f"{int(x):,}")
            
            st.dataframe(duration_summary, use_container_width=True, hide_index=True)
    
    # Title pattern analysis
    st.subheader("📝 제목 패턴 분석")
    if videos_data:
        # Analyze title characteristics of top performing videos
        top_videos = sorted(videos_data, key=lambda x: x.get('view_count', 0), reverse=True)[:20]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_title_length = sum(len(v.get('title', '')) for v in top_videos) / len(top_videos)
            st.metric("상위 영상 평균 제목 길이", f"{avg_title_length:.0f}자")
        
        with col2:
            question_titles = sum(1 for v in top_videos if '?' in v.get('title', ''))
            st.metric("물음표 포함 제목", f"{question_titles}개")
        
        with col3:
            exclamation_titles = sum(1 for v in top_videos if '!' in v.get('title', ''))
            st.metric("느낌표 포함 제목", f"{exclamation_titles}개")

def display_trend_prediction(visualizer):
    """Display trend prediction and future insights"""
    st.subheader("🔮 트렌드 예측 및 인사이트")
    
    videos_data = visualizer.videos_data
    if not videos_data or len(videos_data) < 10:
        st.warning("트렌드 예측을 위해서는 최소 10개 이상의 영상이 필요합니다.")
        return
    
    # Growth trend analysis
    st.subheader("📈 성장 트렌드 분석")
    
    # Sort videos by date
    sorted_videos = sorted(videos_data, key=lambda x: x.get('published_at'))
    
    # Calculate monthly growth
    monthly_data = {}
    for video in sorted_videos:
        month_key = video['published_at'].strftime('%Y-%m')
        if month_key not in monthly_data:
            monthly_data[month_key] = {
                'count': 0,
                'total_views': 0,
                'total_likes': 0,
                'total_comments': 0
            }
        monthly_data[month_key]['count'] += 1
        monthly_data[month_key]['total_views'] += video.get('view_count', 0)
        monthly_data[month_key]['total_likes'] += video.get('like_count', 0)
        monthly_data[month_key]['total_comments'] += video.get('comment_count', 0)
    
    if len(monthly_data) >= 3:
        months = sorted(monthly_data.keys())
        recent_months = months[-3:]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            recent_avg_views = sum(monthly_data[m]['total_views'] for m in recent_months) / len(recent_months)
            older_months = months[:-3] if len(months) > 3 else months[:3]
            older_avg_views = sum(monthly_data[m]['total_views'] for m in older_months) / len(older_months) if older_months else recent_avg_views
            
            growth_rate = ((recent_avg_views - older_avg_views) / older_avg_views * 100) if older_avg_views > 0 else 0
            st.metric("최근 3개월 성장률", f"{growth_rate:+.1f}%")
        
        with col2:
            recent_upload_count = sum(monthly_data[m]['count'] for m in recent_months)
            st.metric("최근 3개월 업로드", f"{recent_upload_count}개")
        
        with col3:
            if len(recent_months) >= 2:
                last_month_views = monthly_data[recent_months[-1]]['total_views']
                prev_month_views = monthly_data[recent_months[-2]]['total_views']
                month_growth = ((last_month_views - prev_month_views) / prev_month_views * 100) if prev_month_views > 0 else 0
                st.metric("전월 대비 성장률", f"{month_growth:+.1f}%")
    
    # Content recommendations
    st.subheader("💡 콘텐츠 추천")
    
    # Analyze successful content patterns
    top_performing = sorted(videos_data, key=lambda x: x.get('view_count', 0), reverse=True)[:10]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**성공 요인 분석:**")
        
        # Most successful video type
        shorts_performance = [v for v in top_performing if v.get('is_short', False)]
        longform_performance = [v for v in top_performing if not v.get('is_short', False)]
        
        if len(shorts_performance) > len(longform_performance):
            st.info("🎯 쇼츠 콘텐츠가 더 높은 성과를 보입니다")
        else:
            st.info("🎯 롱폼 콘텐츠가 더 높은 성과를 보입니다")
        
        # Best upload day
        day_performance = {}
        for video in top_performing:
            day = video['published_at'].strftime('%A')
            if day not in day_performance:
                day_performance[day] = 0
            day_performance[day] += 1
        
        if day_performance:
            best_day = max(day_performance.keys(), key=lambda x: day_performance[x])
            day_names = {
                'Monday': '월요일', 'Tuesday': '화요일', 'Wednesday': '수요일',
                'Thursday': '목요일', 'Friday': '금요일', 'Saturday': '토요일', 'Sunday': '일요일'
            }
            st.info(f"📅 {day_names.get(best_day, best_day)}에 업로드한 영상의 성과가 좋습니다")
    
    with col2:
        st.write("**개선 제안:**")
        
        # Upload consistency
        upload_gaps = []
        for i in range(1, len(sorted_videos)):
            gap = (sorted_videos[i]['published_at'] - sorted_videos[i-1]['published_at']).days
            upload_gaps.append(gap)
        
        if upload_gaps:
            avg_gap = sum(upload_gaps) / len(upload_gaps)
            if avg_gap > 7:
                st.warning("⚡ 업로드 주기를 더 짧게 하면 성장에 도움이 될 수 있습니다")
            elif avg_gap < 1:
                st.warning("⏰ 너무 자주 업로드하면 품질이 떨어질 수 있습니다")
            else:
                st.success("✅ 적절한 업로드 주기를 유지하고 있습니다")
        
        # Engagement rate analysis
        recent_videos = sorted_videos[-10:] if len(sorted_videos) >= 10 else sorted_videos
        avg_engagement = sum(v.get('engagement_rate', 0) for v in recent_videos) / len(recent_videos)
        
        if avg_engagement < 2:
            st.warning("💬 시청자 참여도가 낮습니다. 댓글을 유도하는 질문이나 상호작용을 늘려보세요")
        elif avg_engagement > 5:
            st.success("🔥 높은 참여도를 유지하고 있습니다!")
        else:
            st.info("📊 평균적인 참여도입니다. 더 많은 상호작용을 시도해보세요")

def display_revenue_analysis(visualizer, channel_info):
    """Display revenue estimation and monetization analysis"""
    st.subheader("💰 수익 분석 및 예상")
    
    videos_data = visualizer.videos_data
    if not videos_data:
        st.warning("수익 분석을 위한 데이터가 없습니다.")
        return
    
    # Calculate revenue estimates
    total_views = sum(video.get('view_count', 0) for video in videos_data)
    subscriber_count = channel_info.get('subscriber_count', 0)
    
    # Revenue calculation (rough estimates based on industry averages)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Ad revenue estimation (RPM: Revenue per Mille)
        estimated_rpm = 1.5  # $1-3 per 1000 views average
        ad_revenue = (total_views / 1000) * estimated_rpm
        st.metric("예상 광고 수익", f"${ad_revenue:,.0f}")
    
    with col2:
        # Sponsorship potential
        if subscriber_count > 10000:
            sponsor_rate = subscriber_count * 0.01  # $0.01 per subscriber
            st.metric("스폰서십 잠재가치", f"${sponsor_rate:,.0f}")
        else:
            st.metric("스폰서십 잠재가치", "N/A")
    
    with col3:
        # Monthly earning potential
        from datetime import timezone
        now = datetime.now(timezone.utc)
        recent_videos = []
        for v in videos_data:
            pub_date = v['published_at']
            if hasattr(pub_date, 'tz_localize'):
                pub_date = pub_date.tz_localize('UTC') if pub_date.tz is None else pub_date
            elif not hasattr(pub_date, 'tzinfo') or pub_date.tzinfo is None:
                pub_date = pub_date.replace(tzinfo=timezone.utc)
            
            if (now - pub_date).days <= 30:
                recent_videos.append(v)
        monthly_views = sum(v.get('view_count', 0) for v in recent_videos)
        monthly_revenue = (monthly_views / 1000) * estimated_rpm
        st.metric("월 예상 수익", f"${monthly_revenue:,.0f}")
    
    with col4:
        # Growth potential
        if len(videos_data) >= 10:
            recent_avg = sum(v.get('view_count', 0) for v in videos_data[-5:]) / 5
            older_avg = sum(v.get('view_count', 0) for v in videos_data[-10:-5]) / 5
            growth = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
            st.metric("성장률", f"{growth:+.1f}%")
    
    # Revenue breakdown chart
    st.subheader("📊 수익원별 분석")
    
    # Create revenue sources data
    revenue_sources = {
        '광고 수익': ad_revenue,
        '멤버십': ad_revenue * 0.3,  # Estimated membership revenue
        '슈퍼챗': ad_revenue * 0.1,   # Estimated super chat
        '머천다이즈': ad_revenue * 0.2  # Estimated merchandise
    }
    
    import plotly.express as px
    
    fig = px.pie(
        values=list(revenue_sources.values()),
        names=list(revenue_sources.keys()),
        title="예상 수익원 분포",
        color_discrete_sequence=['#FF0000', '#FF6B6B', '#FFD93D', '#4ECDC4']
    )
    
    fig.update_layout(
        font=dict(family="Noto Sans KR, sans-serif"),
        title_font=dict(size=16, family="Noto Sans KR, sans-serif")
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Revenue optimization tips
    st.subheader("💡 수익 최적화 팁")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**즉시 적용 가능:**")
        tips = []
        
        if subscriber_count < 1000:
            tips.append("• 1,000명 구독자 달성으로 수익화 시작")
        if len([v for v in videos_data if v.get('duration_seconds', 0) > 480]) < 5:
            tips.append("• 8분 이상 영상으로 중간 광고 삽입")
        if monthly_views < 10000:
            tips.append("• 업로드 주기 단축으로 노출 증대")
        
        if not tips:
            tips = ["• 현재 수익화 조건을 잘 만족하고 있습니다!"]
        
        for tip in tips:
            st.write(tip)
    
    with col2:
        st.write("**장기 전략:**")
        long_term_tips = [
            "• 브랜드 협찬 및 제품 리뷰 콘텐츠",
            "• 온라인 강의 또는 코칭 서비스",
            "• 구독자 전용 멤버십 혜택",
            "• 관련 상품 판매 (머천다이즈)"
        ]
        
        for tip in long_term_tips:
            st.write(tip)

def display_ai_recommendations(visualizer, channel_info):
    """Display AI-powered content recommendations"""
    st.subheader("🤖 AI 기반 콘텐츠 추천")
    
    videos_data = visualizer.videos_data
    if not videos_data:
        st.warning("AI 추천을 위한 데이터가 없습니다.")
        return
    
    # Analyze successful patterns
    top_videos = sorted(videos_data, key=lambda x: x.get('view_count', 0), reverse=True)[:10]
    
    # AI-style recommendations based on data analysis
    st.subheader("🎯 맞춤형 콘텐츠 전략")
    
    # Content type recommendation
    shorts_performance = [v for v in top_videos if v.get('is_short', False)]
    longform_performance = [v for v in top_videos if not v.get('is_short', False)]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📱 최적 콘텐츠 형식")
        if len(shorts_performance) > len(longform_performance):
            st.success("🎯 **쇼츠 콘텐츠 집중 추천**")
            st.write("• 60초 이하 임팩트 있는 콘텐츠")
            st.write("• 트렌딩 음악과 해시태그 활용")
            st.write("• 빠른 편집과 시각적 효과")
        else:
            st.success("🎯 **롱폼 콘텐츠 집중 추천**")
            st.write("• 10-15분 심층 분석 콘텐츠")
            st.write("• 상세한 정보와 스토리텔링")
            st.write("• 시리즈물로 구독자 유지")
    
    with col2:
        st.markdown("### ⏰ 최적 업로드 시간")
        
        # Find best upload times
        hour_performance = {}
        day_performance = {}
        
        for video in top_videos:
            hour = video['published_at'].hour
            day = video['published_at'].strftime('%A')
            
            if hour not in hour_performance:
                hour_performance[hour] = []
            if day not in day_performance:
                day_performance[day] = []
                
            hour_performance[hour].append(video.get('view_count', 0))
            day_performance[day].append(video.get('view_count', 0))
        
        # Calculate average performance
        best_hour = max(hour_performance.keys(), 
                       key=lambda x: sum(hour_performance[x]) / len(hour_performance[x])) if hour_performance else 12
        best_day = max(day_performance.keys(), 
                      key=lambda x: sum(day_performance[x]) / len(day_performance[x])) if day_performance else "Sunday"
        
        day_names = {
            'Monday': '월요일', 'Tuesday': '화요일', 'Wednesday': '수요일',
            'Thursday': '목요일', 'Friday': '금요일', 'Saturday': '토요일', 'Sunday': '일요일'
        }
        
        st.info(f"🕐 **{best_hour}시 업로드 추천**")
        st.info(f"📅 **{day_names.get(best_day, best_day)} 업로드 추천**")
    
    # Title optimization
    st.subheader("📝 제목 최적화 AI")
    
    # Analyze successful title patterns
    successful_titles = [v['title'] for v in top_videos if v.get('title')]
    
    if successful_titles:
        # Common words analysis
        from collections import Counter
        import re
        
        all_words = []
        for title in successful_titles:
            words = re.findall(r'\b\w+\b', title.lower())
            all_words.extend(words)
        
        common_words = Counter(all_words).most_common(10)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**성공 키워드 TOP 5:**")
            for word, count in common_words[:5]:
                st.write(f"• {word} ({count}회)")
        
        with col2:
            st.write("**제목 패턴 분석:**")
            avg_length = sum(len(title) for title in successful_titles) / len(successful_titles)
            question_count = sum(1 for title in successful_titles if '?' in title)
            exclamation_count = sum(1 for title in successful_titles if '!' in title)
            
            st.write(f"• 최적 제목 길이: {avg_length:.0f}자")
            st.write(f"• 물음표 사용: {question_count}개 영상")
            st.write(f"• 느낌표 사용: {exclamation_count}개 영상")
    
    # Content gap analysis
    st.subheader("🔍 콘텐츠 갭 분석")
    
    # Analyze upload frequency
    if len(videos_data) >= 5:
        recent_uploads = sorted(videos_data, key=lambda x: x['published_at'], reverse=True)[:5]
        upload_gaps = []
        
        for i in range(1, len(recent_uploads)):
            gap = (recent_uploads[i-1]['published_at'] - recent_uploads[i]['published_at']).days
            upload_gaps.append(gap)
        
        avg_gap = sum(upload_gaps) / len(upload_gaps) if upload_gaps else 7
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if avg_gap > 14:
                st.warning("⚠️ 업로드 주기가 너무 깁니다")
                st.write("권장: 주 1-2회 업로드")
            elif avg_gap < 2:
                st.warning("⚠️ 너무 자주 업로드하고 있습니다")
                st.write("권장: 품질 관리에 집중")
            else:
                st.success("✅ 적절한 업로드 주기")
        
        with col2:
            # Suggest trending topics (mock data for demo)
            st.write("**트렌딩 토픽 추천:**")
            trending_topics = ["AI 활용법", "2025 트렌드", "효율적인 작업", "새로운 기술", "라이프스타일"]
            for topic in trending_topics[:3]:
                st.write(f"• {topic}")
        
        with col3:
            st.write("**경쟁자 분석 필요:**")
            st.write("• 유사 채널 벤치마킹")
            st.write("• 차별화 포인트 발굴")
            st.write("• 협업 기회 탐색")
    
    # Action plan
    st.subheader("📋 실행 계획")
    
    st.markdown("""
    ### 🎯 다음 30일 액션 플랜
    
    **1주차**: 콘텐츠 기획 및 제작
    - [ ] 성공 키워드 기반 새 콘텐츠 기획
    - [ ] 최적 시간대 업로드 스케줄 설정
    - [ ] 썸네일 A/B 테스트 준비
    
    **2주차**: 최적화 및 분석
    - [ ] 제목 패턴 적용 및 테스트
    - [ ] 시청자 참여도 모니터링
    - [ ] 댓글 및 커뮤니티 관리 강화
    
    **3주차**: 확장 및 실험
    - [ ] 새로운 콘텐츠 형식 실험
    - [ ] 협업 또는 게스트 출연 검토
    - [ ] 시리즈 콘텐츠 기획
    
    **4주차**: 분석 및 개선
    - [ ] 월간 성과 분석
    - [ ] 다음 달 전략 수정
    - [ ] 수익화 방안 검토
    """)
    
    # Interactive recommendations
    st.subheader("🔮 개인화된 추천")
    
    recommendation_type = st.selectbox(
        "어떤 분야의 추천을 받고 싶으신가요?",
        ["콘텐츠 주제", "편집 스타일", "마케팅 전략", "수익화 방법"]
    )
    
    if recommendation_type == "콘텐츠 주제":
        st.success("🎬 데이터 기반 추천 주제:")
        st.write("• 시청자들이 가장 좋아하는 스타일의 심화 버전")
        st.write("• 현재 트렌딩 중인 키워드와 채널 특성 결합")
        st.write("• 계절성을 고려한 타이밍 콘텐츠")
    
    elif recommendation_type == "편집 스타일":
        st.success("✂️ 편집 스타일 개선점:")
        # Get performance data for editing recommendations
        top_videos = sorted(videos_data, key=lambda x: x.get('view_count', 0), reverse=True)[:10]
        shorts_performance = [v for v in top_videos if v.get('is_short', False)]
        longform_performance = [v for v in top_videos if not v.get('is_short', False)]
        
        if len(shorts_performance) > len(longform_performance):
            st.write("• 빠른 컷 편집과 역동적인 트랜지션")
            st.write("• 시각적 임팩트를 위한 텍스트 오버레이")
        else:
            st.write("• 스토리텔링을 위한 자연스러운 편집")
            st.write("• 정보 전달을 위한 그래픽 요소 활용")
    
    elif recommendation_type == "마케팅 전략":
        st.success("📢 마케팅 전략:")
        st.write("• 성공 영상의 키워드를 활용한 SEO 최적화")
        st.write("• 시청자와의 상호작용 증대 방안")
        st.write("• 소셜미디어 크로스 프로모션")
    
    else:  # 수익화 방법
        st.success("💰 수익화 전략:")
        subscriber_count = channel_info.get('subscriber_count', 0)
        if subscriber_count < 1000:
            st.write("• 구독자 1000명 달성을 위한 콘텐츠 집중")
        else:
            st.write("• 다양한 수익원 개발 (스폰서십, 멤버십)")
        st.write("• 브랜드 가치 구축을 위한 일관성 있는 콘텐츠")

def display_keywords_analysis(visualizer):
    """Display keyword and content analysis"""
    st.subheader("🔤 Keywords & Content Analysis")
    
    # Keyword analysis options
    analysis_source = st.selectbox(
        "키워드 분석 대상:",
        ["titles", "descriptions", "tags"],
        format_func=lambda x: {
            "titles": "📝 영상 제목",
            "descriptions": "📄 설명란",
            "tags": "🏷️ 태그"
        }[x]
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(f"☁️ 워드 클라우드 - { {'titles':'제목','descriptions':'설명','tags':'태그'}[analysis_source] }")
        wordcloud_fig = visualizer.create_wordcloud(source=analysis_source)
        if wordcloud_fig:
            st.pyplot(wordcloud_fig, use_container_width=True)
        else:
            st.info(f"{ {'titles':'제목','descriptions':'설명','tags':'태그'}[analysis_source] } 데이터가 부족하여 워드클라우드를 생성할 수 없습니다.")

    with col2:
        st.subheader(f"📊 주요 키워드 - { {'titles':'제목','descriptions':'설명','tags':'태그'}[analysis_source] }")
        keywords_fig = visualizer.create_keywords_chart(source=analysis_source, top_n=20)
        if keywords_fig:
            st.plotly_chart(keywords_fig, use_container_width=True)
        else:
            st.info(f"{ {'titles':'제목','descriptions':'설명','tags':'태그'}[analysis_source] } 데이터가 부족하여 키워드 분석을 할 수 없습니다.")


    # 성공 영상 패턴
    st.subheader("🎯 성공 영상 패턴")
    patterns = visualizer.analyze_successful_patterns()

    if patterns:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔥 고성과 키워드")
            if patterns.get('top_keywords'):
                for keyword, data in patterns['top_keywords'].items():
                    st.write(f"**{keyword}**: {data['count']}개 영상, 평균 {data['avg_views']:,.0f}회 조회수")
        
        with col2:
            st.subheader("📈 최적 업로드 시간")
            if patterns.get('best_times'):
                for time_info in patterns['best_times']:
                    st.write(f"**{time_info['period']}**: 평균 {time_info['avg_views']:,.0f}회 ({time_info['count']}개 영상)")

def display_detailed_data():
    """Display detailed video data with filtering and sorting"""
    st.subheader("📊 상세 영상 데이터")
    
    videos_data = st.session_state.channel_data['videos']
    df = pd.DataFrame(videos_data)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        video_type_filter = st.selectbox(
            "영상 유형",
            ["전체", "쇼츠", "롱폼"],
            key="type_filter"
        )
    
    with col2:
        min_views = st.number_input(
            "최소 조회수",
            min_value=0,
            value=0,
            key="min_views_filter"
        )
    
    with col3:
        date_range = st.date_input(
            "날짜 범위",
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
    search_term = st.text_input("🔍 제목 내 검색", key="search_filter")
    if search_term:
        filtered_df = filtered_df[filtered_df['title'].str.contains(search_term, case=False, na=False)]
    
    # Display filtered data
    st.write(f"Showing {len(filtered_df)} of {len(df)} videos")
    
    # Select columns to display
    available_columns = ['title', 'published_at', 'view_count', 'like_count', 'comment_count', 
                        'duration_formatted', 'is_short', 'tags']
    selected_columns = st.multiselect(
        "표시할 컬럼 선택",
        available_columns,
        default=['title', 'published_at', 'view_count', 'like_count', 'comment_count', 'duration_formatted'],
        key="column_selector"
    )
    
    if selected_columns:
        display_df = filtered_df[selected_columns].copy()
        
        # Format column names
        column_mapping = {
            'title': '제목',
            'published_at': '업로드일',
            'view_count': '조회수',
            'like_count': '좋아요',
            'comment_count': '댓글수',
            'duration_formatted': '길이',
            'is_short': '유형',
            'tags': '태그'
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
    st.subheader("📋 내보내기 및 리포트")
    
    videos_data = st.session_state.channel_data['videos']
    channel_info = st.session_state.channel_data['channel_info']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 데이터 내보내기")
        
        # CSV export
        if st.button("📄 CSV로 내보내기", use_container_width=True):
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
        if st.button("📋 JSON으로 내보내기", use_container_width=True):
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
        st.subheader("📈 분석 요약")
        
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
            label="📄 요약 리포트 다운로드",
            data=summary_text,
            file_name=f"{channel_info.get('title', '채널')}_summary.txt",
            mime='text/plain',
            use_container_width=True
        )

if __name__ == "__main__":
    main()
