import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from wordcloud import WordCloud
import numpy as np
from datetime import datetime, timedelta
from collections import Counter
import seaborn as sns
import io
import base64

class DataVisualizer:
    """Comprehensive data visualization for YouTube channel analysis"""
    
    def __init__(self, videos_data):
        self.videos_data = videos_data
        self.df = pd.DataFrame(videos_data)
        
        # Ensure datetime columns
        if not self.df.empty:
            self.df['published_at'] = pd.to_datetime(self.df['published_at'])
    
    def create_views_distribution(self):
        """Create views distribution histogram"""
        if self.df.empty:
            return self._create_empty_chart("No data available")
        
        fig = px.histogram(
            self.df,
            x='view_count',
            nbins=30,
            title='Views Distribution',
            labels={'view_count': 'Views', 'count': 'Number of Videos'},
            color_discrete_sequence=['#FF0000']
        )
        
        fig.update_layout(
            showlegend=False,
            height=400,
            xaxis_tickformat=',',
            hovermode='x unified'
        )
        
        return fig
    
    def create_engagement_chart(self):
        """Create engagement rate distribution"""
        if self.df.empty:
            return self._create_empty_chart("No data available")
        
        fig = px.scatter(
            self.df,
            x='view_count',
            y='engagement_rate',
            color='is_short',
            size='like_count',
            hover_data=['title', 'published_at'],
            title='Engagement Rate vs Views',
            labels={
                'view_count': 'Views',
                'engagement_rate': 'Engagement Rate (%)',
                'is_short': 'Video Type'
            },
            color_discrete_map={True: '#FF6B6B', False: '#4ECDC4'}
        )
        
        fig.update_layout(height=400, xaxis_tickformat=',')
        return fig
    
    def create_shorts_vs_longform_comparison(self):
        """Compare performance between Shorts and Long-form videos"""
        if self.df.empty:
            return self._create_empty_chart("No data available")
        
        # Aggregate data by video type
        comparison_data = self.df.groupby('is_short').agg({
            'view_count': ['mean', 'median', 'sum', 'count'],
            'like_count': ['mean', 'median', 'sum'],
            'comment_count': ['mean', 'median', 'sum'],
            'engagement_rate': ['mean', 'median']
        }).round(2)
        
        # Flatten column names
        comparison_data.columns = ['_'.join(col).strip() for col in comparison_data.columns]
        comparison_data = comparison_data.reset_index()
        comparison_data['video_type'] = comparison_data['is_short'].map({True: 'Shorts', False: 'Long-form'})
        
        # Create subplot with multiple metrics
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Average Views', 'Average Likes', 'Average Comments', 'Average Engagement Rate'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        metrics = [
            ('view_count_mean', 'Views'),
            ('like_count_mean', 'Likes'),
            ('comment_count_mean', 'Comments'),
            ('engagement_rate_mean', 'Engagement Rate (%)')
        ]
        
        positions = [(1, 1), (1, 2), (2, 1), (2, 2)]
        colors = ['#FF0000', '#FF6B6B']
        
        for i, (metric, title) in enumerate(metrics):
            row, col = positions[i]
            
            fig.add_trace(
                go.Bar(
                    x=comparison_data['video_type'],
                    y=comparison_data[metric],
                    name=title,
                    marker_color=colors,
                    showlegend=False
                ),
                row=row, col=col
            )
        
        fig.update_layout(
            title_text="Shorts vs Long-form Performance Comparison",
            height=600,
            showlegend=False
        )
        
        return fig
    
    def create_duration_views_correlation(self):
        """Create scatter plot showing duration vs views correlation"""
        if self.df.empty:
            return self._create_empty_chart("No data available")
        
        fig = px.scatter(
            self.df,
            x='duration_seconds',
            y='view_count',
            color='is_short',
            size='like_count',
            hover_data=['title', 'duration_formatted'],
            title='Video Duration vs Views',
            labels={
                'duration_seconds': 'Duration (seconds)',
                'view_count': 'Views',
                'is_short': 'Video Type'
            },
            color_discrete_map={True: '#FF6B6B', False: '#4ECDC4'}
        )
        
        fig.update_layout(height=400, xaxis_tickformat=',', yaxis_tickformat=',')
        return fig
    
    def create_monthly_trends(self):
        """Create monthly upload and performance trends"""
        if self.df.empty:
            return self._create_empty_chart("No data available")
        
        # Group by month and video type
        monthly_data = self.df.groupby([
            self.df['published_at'].dt.to_period('M'),
            'is_short'
        ]).agg({
            'video_id': 'count',
            'view_count': 'mean',
            'like_count': 'mean',
            'engagement_rate': 'mean'
        }).reset_index()
        
        monthly_data['month_str'] = monthly_data['published_at'].astype(str)
        monthly_data['video_type'] = monthly_data['is_short'].map({True: 'Shorts', False: 'Long-form'})
        
        # Create subplot with uploads and average views
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Monthly Upload Count', 'Average Views per Month'),
            vertical_spacing=0.1
        )
        
        for video_type in monthly_data['video_type'].unique():
            data = monthly_data[monthly_data['video_type'] == video_type]
            color = '#FF6B6B' if video_type == 'Shorts' else '#4ECDC4'
            
            # Upload count
            fig.add_trace(
                go.Scatter(
                    x=data['month_str'],
                    y=data['video_id'],
                    mode='lines+markers',
                    name=f'{video_type} - Uploads',
                    line=dict(color=color),
                    showlegend=True
                ),
                row=1, col=1
            )
            
            # Average views
            fig.add_trace(
                go.Scatter(
                    x=data['month_str'],
                    y=data['view_count'],
                    mode='lines+markers',
                    name=f'{video_type} - Avg Views',
                    line=dict(color=color, dash='dash'),
                    showlegend=True
                ),
                row=2, col=1
            )
        
        fig.update_layout(
            title_text="Monthly Upload and Performance Trends",
            height=600,
            hovermode='x unified'
        )
        
        fig.update_yaxes(title_text="Number of Videos", row=1, col=1)
        fig.update_yaxes(title_text="Average Views", tickformat=',', row=2, col=1)
        fig.update_xaxes(title_text="Month", row=2, col=1)
        
        return fig
    
    def create_weekday_analysis(self):
        """Analyze upload patterns by day of week"""
        if self.df.empty:
            return self._create_empty_chart("No data available")
        
        weekday_data = self.df.groupby('day_of_week').agg({
            'video_id': 'count',
            'view_count': 'mean',
            'engagement_rate': 'mean'
        }).reset_index()
        
        # Order by weekday
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekday_data['day_of_week'] = pd.Categorical(weekday_data['day_of_week'], categories=weekday_order, ordered=True)
        weekday_data = weekday_data.sort_values('day_of_week')
        
        fig = go.Figure()
        
        # Upload count bars
        fig.add_trace(go.Bar(
            x=weekday_data['day_of_week'],
            y=weekday_data['video_id'],
            name='Upload Count',
            marker_color='#FF0000',
            yaxis='y1'
        ))
        
        # Average views line
        fig.add_trace(go.Scatter(
            x=weekday_data['day_of_week'],
            y=weekday_data['view_count'],
            mode='lines+markers',
            name='Avg Views',
            line=dict(color='#4ECDC4', width=3),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='Upload Pattern by Day of Week',
            xaxis_title='Day of Week',
            yaxis=dict(title='Upload Count', side='left'),
            yaxis2=dict(title='Average Views', side='right', overlaying='y', tickformat=','),
            height=400,
            hovermode='x unified'
        )
        
        return fig
    
    def create_hourly_analysis(self):
        """Analyze upload patterns by hour of day"""
        if self.df.empty:
            return self._create_empty_chart("No data available")
        
        hourly_data = self.df.groupby('hour_of_day').agg({
            'video_id': 'count',
            'view_count': 'mean'
        }).reset_index()
        
        fig = px.bar(
            hourly_data,
            x='hour_of_day',
            y='video_id',
            title='Upload Pattern by Hour of Day',
            labels={'hour_of_day': 'Hour (24h format)', 'video_id': 'Upload Count'},
            color_discrete_sequence=['#FF0000']
        )
        
        fig.update_layout(height=400, showlegend=False)
        return fig
    
    def analyze_upload_consistency(self):
        """Analyze upload consistency and patterns"""
        if self.df.empty:
            return {"error": "No data available"}
        
        # Calculate days between uploads
        sorted_dates = self.df['published_at'].sort_values()
        upload_gaps = sorted_dates.diff().dt.days.dropna()
        
        consistency_metrics = {
            "total_videos": len(self.df),
            "date_range": {
                "first_upload": sorted_dates.min().strftime('%Y-%m-%d'),
                "last_upload": sorted_dates.max().strftime('%Y-%m-%d'),
                "days_active": (sorted_dates.max() - sorted_dates.min()).days
            },
            "upload_frequency": {
                "average_gap_days": round(upload_gaps.mean(), 2),
                "median_gap_days": round(upload_gaps.median(), 2),
                "most_consistent_gap": round(upload_gaps.mode().iloc[0] if not upload_gaps.mode().empty else 0, 2)
            },
            "upload_patterns": {
                "most_active_day": self.df['day_of_week'].mode().iloc[0] if not self.df['day_of_week'].mode().empty else "N/A",
                "most_active_hour": int(self.df['hour_of_day'].mode().iloc[0]) if not self.df['hour_of_day'].mode().empty else "N/A",
                "uploads_per_week": round(len(self.df) / ((sorted_dates.max() - sorted_dates.min()).days / 7), 2)
            }
        }
        
        return consistency_metrics
    
    def get_top_videos(self, metric='view_count', count=20):
        """Get top performing videos by specified metric"""
        if self.df.empty:
            return []
        
        if metric not in self.df.columns:
            return []
        
        top_videos = self.df.nlargest(count, metric).to_dict('records')
        return top_videos
    
    def create_top_videos_chart(self, metric='view_count', count=10):
        """Create bar chart of top videos"""
        if self.df.empty:
            return self._create_empty_chart("No data available")
        
        top_videos = self.df.nlargest(count, metric)
        
        # Truncate long titles for display
        top_videos = top_videos.copy()
        top_videos['short_title'] = top_videos['title'].apply(lambda x: x[:50] + '...' if len(x) > 50 else x)
        
        fig = px.bar(
            top_videos,
            y='short_title',
            x=metric,
            orientation='h',
            title=f'Top {count} Videos by {metric.replace("_", " ").title()}',
            labels={metric: metric.replace('_', ' ').title(), 'short_title': 'Video Title'},
            color=metric,
            color_continuous_scale='Reds'
        )
        
        fig.update_layout(
            height=max(400, count * 40),
            yaxis={'categoryorder': 'total ascending'},
            xaxis_tickformat=','
        )
        
        return fig
    
    def create_wordcloud(self, source='titles', max_words=100):
        """Create word cloud from video titles, descriptions, or tags"""
        if self.df.empty:
            return None
        
        # Collect text based on source
        text_data = []
        
        if source == 'titles':
            text_data = self.df['title'].dropna().tolist()
        elif source == 'descriptions':
            text_data = self.df['description'].dropna().tolist()
        elif source == 'tags':
            all_tags = []
            for tags in self.df['tags'].dropna():
                if isinstance(tags, list):
                    all_tags.extend(tags)
            text_data = all_tags
        
        if not text_data:
            return None
        
        # Combine all text
        all_text = ' '.join(str(text) for text in text_data)
        
        if not all_text.strip():
            return None
        
        try:
            # Create word cloud
            wordcloud = WordCloud(
                width=800,
                height=400,
                background_color='white',
                max_words=max_words,
                colormap='Reds',
                relative_scaling=0.5,
                random_state=42
            ).generate(all_text)
            
            # Create matplotlib figure
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            ax.set_title(f'Word Cloud - {source.title()}', fontsize=16, pad=20)
            
            plt.tight_layout()
            return fig
            
        except Exception as e:
            print(f"Error creating word cloud: {e}")
            return None
    
    def create_keywords_chart(self, source='titles', top_n=20):
        """Create bar chart of top keywords"""
        if self.df.empty:
            return self._create_empty_chart("No data available")
        
        # Extract keywords based on source
        all_keywords = []
        
        if source == 'titles':
            for words in self.df['title_words'].dropna():
                if isinstance(words, list):
                    all_keywords.extend(words)
        elif source == 'descriptions':
            for words in self.df['description_words'].dropna():
                if isinstance(words, list):
                    all_keywords.extend(words)
        elif source == 'tags':
            for tags in self.df['tags'].dropna():
                if isinstance(tags, list):
                    all_keywords.extend([tag.lower() for tag in tags])
        
        if not all_keywords:
            return self._create_empty_chart(f"No {source} data available")
        
        # Count keywords
        keyword_counts = Counter(all_keywords)
        top_keywords = dict(keyword_counts.most_common(top_n))
        
        if not top_keywords:
            return self._create_empty_chart(f"No keywords found in {source}")
        
        # Create bar chart
        keywords_df = pd.DataFrame(list(top_keywords.items()), columns=['keyword', 'count'])
        
        fig = px.bar(
            keywords_df,
            x='count',
            y='keyword',
            orientation='h',
            title=f'Top {top_n} Keywords - {source.title()}',
            labels={'count': 'Frequency', 'keyword': 'Keyword'},
            color='count',
            color_continuous_scale='Reds'
        )
        
        fig.update_layout(
            height=max(400, top_n * 25),
            yaxis={'categoryorder': 'total ascending'}
        )
        
        return fig
    
    def analyze_successful_patterns(self):
        """Analyze patterns in successful videos"""
        if self.df.empty:
            return {}
        
        # Define successful videos (top 25% by views)
        view_threshold = self.df['view_count'].quantile(0.75)
        successful_videos = self.df[self.df['view_count'] >= view_threshold]
        
        if successful_videos.empty:
            return {}
        
        patterns = {}
        
        # Analyze keywords in successful videos
        successful_keywords = []
        for words in successful_videos['title_words'].dropna():
            if isinstance(words, list):
                successful_keywords.extend(words)
        
        if successful_keywords:
            keyword_counts = Counter(successful_keywords)
            top_keywords = {}
            
            for keyword, count in keyword_counts.most_common(10):
                # Calculate average views for videos with this keyword
                keyword_videos = self.df[self.df['title_words'].apply(
                    lambda x: keyword in x if isinstance(x, list) else False
                )]
                
                if not keyword_videos.empty:
                    top_keywords[keyword] = {
                        'count': count,
                        'avg_views': keyword_videos['view_count'].mean()
                    }
            
            patterns['top_keywords'] = top_keywords
        
        # Analyze best upload times
        time_performance = successful_videos.groupby(['day_of_week', 'hour_of_day']).agg({
            'view_count': 'mean',
            'video_id': 'count'
        }).reset_index()
        
        time_performance = time_performance[time_performance['video_id'] >= 2]  # At least 2 videos
        top_times = time_performance.nlargest(5, 'view_count')
        
        patterns['best_times'] = []
        for _, row in top_times.iterrows():
            patterns['best_times'].append({
                'period': f"{row['day_of_week']} {row['hour_of_day']}:00",
                'avg_views': row['view_count'],
                'count': row['video_id']
            })
        
        return patterns
    
    def generate_summary_report(self, channel_info):
        """Generate comprehensive summary report"""
        if self.df.empty:
            return {"error": "No data available for summary"}
        
        # Basic statistics
        total_videos = len(self.df)
        total_views = self.df['view_count'].sum()
        total_likes = self.df['like_count'].sum()
        total_comments = self.df['comment_count'].sum()
        
        shorts_count = self.df['is_short'].sum()
        long_form_count = total_videos - shorts_count
        
        # Performance metrics
        avg_views = self.df['view_count'].mean()
        median_views = self.df['view_count'].median()
        avg_engagement = self.df['engagement_rate'].mean()
        
        # Top performing video
        top_video = self.df.loc[self.df['view_count'].idxmax()]
        
        # Upload patterns
        most_active_day = self.df['day_of_week'].mode().iloc[0] if not self.df['day_of_week'].mode().empty else "N/A"
        most_active_hour = self.df['hour_of_day'].mode().iloc[0] if not self.df['hour_of_day'].mode().empty else "N/A"
        
        # Duration analysis
        avg_duration_shorts = self.df[self.df['is_short']]['duration_seconds'].mean() if shorts_count > 0 else 0
        avg_duration_long = self.df[~self.df['is_short']]['duration_seconds'].mean() if long_form_count > 0 else 0
        
        summary = {
            "Channel Information": {
                "Channel Name": channel_info.get('title', 'Unknown'),
                "Total Channel Subscribers": f"{channel_info.get('subscriber_count', 0):,}",
                "Analysis Period": f"{self.df['published_at'].min().strftime('%Y-%m-%d')} to {self.df['published_at'].max().strftime('%Y-%m-%d')}"
            },
            "Video Statistics": {
                "Total Videos Analyzed": f"{total_videos:,}",
                "Shorts": f"{shorts_count:,}",
                "Long-form": f"{long_form_count:,}",
                "Total Views": f"{total_views:,}",
                "Total Likes": f"{total_likes:,}",
                "Total Comments": f"{total_comments:,}"
            },
            "Performance Metrics": {
                "Average Views per Video": f"{avg_views:,.0f}",
                "Median Views per Video": f"{median_views:,.0f}",
                "Average Engagement Rate": f"{avg_engagement:.2f}%",
                "Views per Subscriber": f"{total_views / max(channel_info.get('subscriber_count', 1), 1):.2f}"
            },
            "Top Performing Video": {
                "Title": top_video['title'][:100],
                "Views": f"{top_video['view_count']:,}",
                "Likes": f"{top_video['like_count']:,}",
                "Upload Date": top_video['published_at'].strftime('%Y-%m-%d')
            },
            "Upload Patterns": {
                "Most Active Day": most_active_day,
                "Most Active Hour": f"{most_active_hour}:00" if most_active_hour != "N/A" else "N/A",
                "Average Upload Frequency": f"{len(self.df) / ((self.df['published_at'].max() - self.df['published_at'].min()).days / 7):.1f} videos/week"
            },
            "Content Analysis": {
                "Average Shorts Duration": f"{avg_duration_shorts:.0f} seconds" if avg_duration_shorts > 0 else "N/A",
                "Average Long-form Duration": f"{avg_duration_long/60:.1f} minutes" if avg_duration_long > 0 else "N/A",
                "Shorts Performance": f"{self.df[self.df['is_short']]['view_count'].mean():,.0f} avg views" if shorts_count > 0 else "N/A",
                "Long-form Performance": f"{self.df[~self.df['is_short']]['view_count'].mean():,.0f} avg views" if long_form_count > 0 else "N/A"
            }
        }
        
        return summary
    
    def _create_empty_chart(self, message):
        """Create empty chart with message"""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(
            height=400,
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=False, showticklabels=False, zeroline=False)
        )
        return fig
