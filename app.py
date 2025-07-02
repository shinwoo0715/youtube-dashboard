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

# Custom CSS for modern UI/UX
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&display=swap');
    
    .main {
        font-family: 'Noto Sans KR', sans-serif;
    }
    
    .main-header {
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #FF0000 0%, #FF6B6B 50%, #FF9999 100%);
        color: white;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(255, 0, 0, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
        animation: shine 3s infinite;
    }
    
    @keyframes shine {
        0% { transform: translateX(-100%) translateY(-100%) rotate(30deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(30deg); }
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        font-size: 1.1rem;
        opacity: 0.9;
        font-weight: 400;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid #e9ecef;
        margin: 0.75rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #FF0000, #FF6B6B, #FF9999);
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }
    
    .progress-container {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        border: 1px solid #dee2e6;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
    }
    
    .error-message {
        background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
        color: #c62828;
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #c62828;
        margin: 1.5rem 0;
        box-shadow: 0 5px 15px rgba(198, 40, 40, 0.1);
        animation: slideIn 0.5s ease;
    }
    
    .success-message {
        background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
        color: #2e7d32;
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #2e7d32;
        margin: 1.5rem 0;
        box-shadow: 0 5px 15px rgba(46, 125, 50, 0.1);
        animation: slideIn 0.5s ease;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .sidebar .stSelectbox, .sidebar .stTextInput, .sidebar .stTextArea {
        margin-bottom: 1.5rem;
    }
    
    .sidebar .stButton > button {
        width: 100%;
        height: 3rem;
        border-radius: 10px;
        font-weight: 600;
        font-size: 1.1rem;
        background: linear-gradient(135deg, #FF0000 0%, #FF6B6B 100%);
        border: none;
        color: white;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(255, 0, 0, 0.2);
    }
    
    .sidebar .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(255, 0, 0, 0.3);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        padding: 10px 20px;
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        border-radius: 10px;
        border: 1px solid #dee2e6;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #FF0000 0%, #FF6B6B 100%);
        color: white !important;
        box-shadow: 0 5px 15px rgba(255, 0, 0, 0.2);
    }
    
    .element-container .stMetric {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        box-shadow: 0 3px 10px rgba(0,0,0,0.05);
    }
    
    .feature-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 2rem;
        border-radius: 20px;
        border: 1px solid #e9ecef;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.15);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #FF0000, #FF6B6B);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        
        .main-header {
            padding: 2rem 1rem;
        }
        
        .metric-card {
            font-size: 0.9rem;
            padding: 1rem;
        }
        
        .feature-card {
            padding: 1.5rem;
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
    
    # Main header
    st.markdown('<div class="main-header"><h1>📊 유튜브 채널 완전 분석</h1><p>모든 유튜브 채널의 완벽한 데이터 분석 도구</p></div>', unsafe_allow_html=True)
    
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
                [50, 100, 200, 500, 1000, 2000],
                index=2,
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
    
    # Create enhanced analysis tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "📈 성과 개요",
        "📅 업로드 패턴", 
        "🔥 인기 영상",
        "🔤 키워드 분석",
        "🎯 성공 패턴",
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
        display_detailed_data()
    
    with tab7:
        display_trend_prediction(visualizer)
    
    with tab8:
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
        display_df['유형'] = display_df['유형'].apply(lambda x: '쇼츠' if x else '롱폼')
        
        # Format numbers with commas
        for col in ['조회수', '좋아요', '댓글수']:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: f"{x:,}" if isinstance(x, (int, float)) else x)
        
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
                        '평균 조회수': f"{data['avg_views']:,.0f}",
                        '총 조회수': f"{data['total_views']:,.0f}"
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
                    times_data.append({
                        '시간대': f"{time_info['hour']}시",
                        '영상수': time_info['count'],
                        '평균 조회수': f"{time_info['avg_views']:,.0f}"
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
