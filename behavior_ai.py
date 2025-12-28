#!/usr/bin/env python3
"""
Behavior AI Simulator
Uses statistical models for human-like behavior simulation
"""

import random
import numpy as np
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import math

class BehaviorPattern(Enum):
    """Behavior pattern types"""
    CASUAL_BROWSING = "casual_browsing"
    FOCUSED_WATCHING = "focused_watching"
    MULTITASKING = "multitasking"
    RESEARCH_MODE = "research_mode"
    ENTERTAINMENT = "entertainment"

@dataclass
class MouseAction:
    """Mouse action data"""
    x: int
    y: int
    action_type: str  # 'move', 'click', 'scroll', 'drag'
    timestamp: float
    duration: float = 0.0
    pressure: float = 1.0  # For touch devices

@dataclass
class ScrollAction:
    """Scroll action data"""
    direction: str  # 'up', 'down'
    amount: int
    speed: float
    timestamp: float
    smoothness: float = 0.8  # 0.0 to 1.0

@dataclass
class ViewSession:
    """Viewing session data"""
    start_time: float
    end_time: float
    video_duration: int
    watch_time: int
    retention_rate: float
    engagement_actions: List[Dict]
    attention_pattern: List[float]

class BehaviorAISimulator:
    """AI-powered behavior simulator for human-like interactions"""
    
    def __init__(self, config_path: str = "config_advanced.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Load behavior models
        self.behavior_models = self._load_behavior_models()
        self.mouse_patterns = self._load_mouse_patterns()
        self.scroll_patterns = self._load_scroll_patterns()
        self.attention_models = self._load_attention_models()
        
        # Statistics
        self.session_history = []
        self.pattern_usage = {pattern.value: 0 for pattern in BehaviorPattern}
        
    def _load_behavior_models(self) -> Dict[BehaviorPattern, Dict]:
        """Load pre-trained behavior models"""
        
        return {
            BehaviorPattern.CASUAL_BROWSING: {
                'description': 'Casual viewer, browsing for entertainment',
                'watch_completion': (0.3, 0.7),
                'attention_span': (15, 45),  # seconds
                'click_frequency': (0.1, 0.3),  # clicks per minute
                'scroll_frequency': (2, 5),  # scrolls per minute
                'pause_frequency': (0.5, 1.5),  # pauses per minute
                'engagement_rate': (0.1, 0.3),
                'preferred_times': ['afternoon', 'evening', 'night'],
                'content_preferences': ['entertainment', 'music', 'vlogs'],
                'device_bias': {'mobile': 0.6, 'desktop': 0.4}
            },
            BehaviorPattern.FOCUSED_WATCHING: {
                'description': 'Focused viewer, watching educational/tutorial content',
                'watch_completion': (0.7, 0.95),
                'attention_span': (60, 180),  # seconds
                'click_frequency': (0.05, 0.15),  # clicks per minute
                'scroll_frequency': (0.5, 2),  # scrolls per minute
                'pause_frequency': (0.8, 2.0),  # pauses per minute
                'engagement_rate': (0.4, 0.7),
                'preferred_times': ['morning', 'afternoon'],
                'content_preferences': ['educational', 'tutorial', 'documentary'],
                'device_bias': {'desktop': 0.7, 'tablet': 0.3}
            },
            BehaviorPattern.MULTITASKING: {
                'description': 'Viewer who multitasks while watching',
                'watch_completion': (0.2, 0.5),
                'attention_span': (5, 20),  # seconds
                'click_frequency': (0.3, 0.6),  # clicks per minute
                'scroll_frequency': (4, 8),  # scrolls per minute
                'pause_frequency': (2.0, 4.0),  # pauses per minute
                'engagement_rate': (0.05, 0.2),
                'preferred_times': ['afternoon', 'evening'],
                'content_preferences': ['entertainment', 'background'],
                'device_bias': {'mobile': 0.8, 'tablet': 0.2}
            },
            BehaviorPattern.RESEARCH_MODE: {
                'description': 'Viewer researching or comparing content',
                'watch_completion': (0.4, 0.6),
                'attention_span': (30, 90),  # seconds
                'click_frequency': (0.2, 0.4),  # clicks per minute
                'scroll_frequency': (3, 6),  # scrolls per minute
                'pause_frequency': (1.5, 3.0),  # pauses per minute
                'engagement_rate': (0.3, 0.5),
                'preferred_times': ['morning', 'afternoon'],
                'content_preferences': ['educational', 'review', 'comparison'],
                'device_bias': {'desktop': 0.9, 'tablet': 0.1}
            },
            BehaviorPattern.ENTERTAINMENT: {
                'description': 'Viewer seeking entertainment',
                'watch_completion': (0.5, 0.8),
                'attention_span': (20, 60),  # seconds
                'click_frequency': (0.15, 0.25),  # clicks per minute
                'scroll_frequency': (1, 3),  # scrolls per minute
                'pause_frequency': (0.3, 1.0),  # pauses per minute
                'engagement_rate': (0.2, 0.4),
                'preferred_times': ['evening', 'night'],
                'content_preferences': ['entertainment', 'comedy', 'music'],
                'device_bias': {'mobile': 0.5, 'desktop': 0.3, 'tv': 0.2}
            }
        }
    
    def _load_mouse_patterns(self) -> Dict[str, Dict]:
        """Load mouse movement patterns"""
        return {
            'straight': {
                'description': 'Direct, purposeful movements',
                'speed_range': (0.5, 2.0),  # pixels per ms
                'acceleration_range': (0.01, 0.05),
                'curvature_range': (0.0, 0.1),  # 0.0 = straight line
                'pause_probability': 0.1,
                'common_for': ['focused_watching', 'research_mode']
            },
            'exploratory': {
                'description': 'Curved, exploratory movements',
                'speed_range': (0.3, 1.5),
                'acceleration_range': (0.02, 0.08),
                'curvature_range': (0.2, 0.5),
                'pause_probability': 0.3,
                'common_for': ['casual_browsing', 'entertainment']
            },
            'hesitant': {
                'description': 'Slow, hesitant movements with pauses',
                'speed_range': (0.1, 0.8),
                'acceleration_range': (0.005, 0.02),
                'curvature_range': (0.3, 0.7),
                'pause_probability': 0.5,
                'common_for': ['research_mode', 'multitasking']
            },
            'rapid': {
                'description': 'Fast, rapid movements',
                'speed_range': (1.0, 3.0),
                'acceleration_range': (0.05, 0.15),
                'curvature_range': (0.1, 0.3),
                'pause_probability': 0.05,
                'common_for': ['multitasking']
            },
            'natural': {
                'description': 'Natural human-like movements',
                'speed_range': (0.4, 1.8),
                'acceleration_range': (0.01, 0.1),
                'curvature_range': (0.05, 0.4),
                'pause_probability': 0.2,
                'common_for': ['all']
            }
        }
    
    def _load_scroll_patterns(self) -> Dict[str, Dict]:
        """Load scrolling patterns"""
        return {
            'burst_scroll': {
                'description': 'Rapid scrolling in bursts',
                'speed_range': (100, 500),  # pixels per second
                'burst_count': (2, 5),
                'burst_duration': (0.5, 1.5),  # seconds
                'pause_between': (0.5, 2.0),
                'smoothness': 0.7,
                'common_for': ['casual_browsing', 'entertainment']
            },
            'continuous_scroll': {
                'description': 'Smooth continuous scrolling',
                'speed_range': (50, 200),
                'burst_count': (1, 1),  # Continuous
                'burst_duration': (3.0, 10.0),
                'pause_between': (0.0, 0.0),
                'smoothness': 0.9,
                'common_for': ['focused_watching', 'research_mode']
            },
            'idle_scroll': {
                'description': 'Slow, idle scrolling',
                'speed_range': (20, 100),
                'burst_count': (1, 3),
                'burst_duration': (1.0, 3.0),
                'pause_between': (1.0, 3.0),
                'smoothness': 0.8,
                'common_for': ['multitasking', 'casual_browsing']
            },
            'reading_scroll': {
                'description': 'Scrolling with reading pauses',
                'speed_range': (30, 150),
                'burst_count': (1, 2),
                'burst_duration': (2.0, 5.0),
                'pause_between': (2.0, 5.0),
                'smoothness': 0.85,
                'common_for': ['research_mode', 'focused_watching']
            }
        }
    
    def _load_attention_models(self) -> Dict[str, List[float]]:
        """Load attention span models"""
        return {
            'short_attention': [1.0, 0.8, 0.6, 0.4, 0.3, 0.2, 0.1],  # Quick drop-off
            'medium_attention': [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3],  # Gradual drop
            'long_attention': [1.0, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7, 0.65, 0.6],  # Slow drop
            'spikey_attention': [1.0, 0.7, 0.9, 0.5, 0.8, 0.4, 0.7],  # Variable attention
            'sustained_attention': [1.0, 0.98, 0.96, 0.94, 0.92, 0.90, 0.88]  # Very sustained
        }
    
    def select_behavior_pattern(self, context: Dict = None) -> BehaviorPattern:
        """Select appropriate behavior pattern based on context"""
        
        if context:
            # Context-based selection
            time_of_day = context.get('time_of_day', 'afternoon')
            content_type = context.get('content_type', 'entertainment')
            device_type = context.get('device_type', 'desktop')
            
            # Score each pattern
            pattern_scores = {}
            for pattern, model in self.behavior_models.items():
                score = 0
                
                # Time of day match
                if time_of_day in model['preferred_times']:
                    score += 2
                
                # Content type match
                if content_type in model['content_preferences']:
                    score += 3
                
                # Device bias
                device_bias = model['device_bias'].get(device_type, 0)
                score += device_bias * 2
                
                pattern_scores[pattern] = score
            
            # Select highest scoring pattern
            selected = max(pattern_scores.items(), key=lambda x: x[1])[0]
            
        else:
            # Random selection with weights
            patterns = list(BehaviorPattern)
            weights = [0.3, 0.2, 0.2, 0.15, 0.15]  # Casual browsing is most common
            selected = random.choices(patterns, weights=weights, k=1)[0]
        
        self.pattern_usage[selected.value] += 1
        return selected
    
    def generate_mouse_trajectory(self, start_x: int, start_y: int, 
                                  end_x: int, end_y: int, 
                                  pattern_type: str = 'natural') -> List[MouseAction]:
        """Generate mouse trajectory based on pattern"""
        
        pattern = self.mouse_patterns.get(pattern_type, self.mouse_patterns['natural'])
        
        actions = []
        current_x, current_y = start_x, start_y
        current_time = time.time()
        
        # Calculate total distance
        dx = end_x - start_x
        dy = end_y - start_y
        distance = math.sqrt(dx**2 + dy**2)
        
        # Determine number of points (more points for longer distances)
        num_points = max(10, min(50, int(distance / 10)))
        
        # Generate control points for Bezier curve
        if pattern_type == 'straight':
            # Straight line with slight variation
            control_x = start_x + dx * 0.5
            control_y = start_y + dy * 0.5
            control_points = [(control_x, control_y)]
        elif pattern_type == 'exploratory':
            # Curved, exploratory path
            control_x1 = start_x + dx * 0.3 + random.randint(-50, 50)
            control_y1 = start_y + dy * 0.3 + random.randint(-50, 50)
            control_x2 = start_x + dx * 0.7 + random.randint(-50, 50)
            control_y2 = start_y + dy * 0.7 + random.randint(-50, 50)
            control_points = [(control_x1, control_y1), (control_x2, control_y2)]
        elif pattern_type == 'hesitant':
            # Slow, hesitant path with more control points
            control_points = []
            for i in range(1, 4):
                t = i / 4
                cx = start_x + dx * t + random.randint(-30, 30)
                cy = start_y + dy * t + random.randint(-30, 30)
                control_points.append((cx, cy))
        else:  # natural or rapid
            # Natural path with one control point
            control_x = start_x + dx * random.uniform(0.3, 0.7)
            control_y = start_y + dy * random.uniform(0.3, 0.7)
            control_points = [(control_x, control_y)]
        
        # Generate points along the curve
        for i in range(num_points):
            t = i / (num_points - 1)
            
            # Calculate position on Bezier curve
            if len(control_points) == 1:
                # Quadratic Bezier
                cx, cy = control_points[0]
                x = (1-t)**2 * start_x + 2*(1-t)*t * cx + t**2 * end_x
                y = (1-t)**2 * start_y + 2*(1-t)*t * cy + t**2 * end_y
            elif len(control_points) == 2:
                # Cubic Bezier
                cx1, cy1 = control_points[0]
                cx2, cy2 = control_points[1]
                x = (1-t)**3 * start_x + 3*(1-t)**2*t * cx1 + 3*(1-t)*t**2 * cx2 + t**3 * end_x
                y = (1-t)**3 * start_y + 3*(1-t)**2*t * cy1 + 3*(1-t)*t**2 * cy2 + t**3 * end_y
            else:
                # Multiple control points (de Casteljau's algorithm)
                points = [(start_x, start_y)] + list(control_points) + [(end_x, end_y)]
                for r in range(1, len(points)):
                    for i in range(len(points) - r):
                        px, py = points[i]
                        qx, qy = points[i + 1]
                        points[i] = ((1-t) * px + t * qx, (1-t) * py + t * qy)
                x, y = points[0]
            
            # Add micro-movements
            if random.random() > 0.7:
                x += random.randint(-2, 2)
                y += random.randint(-2, 2)
            
            # Calculate speed and duration
            speed = random.uniform(*pattern['speed_range'])
            move_duration = distance / (num_points * speed) if speed > 0 else 0.01
            
            # Create action
            action = MouseAction(
                x=int(x),
                y=int(y),
                action_type='move',
                timestamp=current_time,
                duration=move_duration,
                pressure=random.uniform(0.5, 1.0) if pattern_type == 'hesitant' else 1.0
            )
            actions.append(action)
            
            current_time += move_duration
            
            # Random pauses
            if random.random() < pattern['pause_probability']:
                pause_duration = random.uniform(0.05, 0.2)
                current_time += pause_duration
        
        return actions
    
    def generate_scroll_actions(self, pattern_type: str = 'burst_scroll', 
                               total_scroll: int = 1000) -> List[ScrollAction]:
        """Generate scroll actions based on pattern"""
        
        pattern = self.scroll_patterns.get(pattern_type, self.scroll_patterns['burst_scroll'])
        actions = []
        current_time = time.time()
        remaining_scroll = total_scroll
        
        burst_count = random.randint(*pattern['burst_count'])
        scroll_per_burst = total_scroll // burst_count
        
        for burst in range(burst_count):
            # Burst duration
            burst_duration = random.uniform(*pattern['burst_duration'])
            
            # Scroll speed for this burst
            speed = random.uniform(*pattern['speed_range'])
            
            # Calculate scroll amount for this burst
            burst_scroll = min(scroll_per_burst, remaining_scroll)
            if burst_scroll <= 0:
                break
            
            # Create scroll action
            action = ScrollAction(
                direction='down' if random.random() > 0.1 else 'up',  # Mostly down
                amount=burst_scroll,
                speed=speed,
                timestamp=current_time,
                smoothness=pattern['smoothness']
            )
            actions.append(action)
            
            # Update time
            current_time += burst_duration
            remaining_scroll -= burst_scroll
            
            # Pause between bursts
            if burst < burst_count - 1 and remaining_scroll > 0:
                pause_duration = random.uniform(*pattern['pause_between'])
                current_time += pause_duration
        
        return actions
    
    def generate_attention_pattern(self, video_duration: int, 
                                  pattern_type: str = None) -> List[float]:
        """Generate attention pattern for video watching"""
        
        if not pattern_type:
            pattern_type = random.choice(list(self.attention_models.keys()))
        
        base_pattern = self.attention_models[pattern_type]
        
        # Scale pattern to video duration
        num_segments = min(video_duration // 30, len(base_pattern))
        if num_segments < 2:
            num_segments = 2
        
        scaled_pattern = []
        for i in range(num_segments):
            base_idx = min(i, len(base_pattern) - 1)
            base_value = base_pattern[base_idx]
            
            # Add variation
            if pattern_type == 'spikey_attention':
                variation = random.uniform(-0.3, 0.3)
            else:
                variation = random.uniform(-0.15, 0.15)
            
            value = max(0.1, min(1.0, base_value + variation))
            scaled_pattern.append(value)
        
        return scaled_pattern
    
    def generate_view_session(self, video_duration: int, 
                             behavior_pattern: BehaviorPattern = None) -> ViewSession:
        """Generate complete viewing session"""
        
        if not behavior_pattern:
            behavior_pattern = self.select_behavior_pattern()
        
        model = self.behavior_models[behavior_pattern]
        
        # Calculate watch time based on completion rate
        min_completion, max_completion = model['watch_completion']
        completion_rate = random.uniform(min_completion, max_completion)
        watch_time = int(video_duration * completion_rate)
        
        # Generate attention pattern
        if behavior_pattern == BehaviorPattern.FOCUSED_WATCHING:
            attention_type = 'long_attention'
        elif behavior_pattern == BehaviorPattern.MULTITASKING:
            attention_type = 'short_attention'
        else:
            attention_type = random.choice(['medium_attention', 'spikey_attention'])
        
        attention_pattern = self.generate_attention_pattern(video_duration, attention_type)
        
        # Generate engagement actions
        engagement_actions = self._generate_engagement_actions(behavior_pattern, watch_time)
        
        # Create session
        session = ViewSession(
            start_time=time.time(),
            end_time=time.time() + watch_time,
            video_duration=video_duration,
            watch_time=watch_time,
            retention_rate=completion_rate,
            engagement_actions=engagement_actions,
            attention_pattern=attention_pattern
        )
        
        self.session_history.append(session)
        return session
    
    def _generate_engagement_actions(self, behavior_pattern: BehaviorPattern, 
                                    watch_time: int) -> List[Dict]:
        """Generate engagement actions based on behavior pattern"""
        
        model = self.behavior_models[behavior_pattern]
        actions = []
        
        # Calculate number of actions based on frequency
        click_freq = random.uniform(*model['click_frequency'])
        scroll_freq = random.uniform(*model['scroll_frequency'])
        pause_freq = random.uniform(*model['pause_frequency'])
        
        num_clicks = int(watch_time * click_freq / 60)
        num_scrolls = int(watch_time * scroll_freq / 60)
        num_pauses = int(watch_time * pause_freq / 60)
        
        # Generate clicks
        for _ in range(num_clicks):
            click_time = random.uniform(10, watch_time - 10)
            actions.append({
                'type': 'click',
                'time': click_time,
                'element': random.choice(['video', 'like', 'subscribe', 'comment', 'share']),
                'duration': random.uniform(0.1, 0.5)
            })
        
        # Generate scrolls
        for _ in range(num_scrolls):
            scroll_time = random.uniform(5, watch_time - 5)
            actions.append({
                'type': 'scroll',
                'time': scroll_time,
                'direction': random.choice(['up', 'down']),
                'amount': random.randint(100, 500),
                'speed': random.uniform(50, 300)
            })
        
        # Generate pauses
        for _ in range(num_pauses):
            pause_time = random.uniform(15, watch_time - 15)
            pause_duration = random.uniform(2, 10)
            actions.append({
                'type': 'pause',
                'time': pause_time,
                'duration': pause_duration
            })
        
        # Generate quality changes (10% chance)
        if random.random() < 0.1:
            change_time = random.uniform(30, watch_time - 30)
            actions.append({
                'type': 'quality_change',
                'time': change_time,
                'from': random.choice(['360p', '480p', '720p']),
                'to': random.choice(['480p', '720p', '1080p'])
            })
        
        # Generate volume changes (30% chance)
        if random.random() < 0.3:
            num_volume_changes = random.randint(1, 3)
            for _ in range(num_volume_changes):
                change_time = random.uniform(20, watch_time - 20)
                actions.append({
                    'type': 'volume_change',
                    'time': change_time,
                    'amount': random.randint(-30, 30)
                })
        
        # Sort by time
        actions.sort(key=lambda x: x['time'])
        return actions
    
    def get_behavior_statistics(self) -> Dict[str, Any]:
        """Get behavior simulation statistics"""
        
        if not self.session_history:
            return {'total_sessions': 0, 'pattern_usage': self.pattern_usage}
        
        total_sessions = len(self.session_history)
        total_watch_time = sum(s.watch_time for s in self.session_history)
        avg_watch_time = total_watch_time / total_sessions if total_sessions > 0 else 0
        avg_retention = sum(s.retention_rate for s in self.session_history) / total_sessions
        
        return {
            'total_sessions': total_sessions,
            'total_watch_time': total_watch_time,
            'average_watch_time': avg_watch_time,
            'average_retention_rate': avg_retention,
            'pattern_usage': self.pattern_usage,
            'most_used_pattern': max(self.pattern_usage.items(), key=lambda x: x[1])[0],
            'session_timeline': [
                {
                    'start': datetime.fromtimestamp(s.start_time).strftime('%Y-%m-%d %H:%M:%S'),
                    'duration': s.watch_time,
                    'pattern': 'unknown',  # Would need to store pattern with session
                    'retention': s.retention_rate
                }
                for s in self.session_history[-10:]  # Last 10 sessions
            ]
        }
    
    def get_recommendations(self, current_session: ViewSession = None) -> List[str]:
        """Get recommendations for more natural behavior"""
        
        recommendations = []
        
        if current_session:
            # Analyze current session
            retention = current_session.retention_rate
            watch_time = current_session.watch_time
            video_duration = current_session.video_duration
            
            if retention > 0.9:
                recommendations.append("Consider adding more pauses or distractions for realism")
            
            if watch_time < video_duration * 0.2:
                recommendations.append("Watch time is very low, consider increasing engagement")
            
            if len(current_session.engagement_actions) < 3:
                recommendations.append("Add more engagement actions (clicks, scrolls, pauses)")
        
        # General recommendations based on statistics
        if self.session_history:
            avg_retention = sum(s.retention_rate for s in self.session_history) / len(self.session_history)
            
            if avg_retention > 0.8:
                recommendations.append("Overall retention is high - vary completion rates more")
            
            if self.pattern_usage[BehaviorPattern.CASUAL_BROWSING.value] / sum(self.pattern_usage.values()) > 0.5:
                recommendations.append("Using casual browsing pattern too frequently - try other patterns")
        
        return recommendations[:3]  # Return top 3 recommendations