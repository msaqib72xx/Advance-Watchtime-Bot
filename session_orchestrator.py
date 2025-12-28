#!/usr/bin/env python3
"""
Session Orchestrator
Manages multiple sessions with coordinated timing and behavior
"""

import asyncio
import random
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np

from bot_advanced import YouTubeWatchTimeBotAdvanced
from stealth_manager import StealthManager
from behavior_ai import BehaviorAISimulator, BehaviorPattern

class SessionPriority(Enum):
    """Session priority levels"""
    HIGH = "high"      # Maximum stealth, slow execution
    MEDIUM = "medium"  # Balanced stealth and speed
    LOW = "low"        # Faster execution, basic stealth
    TEST = "test"      # Quick testing mode

@dataclass
class OrchestrationPlan:
    """Session orchestration plan"""
    campaign_id: str
    video_url: str
    total_sessions: int
    priority: SessionPriority
    start_time: float
    end_time: float
    session_schedule: List[Dict]
    success_criteria: Dict
    risk_assessment: Dict

class SessionOrchestrator:
    """Orchestrates multiple sessions with intelligent scheduling"""
    
    def __init__(self, config_path: str = "config_advanced.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.bot = YouTubeWatchTimeBotAdvanced(config_path)
        self.stealth = StealthManager(config_path)
        self.behavior_ai = BehaviorAISimulator(config_path)
        
        self.active_campaigns = []
        self.completed_campaigns = []
        self.campaign_history = []
        
        # Performance metrics
        self.metrics = {
            'total_campaigns': 0,
            'successful_campaigns': 0,
            'failed_campaigns': 0,
            'total_sessions': 0,
            'total_watch_time': 0,
            'avg_success_rate': 0.0,
            'peak_concurrent_sessions': 0,
            'detection_events': 0
        }
    
    async def create_campaign_plan(self, video_url: str, num_sessions: int,
                                  priority: SessionPriority = SessionPriority.MEDIUM) -> OrchestrationPlan:
        """Create intelligent campaign plan"""
        
        campaign_id = f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Analyze video for optimal scheduling
        video_analysis = await self._analyze_video(video_url)
        
        # Determine optimal session distribution
        session_schedule = self._create_session_schedule(num_sessions, priority, video_analysis)
        
        # Calculate expected duration
        total_duration = sum(session.get('estimated_duration', 300) for session in session_schedule)
        buffer_time = total_duration * 0.2  # 20% buffer
        
        # Create success criteria
        success_criteria = self._create_success_criteria(num_sessions, priority)
        
        # Risk assessment
        risk_assessment = self._assess_campaign_risk(num_sessions, priority, video_analysis)
        
        plan = OrchestrationPlan(
            campaign_id=campaign_id,
            video_url=video_url,
            total_sessions=num_sessions,
            priority=priority,
            start_time=time.time(),
            end_time=time.time() + total_duration + buffer_time,
            session_schedule=session_schedule,
            success_criteria=success_criteria,
            risk_assessment=risk_assessment
        )
        
        return plan
    
    async def _analyze_video(self, video_url: str) -> Dict[str, Any]:
        """Analyze video for optimal viewing patterns"""
        
        # For educational purposes, we simulate video analysis
        # In production, you could extract actual video metadata
        
        video_types = ['educational', 'entertainment', 'tutorial', 'music', 'documentary']
        video_lengths = [180, 300, 600, 900, 1200]  # 3-20 minutes
        
        # Simulate analysis
        analysis = {
            'estimated_length': random.choice(video_lengths),
            'content_type': random.choice(video_types),
            'optimal_view_times': self._get_optimal_view_times(),
            'engagement_pattern': self._get_engagement_pattern(),
            'audience_demographics': self._get_audience_demographics(),
            'watch_pattern_recommendations': []
        }
        
        # Add recommendations based on content type
        if analysis['content_type'] == 'educational':
            analysis['watch_pattern_recommendations'] = [
                'Use focused_watching pattern',
                'Include frequent pauses',
                'High completion rates expected'
            ]
        elif analysis['content_type'] == 'entertainment':
            analysis['watch_pattern_recommendations'] = [
                'Use casual_browsing or entertainment pattern',
                'Variable completion rates',
                'Include engagement actions'
            ]
        
        return analysis
    
    def _get_optimal_view_times(self) -> List[Dict]:
        """Get optimal viewing times based on content type"""
        
        time_slots = [
            {'hour': 9, 'weight': 0.3, 'description': 'Morning'},
            {'hour': 12, 'weight': 0.7, 'description': 'Lunch time'},
            {'hour': 15, 'weight': 0.8, 'description': 'Afternoon'},
            {'hour': 18, 'weight': 0.9, 'description': 'Evening'},
            {'hour': 21, 'weight': 0.6, 'description': 'Night'},
            {'hour': 2, 'weight': 0.1, 'description': 'Late night'}
        ]
        
        # Adjust weights based on day of week
        day_of_week = datetime.now().weekday()
        if day_of_week >= 5:  # Weekend
            for slot in time_slots:
                if slot['hour'] in [9, 12]:
                    slot['weight'] *= 0.5  # Less morning viewing
                elif slot['hour'] in [15, 18, 21]:
                    slot['weight'] *= 1.2  # More afternoon/evening viewing
        
        return time_slots
    
    def _get_engagement_pattern(self) -> Dict[str, float]:
        """Get expected engagement pattern"""
        
        return {
            'like_probability': random.uniform(0.3, 0.7),
            'comment_probability': random.uniform(0.05, 0.2),
            'subscribe_probability': random.uniform(0.1, 0.4),
            'share_probability': random.uniform(0.02, 0.1),
            'completion_rate': random.uniform(0.4, 0.8),
            'avg_watch_time_percentage': random.uniform(0.5, 0.9)
        }
    
    def _get_audience_demographics(self) -> Dict[str, Any]:
        """Get simulated audience demographics"""
        
        demographics = {
            'age_groups': {
                '13-17': random.uniform(0.1, 0.2),
                '18-24': random.uniform(0.3, 0.4),
                '25-34': random.uniform(0.2, 0.3),
                '35-44': random.uniform(0.1, 0.2),
                '45+': random.uniform(0.05, 0.15)
            },
            'genders': {
                'male': random.uniform(0.4, 0.6),
                'female': random.uniform(0.3, 0.5),
                'other': random.uniform(0.01, 0.05)
            },
            'devices': {
                'mobile': random.uniform(0.5, 0.7),
                'desktop': random.uniform(0.2, 0.4),
                'tablet': random.uniform(0.1, 0.2),
                'tv': random.uniform(0.05, 0.1)
            },
            'locations': {
                'US': random.uniform(0.3, 0.5),
                'IN': random.uniform(0.1, 0.2),
                'GB': random.uniform(0.05, 0.1),
                'DE': random.uniform(0.03, 0.07),
                'Others': random.uniform(0.2, 0.4)
            }
        }
        
        # Normalize percentages
        for category in demographics:
            total = sum(demographics[category].values())
            if total > 0:
                for key in demographics[category]:
                    demographics[category][key] /= total
        
        return demographics
    
    def _create_session_schedule(self, num_sessions: int, priority: SessionPriority,
                                video_analysis: Dict) -> List[Dict]:
        """Create intelligent session schedule"""
        
        schedule = []
        
        # Determine timing strategy based on priority
        if priority == SessionPriority.HIGH:
            # Spread out over longer period
            min_gap = 1800  # 30 minutes
            max_gap = 7200  # 2 hours
            session_duration = random.uniform(300, 600)  # 5-10 minutes
        elif priority == SessionPriority.MEDIUM:
            # Moderate spacing
            min_gap = 900   # 15 minutes
            max_gap = 3600  # 1 hour
            session_duration = random.uniform(240, 480)  # 4-8 minutes
        elif priority == SessionPriority.LOW:
            # Faster execution
            min_gap = 300   # 5 minutes
            max_gap = 1800  # 30 minutes
            session_duration = random.uniform(180, 360)  # 3-6 minutes
        else:  # TEST
            # Very fast for testing
            min_gap = 60    # 1 minute
            max_gap = 300   # 5 minutes
            session_duration = random.uniform(120, 240)  # 2-4 minutes
        
        # Generate schedule
        current_time = time.time()
        
        for i in range(num_sessions):
            # Determine start time with jitter
            if i == 0:
                start_delay = random.uniform(60, 300)  # 1-5 minutes for first session
            else:
                start_delay = random.uniform(min_gap, max_gap)
            
            current_time += start_delay
            
            # Select behavior pattern based on video analysis
            if video_analysis['content_type'] == 'educational':
                behavior_pattern = BehaviorPattern.FOCUSED_WATCHING
            elif video_analysis['content_type'] == 'entertainment':
                behavior_pattern = random.choice([BehaviorPattern.CASUAL_BROWSING, 
                                                 BehaviorPattern.ENTERTAINMENT])
            else:
                behavior_pattern = self.behavior_ai.select_behavior_pattern()
            
            # Create session configuration
            session_config = {
                'session_number': i + 1,
                'scheduled_start': current_time,
                'estimated_duration': session_duration,
                'behavior_pattern': behavior_pattern.value,
                'viewer_profile': self._generate_viewer_profile(video_analysis),
                'stealth_level': self._get_stealth_level(priority),
                'network_config': self._get_network_config(priority),
                'engagement_goals': self._get_engagement_goals(behavior_pattern),
                'retention_target': random.uniform(0.4, 0.8)
            }
            
            schedule.append(session_config)
            
            # Add some variability to next session duration
            session_duration *= random.uniform(0.8, 1.2)
        
        return schedule
    
    def _generate_viewer_profile(self, video_analysis: Dict) -> Dict[str, Any]:
        """Generate viewer profile based on audience demographics"""
        
        demographics = video_analysis['audience_demographics']
        
        # Select age group based on probabilities
        age_groups = list(demographics['age_groups'].keys())
        age_probs = list(demographics['age_groups'].values())
        age_group = np.random.choice(age_groups, p=age_probs)
        
        # Select gender
        genders = list(demographics['genders'].keys())
        gender_probs = list(demographics['genders'].values())
        gender = np.random.choice(genders, p=gender_probs)
        
        # Select device
        devices = list(demographics['devices'].keys())
        device_probs = list(demographics['devices'].values())
        device = np.random.choice(devices, p=device_probs)
        
        # Select location
        locations = list(demographics['locations'].keys())
        location_probs = list(demographics['locations'].values())
        location = np.random.choice(locations, p=location_probs)
        
        return {
            'age_group': age_group,
            'gender': gender,
            'device': device,
            'location': location,
            'viewer_type': random.choice(['new_viewer', 'returning_viewer', 'subscriber']),
            'interests': self._generate_interests(video_analysis['content_type']),
            'watch_history': random.randint(10, 1000),
            'subscription_count': random.randint(0, 50)
        }
    
    def _generate_interests(self, content_type: str) -> List[str]:
        """Generate interests based on content type"""
        
        interest_categories = {
            'educational': ['Learning', 'Technology', 'Science', 'History', 'Documentaries'],
            'entertainment': ['Comedy', 'Music', 'Movies', 'Gaming', 'Vlogs'],
            'tutorial': ['How-to', 'DIY', 'Cooking', 'Fitness', 'Programming'],
            'music': ['Pop', 'Rock', 'Hip Hop', 'Classical', 'Electronic'],
            'documentary': ['Nature', 'History', 'Science', 'Travel', 'Culture']
        }
        
        base_interests = interest_categories.get(content_type, interest_categories['entertainment'])
        
        # Select 3-5 interests
        num_interests = random.randint(3, 5)
        interests = random.sample(base_interests, min(num_interests, len(base_interests)))
        
        # Add some random interests
        all_interests = []
        for category in interest_categories.values():
            all_interests.extend(category)
        
        additional = random.sample(all_interests, random.randint(1, 2))
        interests.extend(additional)
        
        return list(set(interests))  # Remove duplicates
    
    def _get_stealth_level(self, priority: SessionPriority) -> Dict[str, Any]:
        """Get stealth configuration based on priority"""
        
        if priority == SessionPriority.HIGH:
            return {
                'fingerprint_rotation': True,
                'proxy_rotation': True,
                'behavior_randomization': True,
                'network_randomization': True,
                'timing_randomization': True,
                'mouse_movement_simulation': True,
                'scroll_behavior_simulation': True,
                'max_concurrent_sessions': 1,
                'min_session_gap': 1800,  # 30 minutes
                'geo_diversity': True
            }
        elif priority == SessionPriority.MEDIUM:
            return {
                'fingerprint_rotation': True,
                'proxy_rotation': True,
                'behavior_randomization': True,
                'network_randomization': False,
                'timing_randomization': True,
                'mouse_movement_simulation': True,
                'scroll_behavior_simulation': False,
                'max_concurrent_sessions': 2,
                'min_session_gap': 900,  # 15 minutes
                'geo_diversity': False
            }
        elif priority == SessionPriority.LOW:
            return {
                'fingerprint_rotation': False,
                'proxy_rotation': False,
                'behavior_randomization': True,
                'network_randomization': False,
                'timing_randomization': False,
                'mouse_movement_simulation': False,
                'scroll_behavior_simulation': False,
                'max_concurrent_sessions': 3,
                'min_session_gap': 300,  # 5 minutes
                'geo_diversity': False
            }
        else:  # TEST
            return {
                'fingerprint_rotation': False,
                'proxy_rotation': False,
                'behavior_randomization': False,
                'network_randomization': False,
                'timing_randomization': False,
                'mouse_movement_simulation': False,
                'scroll_behavior_simulation': False,
                'max_concurrent_sessions': 5,
                'min_session_gap': 60,  # 1 minute
                'geo_diversity': False
            }
    
    def _get_network_config(self, priority: SessionPriority) -> Dict[str, Any]:
        """Get network configuration based on priority"""
        
        if priority == SessionPriority.HIGH:
            return {
                'use_proxy': True,
                'proxy_type': 'residential',
                'bandwidth_simulation': True,
                'latency_simulation': True,
                'packet_loss_simulation': True,
                'dns_simulation': True,
                'isp_rotation': True,
                'geo_ip_rotation': True
            }
        elif priority == SessionPriority.MEDIUM:
            return {
                'use_proxy': True,
                'proxy_type': 'mixed',
                'bandwidth_simulation': True,
                'latency_simulation': False,
                'packet_loss_simulation': False,
                'dns_simulation': False,
                'isp_rotation': False,
                'geo_ip_rotation': False
            }
        else:
            return {
                'use_proxy': False,
                'proxy_type': 'none',
                'bandwidth_simulation': False,
                'latency_simulation': False,
                'packet_loss_simulation': False,
                'dns_simulation': False,
                'isp_rotation': False,
                'geo_ip_rotation': False
            }
    
    def _get_engagement_goals(self, behavior_pattern: BehaviorPattern) -> Dict[str, float]:
        """Get engagement goals based on behavior pattern"""
        
        if behavior_pattern == BehaviorPattern.FOCUSED_WATCHING:
            return {
                'min_watch_percentage': 0.7,
                'max_watch_percentage': 0.95,
                'like_probability': 0.7,
                'comment_probability': 0.2,
                'subscribe_probability': 0.4,
                'share_probability': 0.1
            }
        elif behavior_pattern == BehaviorPattern.CASUAL_BROWSING:
            return {
                'min_watch_percentage': 0.3,
                'max_watch_percentage': 0.7,
                'like_probability': 0.3,
                'comment_probability': 0.05,
                'subscribe_probability': 0.1,
                'share_probability': 0.02
            }
        elif behavior_pattern == BehaviorPattern.MULTITASKING:
            return {
                'min_watch_percentage': 0.2,
                'max_watch_percentage': 0.5,
                'like_probability': 0.1,
                'comment_probability': 0.01,
                'subscribe_probability': 0.02,
                'share_probability': 0.005
            }
        else:
            return {
                'min_watch_percentage': 0.4,
                'max_watch_percentage': 0.8,
                'like_probability': 0.5,
                'comment_probability': 0.1,
                'subscribe_probability': 0.2,
                'share_probability': 0.05
            }
    
    def _create_success_criteria(self, num_sessions: int, priority: SessionPriority) -> Dict[str, Any]:
        """Create success criteria for campaign"""
        
        if priority == SessionPriority.HIGH:
            min_success_rate = 0.9
            min_avg_watch = 0.7
            max_detection_risk = 0.1
        elif priority == SessionPriority.MEDIUM:
            min_success_rate = 0.8
            min_avg_watch = 0.6
            max_detection_risk = 0.2
        elif priority == SessionPriority.LOW:
            min_success_rate = 0.7
            min_avg_watch = 0.5
            max_detection_risk = 0.3
        else:  # TEST
            min_success_rate = 0.6
            min_avg_watch = 0.4
            max_detection_risk = 0.4
        
        return {
            'min_successful_sessions': int(num_sessions * min_success_rate),
            'min_success_rate': min_success_rate,
            'min_average_watch_percentage': min_avg_watch,
            'max_detection_risk': max_detection_risk,
            'max_consecutive_failures': 2,
            'max_total_duration': 86400,  # 24 hours
            'quality_metrics': {
                'fingerprint_diversity': 0.8,
                'behavior_variance': 0.7,
                'timing_naturalness': 0.9,
                'network_realism': 0.6 if priority == SessionPriority.HIGH else 0.3
            }
        }
    
    def _assess_campaign_risk(self, num_sessions: int, priority: SessionPriority,
                             video_analysis: Dict) -> Dict[str, Any]:
        """Assess campaign risk"""
        
        base_risk = {
            'low': 0.1,
            'medium': 0.3,
            'high': 0.6,
            'test': 0.8
        }
        
        risk_level = base_risk[priority.value]
        
        # Adjust based on number of sessions
        if num_sessions > 10:
            risk_level *= 1.5
        elif num_sessions > 5:
            risk_level *= 1.2
        
        # Adjust based on content type
        if video_analysis['content_type'] in ['educational', 'documentary']:
            risk_level *= 0.8  # Lower risk for educational content
        elif video_analysis['content_type'] == 'entertainment':
            risk_level *= 1.1  # Higher risk for entertainment
        
        risk_assessment = {
            'overall_risk': min(0.95, risk_level),
            'detection_risk': risk_level * 0.8,
            'technical_risk': risk_level * 0.4,
            'timing_risk': risk_level * 0.6,
            'behavioral_risk': risk_level * 0.7,
            'network_risk': risk_level * 0.5,
            'mitigation_strategies': self._get_mitigation_strategies(priority, risk_level),
            'risk_factors': [
                f"{num_sessions} sessions in campaign",
                f"Priority level: {priority.value}",
                f"Content type: {video_analysis['content_type']}",
                f"Estimated video length: {video_analysis['estimated_length']}s"
            ]
        }
        
        return risk_assessment
    
    def _get_mitigation_strategies(self, priority: SessionPriority, risk_level: float) -> List[str]:
        """Get risk mitigation strategies"""
        
        strategies = []
        
        if risk_level > 0.7:
            strategies.append("Consider reducing number of sessions")
            strategies.append("Increase time between sessions")
            strategies.append("Use maximum stealth settings")
        
        if risk_level > 0.5:
            strategies.append("Rotate fingerprints between sessions")
            strategies.append("Use residential proxies")
            strategies.append("Vary behavior patterns significantly")
        
        if priority != SessionPriority.HIGH:
            strategies.append("Consider upgrading to HIGH priority for better stealth")
        
        strategies.append("Monitor session success rates closely")
        strategies.append("Have fallback configurations ready")
        
        return strategies[:5]  # Return top 5 strategies
    
    async def execute_campaign(self, plan: OrchestrationPlan) -> Dict[str, Any]:
        """Execute campaign according to plan"""
        
        print(f"\n🎬 EXECUTING CAMPAIGN: {plan.campaign_id}")
        print(f"   Priority: {plan.priority.value}")
        print(f"   Sessions: {plan.total_sessions}")
        print(f"   Estimated duration: {(plan.end_time - plan.start_time)/3600:.1f} hours")
        print(f"{'='*60}")
        
        campaign_data = {
            'campaign_id': plan.campaign_id,
            'plan': plan,
            'start_time': time.time(),
            'end_time': None,
            'sessions': [],
            'results': {},
            'status': 'running'
        }
        
        self.active_campaigns.append(campaign_data)
        self.metrics['total_campaigns'] += 1
        
        successful_sessions = 0
        failed_sessions = 0
        total_watch_time = 0
        detection_events = 0
        
        try:
            for i, session_config in enumerate(plan.session_schedule):
                session_num = i + 1
                
                # Wait for scheduled start time
                current_time = time.time()
                scheduled_start = session_config['scheduled_start']
                
                if current_time < scheduled_start:
                    wait_time = scheduled_start - current_time
                    print(f"⏱️  Session {session_num}/{plan.total_sessions} starts in {wait_time:.0f}s...")
                    await asyncio.sleep(wait_time)
                
                # Update concurrent session count
                concurrent_sessions = len([s for s in self.active_campaigns 
                                         if s['status'] == 'running'])
                self.metrics['peak_concurrent_sessions'] = max(
                    self.metrics['peak_concurrent_sessions'], concurrent_sessions
                )
                
                # Execute session
                print(f"\n📅 Executing Session {session_num}/{plan.total_sessions}")
                print(f"   Pattern: {session_config['behavior_pattern']}")
                print(f"   Viewer: {session_config['viewer_profile']['age_group']} "
                      f"from {session_config['viewer_profile']['location']}")
                
                session_result = await self.bot.run_advanced_session(
                    plan.video_url, session_num
                )
                
                # Record session data
                session_data = {
                    'session_number': session_num,
                    'config': session_config,
                    'result': session_result,
                    'timestamp': time.time()
                }
                
                campaign_data['sessions'].append(session_data)
                
                # Update statistics
                if session_result.get('success'):
                    successful_sessions += 1
                    if session_result.get('watch_data'):
                        total_watch_time += session_result['watch_data']['watch_time']
                    print(f"   ✅ Session successful")
                else:
                    failed_sessions += 1
                    detection_events += 1
                    print(f"   ❌ Session failed: {session_result.get('error', 'Unknown')}")
                
                # Check for emergency stop conditions
                if self._should_stop_campaign(campaign_data, plan.success_criteria):
                    print(f"⚠️  Emergency stop triggered for campaign {plan.campaign_id}")
                    campaign_data['status'] = 'stopped_early'
                    break
            
            # Campaign completed
            campaign_data['end_time'] = time.time()
            campaign_data['status'] = 'completed'
            campaign_data['duration'] = campaign_data['end_time'] - campaign_data['start_time']
            
            # Calculate results
            success_rate = successful_sessions / plan.total_sessions if plan.total_sessions > 0 else 0
            avg_watch_time = total_watch_time / successful_sessions if successful_sessions > 0 else 0
            
            campaign_data['results'] = {
                'successful_sessions': successful_sessions,
                'failed_sessions': failed_sessions,
                'success_rate': success_rate,
                'total_watch_time': total_watch_time,
                'average_watch_time': avg_watch_time,
                'detection_events': detection_events,
                'met_success_criteria': self._check_success_criteria(
                    campaign_data, plan.success_criteria
                )
            }
            
            # Update metrics
            self.metrics['total_sessions'] += plan.total_sessions
            self.metrics['total_watch_time'] += total_watch_time
            
            if success_rate >= plan.success_criteria['min_success_rate']:
                self.metrics['successful_campaigns'] += 1
                campaign_result = 'success'
            else:
                self.metrics['failed_campaigns'] += 1
                campaign_result = 'failed'
            
            self.metrics['detection_events'] += detection_events
            
            # Calculate average success rate
            if self.metrics['total_campaigns'] > 0:
                self.metrics['avg_success_rate'] = (
                    self.metrics['successful_campaigns'] / self.metrics['total_campaigns']
                )
            
            # Move to completed campaigns
            self.active_campaigns.remove(campaign_data)
            self.completed_campaigns.append(campaign_data)
            self.campaign_history.append(campaign_data)
            
            # Keep only last 50 campaigns in history
            if len(self.campaign_history) > 50:
                self.campaign_history = self.campaign_history[-50:]
            
            print(f"\n{'='*60}")
            print(f"📊 CAMPAIGN COMPLETE: {campaign_result.upper()}")
            print(f"   Campaign ID: {plan.campaign_id}")
            print(f"   Duration: {campaign_data['duration']/60:.1f} minutes")
            print(f"   Success Rate: {success_rate:.1%}")
            print(f"   Total Watch Time: {total_watch_time/60:.1f} minutes")
            print(f"   Detection Events: {detection_events}")
            print(f"{'='*60}")
            
            return campaign_data
            
        except Exception as e:
            print(f"\n❌ Campaign execution failed: {e}")
            campaign_data['status'] = 'failed'
            campaign_data['error'] = str(e)
            campaign_data['end_time'] = time.time()
            
            self.active_campaigns.remove(campaign_data)
            self.completed_campaigns.append(campaign_data)
            self.metrics['failed_campaigns'] += 1
            
            return campaign_data
    
    def _should_stop_campaign(self, campaign_data: Dict, success_criteria: Dict) -> bool:
        """Check if campaign should be stopped early"""
        
        sessions = campaign_data['sessions']
        if len(sessions) < 3:
            return False
        
        # Check consecutive failures
        recent_failures = 0
        for session in reversed(sessions[-3:]):  # Check last 3 sessions
            if not session['result'].get('success', False):
                recent_failures += 1
        
        if recent_failures >= success_criteria['max_consecutive_failures']:
            return True
        
        # Check if success rate is too low
        successful = sum(1 for s in sessions if s['result'].get('success', False))
        success_rate = successful / len(sessions) if len(sessions) > 0 else 0
        
        if success_rate < success_criteria['min_success_rate'] * 0.5:  # 50% below target
            return True
        
        # Check total duration
        if campaign_data.get('start_time'):
            elapsed = time.time() - campaign_data['start_time']
            if elapsed > success_criteria['max_total_duration'] * 0.5:  # 50% of max
                # If success rate is low halfway through, consider stopping
                if success_rate < success_criteria['min_success_rate'] * 0.7:
                    return True
        
        return False
    
    def _check_success_criteria(self, campaign_data: Dict, success_criteria: Dict) -> Dict[str, bool]:
        """Check which success criteria were met"""
        
        results = campaign_data['results']
        
        return {
            'min_successful_sessions': results['successful_sessions'] >= 
                                      success_criteria['min_successful_sessions'],
            'min_success_rate': results['success_rate'] >= 
                               success_criteria['min_success_rate'],
            'min_average_watch': (results['average_watch_time'] / 300) >=  # Assuming 5min videos
                                success_criteria['min_average_watch_percentage'],
            'max_detection_risk': results['detection_events'] / campaign_data['plan'].total_sessions <=
                                 success_criteria['max_detection_risk'],
            'max_consecutive_failures': True,  # Checked during execution
            'max_total_duration': campaign_data['duration'] <= 
                                 success_criteria['max_total_duration']
        }
    
    def get_campaign_statistics(self) -> Dict[str, Any]:
        """Get campaign orchestration statistics"""
        
        return {
            **self.metrics,
            'active_campaigns': len(self.active_campaigns),
            'completed_campaigns': len(self.completed_campaigns),
            'campaign_history_size': len(self.campaign_history),
            'recent_success_rate': self._calculate_recent_success_rate(),
            'efficiency_metrics': self._calculate_efficiency_metrics(),
            'risk_profile': self._calculate_risk_profile()
        }
    
    def _calculate_recent_success_rate(self) -> float:
        """Calculate success rate for recent campaigns"""
        
        if not self.completed_campaigns:
            return 0.0
        
        recent = self.completed_campaigns[-10:]  # Last 10 campaigns
        successful = sum(1 for c in recent 
                        if c['results'].get('met_success_criteria', {}).get('min_success_rate', False))
        
        return successful / len(recent) if len(recent) > 0 else 0.0
    
    def _calculate_efficiency_metrics(self) -> Dict[str, float]:
        """Calculate efficiency metrics"""
        
        if not self.completed_campaigns:
            return {'watch_time_per_hour': 0.0, 'sessions_per_hour': 0.0, 'success_per_hour': 0.0}
        
        total_duration = sum(c.get('duration', 0) for c in self.completed_campaigns)
        total_sessions = sum(len(c['sessions']) for c in self.completed_campaigns)
        total_successful = sum(c['results'].get('successful_sessions', 0) 
                              for c in self.completed_campaigns)
        total_watch_time = sum(c['results'].get('total_watch_time', 0) 
                              for c in self.completed_campaigns)
        
        total_hours = total_duration / 3600
        
        return {
            'watch_time_per_hour': total_watch_time / total_hours if total_hours > 0 else 0.0,
            'sessions_per_hour': total_sessions / total_hours if total_hours > 0 else 0.0,
            'success_per_hour': total_successful / total_hours if total_hours > 0 else 0.0,
            'avg_campaign_duration': total_duration / len(self.completed_campaigns) 
                                   if self.completed_campaigns else 0.0
        }
    
    def _calculate_risk_profile(self) -> Dict[str, float]:
        """Calculate risk profile"""
        
        if not self.completed_campaigns:
            return {'detection_rate': 0.0, 'failure_rate': 0.0, 'risk_score': 0.0}
        
        total_sessions = sum(len(c['sessions']) for c in self.completed_campaigns)
        total_detections = sum(c['results'].get('detection_events', 0) 
                              for c in self.completed_campaigns)
        total_failures = sum(c['results'].get('failed_sessions', 0) 
                            for c in self.completed_campaigns)
        
        detection_rate = total_detections / total_sessions if total_sessions > 0 else 0.0
        failure_rate = total_failures / total_sessions if total_sessions > 0 else 0.0
        
        return {
            'detection_rate': detection_rate,
            'failure_rate': failure_rate,
            'risk_score': min(1.0, detection_rate * 0.7 + failure_rate * 0.3),
            'risk_level': 'high' if detection_rate > 0.3 else 
                         'medium' if detection_rate > 0.1 else 'low'
        }
    
    async def run_campaign(self, video_url: str, num_sessions: int = 3,
                          priority: SessionPriority = SessionPriority.MEDIUM) -> Dict[str, Any]:
        """Convenience method to run a campaign"""
        
        plan = await self.create_campaign_plan(video_url, num_sessions, priority)
        return await self.execute_campaign(plan)