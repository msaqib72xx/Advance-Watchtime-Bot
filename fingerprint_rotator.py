#!/usr/bin/env python3
"""
Advanced Fingerprint Rotator
Generates and rotates browser fingerprints to avoid detection
"""

import random
import json
import time
import hashlib
import platform
import psutil
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np

class FingerprintType(Enum):
    """Types of browser fingerprints"""
    DESKTOP_CHROME = "desktop_chrome"
    DESKTOP_FIREFOX = "desktop_firefox"
    DESKTOP_SAFARI = "desktop_safari"
    MOBILE_CHROME = "mobile_chrome"
    MOBILE_SAFARI = "mobile_safari"
    TABLET_CHROME = "tablet_chrome"
    LINUX_FIREFOX = "linux_firefox"
    EDGE = "edge"

@dataclass
class FingerprintConfig:
    """Complete fingerprint configuration"""
    # Browser identification
    user_agent: str
    browser_name: str
    browser_version: str
    browser_engine: str
    browser_language: str
    
    # Platform information
    platform: str
    platform_version: str
    architecture: str
    device_type: str
    
    # Hardware information
    hardware_concurrency: int
    device_memory: int
    max_touch_points: int
    cpu_cores: int
    cpu_brand: str
    gpu_vendor: str
    gpu_renderer: str
    
    # Screen properties
    screen_width: int
    screen_height: int
    color_depth: int
    pixel_ratio: float
    screen_orientation: Dict[str, Any]
    
    # Time and locale
    timezone: str
    timezone_offset: int
    locale: str
    languages: List[str]
    
    # Web capabilities
    webgl_vendor: str
    webgl_renderer: str
    webgl_version: str
    webgl_extensions: List[str]
    canvas_hash: str
    audio_hash: str
    
    # Font information
    fonts: List[str]
    font_hash: str
    
    # Plugin information
    plugins: List[str]
    mime_types: List[str]
    
    # Network information
    connection_type: str
    effective_type: str
    downlink: float
    rtt: int
    
    # Browser features
    cookie_enabled: bool
    do_not_track: str
    java_enabled: bool
    pdf_viewer_enabled: bool
    flash_enabled: bool
    
    # Additional properties
    session_id: str
    fingerprint_hash: str
    created_at: float
    expires_at: float
    
    # Security properties
    webdriver: bool = False
    chrome: bool = False
    permissions: Dict[str, str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    def get_browser_context(self) -> Dict[str, Any]:
        """Get context for Playwright browser"""
        return {
            'user_agent': self.user_agent,
            'viewport': {
                'width': self.screen_width,
                'height': self.screen_height
            },
            'screen': {
                'width': self.screen_width,
                'height': self.screen_height
            },
            'device_scale_factor': self.pixel_ratio,
            'is_mobile': self.device_type in ['mobile', 'tablet'],
            'has_touch': self.max_touch_points > 0,
            'locale': self.locale,
            'timezone_id': self.timezone,
            'permissions': self.permissions or {}
        }

class FingerprintRotator:
    """Advanced fingerprint rotation system"""
    
    def __init__(self, config_path: str = "config_advanced.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.fingerprint_history: List[FingerprintConfig] = []
        self.current_fingerprint: Optional[FingerprintConfig] = None
        self.rotation_counter = 0
        
        # Load fingerprint templates
        self.templates = self._load_fingerprint_templates()
        
        # Load real-world data
        self.hardware_profiles = self._load_hardware_profiles()
        self.locale_data = self._load_locale_data()
        self.timezone_data = self._load_timezone_data()
        
        # Statistics
        self.stats = {
            'fingerprints_generated': 0,
            'rotations_performed': 0,
            'unique_configs': 0,
            'detection_attempts': 0,
            'successful_rotations': 0
        }
    
    def _load_fingerprint_templates(self) -> Dict[FingerprintType, Dict]:
        """Load fingerprint templates for different browser types"""
        
        return {
            FingerprintType.DESKTOP_CHROME: {
                'description': 'Chrome on Windows/Mac',
                'browser_name': 'Chrome',
                'browser_engine': 'Blink',
                'device_type': 'desktop',
                'common_resolutions': [
                    (1920, 1080), (1366, 768), (1536, 864),
                    (1440, 900), (1280, 720), (2560, 1440)
                ],
                'common_platforms': ['Win32', 'Win64', 'MacIntel'],
                'webgl_vendors': ['Google Inc.', 'Intel Inc.', 'NVIDIA Corporation', 'AMD'],
                'font_sets': 'windows'  # or 'mac'
            },
            FingerprintType.DESKTOP_FIREFOX: {
                'description': 'Firefox on Windows/Mac/Linux',
                'browser_name': 'Firefox',
                'browser_engine': 'Gecko',
                'device_type': 'desktop',
                'common_resolutions': [
                    (1920, 1080), (1366, 768), (1600, 900),
                    (1280, 720), (1440, 900), (2560, 1440)
                ],
                'common_platforms': ['Win32', 'Win64', 'MacIntel', 'Linux x86_64'],
                'webgl_vendors': ['Mozilla', 'Intel Inc.', 'NVIDIA Corporation', 'AMD'],
                'font_sets': 'mixed'
            },
            FingerprintType.DESKTOP_SAFARI: {
                'description': 'Safari on Mac',
                'browser_name': 'Safari',
                'browser_engine': 'WebKit',
                'device_type': 'desktop',
                'common_resolutions': [
                    (1440, 900), (1680, 1050), (1920, 1080),
                    (2560, 1600), (2880, 1800)
                ],
                'common_platforms': ['MacIntel'],
                'webgl_vendors': ['Apple Inc.', 'Intel Inc.'],
                'font_sets': 'mac'
            },
            FingerprintType.MOBILE_CHROME: {
                'description': 'Chrome on Android',
                'browser_name': 'Chrome',
                'browser_engine': 'Blink',
                'device_type': 'mobile',
                'common_resolutions': [
                    (360, 640), (375, 667), (414, 896),
                    (360, 740), (393, 851), (412, 915)
                ],
                'common_platforms': ['Linux armv8l', 'Linux aarch64'],
                'webgl_vendors': ['Google Inc.', 'Qualcomm', 'ARM'],
                'font_sets': 'android'
            },
            FingerprintType.MOBILE_SAFARI: {
                'description': 'Safari on iPhone',
                'browser_name': 'Safari',
                'browser_engine': 'WebKit',
                'device_type': 'mobile',
                'common_resolutions': [
                    (375, 667), (414, 896), (390, 844),
                    (428, 926), (393, 852)
                ],
                'common_platforms': ['iPhone'],
                'webgl_vendors': ['Apple Inc.'],
                'font_sets': 'ios'
            },
            FingerprintType.TABLET_CHROME: {
                'description': 'Chrome on Tablet',
                'browser_name': 'Chrome',
                'browser_engine': 'Blink',
                'device_type': 'tablet',
                'common_resolutions': [
                    (768, 1024), (800, 1280), (1024, 1366),
                    (1200, 1920), (1536, 2048)
                ],
                'common_platforms': ['Linux armv8l', 'Linux aarch64'],
                'webgl_vendors': ['Google Inc.', 'Qualcomm', 'ARM'],
                'font_sets': 'android'
            },
            FingerprintType.LINUX_FIREFOX: {
                'description': 'Firefox on Linux',
                'browser_name': 'Firefox',
                'browser_engine': 'Gecko',
                'device_type': 'desktop',
                'common_resolutions': [
                    (1920, 1080), (1366, 768), (1600, 900),
                    (1280, 720), (2560, 1440)
                ],
                'common_platforms': ['Linux x86_64'],
                'webgl_vendors': ['Mozilla', 'Intel Inc.', 'NVIDIA Corporation', 'AMD'],
                'font_sets': 'linux'
            },
            FingerprintType.EDGE: {
                'description': 'Microsoft Edge',
                'browser_name': 'Edg',  # Edge reports as Edg
                'browser_engine': 'Blink',
                'device_type': 'desktop',
                'common_resolutions': [
                    (1920, 1080), (1366, 768), (1536, 864),
                    (1440, 900), (1280, 720), (2560, 1440)
                ],
                'common_platforms': ['Win32', 'Win64'],
                'webgl_vendors': ['Google Inc.', 'Intel Inc.', 'NVIDIA Corporation', 'AMD'],
                'font_sets': 'windows'
            }
        }
    
    def _load_hardware_profiles(self) -> Dict[str, Dict]:
        """Load realistic hardware profiles"""
        
        return {
            'desktop_high_end': {
                'cpu_cores': 8,
                'device_memory': 16,
                'hardware_concurrency': 8,
                'cpu_brand': 'Intel(R) Core(TM) i7-12700K',
                'gpu_vendor': 'NVIDIA Corporation',
                'gpu_renderer': 'NVIDIA GeForce RTX 3060'
            },
            'desktop_mid_end': {
                'cpu_cores': 6,
                'device_memory': 8,
                'hardware_concurrency': 6,
                'cpu_brand': 'Intel(R) Core(TM) i5-12400',
                'gpu_vendor': 'Intel Inc.',
                'gpu_renderer': 'Intel(R) UHD Graphics 730'
            },
            'desktop_low_end': {
                'cpu_cores': 4,
                'device_memory': 4,
                'hardware_concurrency': 4,
                'cpu_brand': 'Intel(R) Core(TM) i3-10100',
                'gpu_vendor': 'Intel Inc.',
                'gpu_renderer': 'Intel(R) UHD Graphics 630'
            },
            'laptop': {
                'cpu_cores': 4,
                'device_memory': 8,
                'hardware_concurrency': 4,
                'cpu_brand': 'Intel(R) Core(TM) i5-1135G7',
                'gpu_vendor': 'Intel Inc.',
                'gpu_renderer': 'Intel(R) Iris(R) Xe Graphics'
            },
            'mobile_high_end': {
                'cpu_cores': 8,
                'device_memory': 8,
                'hardware_concurrency': 8,
                'cpu_brand': 'Snapdragon 888',
                'gpu_vendor': 'Qualcomm',
                'gpu_renderer': 'Adreno 660'
            },
            'mobile_mid_end': {
                'cpu_cores': 6,
                'device_memory': 6,
                'hardware_concurrency': 6,
                'cpu_brand': 'Snapdragon 765G',
                'gpu_vendor': 'Qualcomm',
                'gpu_renderer': 'Adreno 620'
            },
            'mobile_low_end': {
                'cpu_cores': 4,
                'device_memory': 4,
                'hardware_concurrency': 4,
                'cpu_brand': 'Snapdragon 460',
                'gpu_vendor': 'Qualcomm',
                'gpu_renderer': 'Adreno 610'
            },
            'tablet': {
                'cpu_cores': 6,
                'device_memory': 6,
                'hardware_concurrency': 6,
                'cpu_brand': 'Apple A14 Bionic',
                'gpu_vendor': 'Apple Inc.',
                'gpu_renderer': 'Apple GPU'
            }
        }
    
    def _load_locale_data(self) -> Dict[str, Dict]:
        """Load locale and language data"""
        
        return {
            'en-US': {
                'locale': 'en-US',
                'languages': ['en-US', 'en'],
                'timezone': 'America/New_York',
                'timezone_offset': -5,
                'region': 'US'
            },
            'en-GB': {
                'locale': 'en-GB',
                'languages': ['en-GB', 'en'],
                'timezone': 'Europe/London',
                'timezone_offset': 0,
                'region': 'GB'
            },
            'en-IN': {
                'locale': 'en-IN',
                'languages': ['en-IN', 'en', 'hi'],
                'timezone': 'Asia/Kolkata',
                'timezone_offset': 5.5,
                'region': 'IN'
            },
            'de-DE': {
                'locale': 'de-DE',
                'languages': ['de-DE', 'de', 'en'],
                'timezone': 'Europe/Berlin',
                'timezone_offset': 1,
                'region': 'DE'
            },
            'fr-FR': {
                'locale': 'fr-FR',
                'languages': ['fr-FR', 'fr', 'en'],
                'timezone': 'Europe/Paris',
                'timezone_offset': 1,
                'region': 'FR'
            },
            'ja-JP': {
                'locale': 'ja-JP',
                'languages': ['ja-JP', 'ja'],
                'timezone': 'Asia/Tokyo',
                'timezone_offset': 9,
                'region': 'JP'
            },
            'es-ES': {
                'locale': 'es-ES',
                'languages': ['es-ES', 'es'],
                'timezone': 'Europe/Madrid',
                'timezone_offset': 1,
                'region': 'ES'
            }
        }
    
    def _load_timezone_data(self) -> Dict[str, Dict]:
        """Load timezone data"""
        
        return {
            'America/New_York': {'offset': -5, 'region': 'US'},
            'America/Chicago': {'offset': -6, 'region': 'US'},
            'America/Denver': {'offset': -7, 'region': 'US'},
            'America/Los_Angeles': {'offset': -8, 'region': 'US'},
            'Europe/London': {'offset': 0, 'region': 'GB'},
            'Europe/Paris': {'offset': 1, 'region': 'FR'},
            'Europe/Berlin': {'offset': 1, 'region': 'DE'},
            'Asia/Kolkata': {'offset': 5.5, 'region': 'IN'},
            'Asia/Tokyo': {'offset': 9, 'region': 'JP'},
            'Asia/Shanghai': {'offset': 8, 'region': 'CN'},
            'Australia/Sydney': {'offset': 10, 'region': 'AU'}
        }
    
    def generate_fingerprint(self, 
                           fingerprint_type: Optional[FingerprintType] = None,
                           hardware_profile: Optional[str] = None) -> FingerprintConfig:
        """Generate a new browser fingerprint"""
        
        # Select fingerprint type if not specified
        if not fingerprint_type:
            fingerprint_type = self._select_fingerprint_type()
        
        # Get template
        template = self.templates[fingerprint_type]
        
        # Select hardware profile
        if not hardware_profile:
            hardware_profile = self._select_hardware_profile(fingerprint_type)
        
        hardware = self.hardware_profiles[hardware_profile]
        
        # Generate screen resolution
        screen_width, screen_height = random.choice(template['common_resolutions'])
        
        # Generate user agent
        user_agent = self._generate_user_agent(fingerprint_type)
        
        # Select locale
        locale_config = self._select_locale(fingerprint_type)
        
        # Generate WebGL information
        webgl_vendor = random.choice(template['webgl_vendors'])
        webgl_renderer = self._generate_webgl_renderer(webgl_vendor, fingerprint_type)
        
        # Generate fonts
        fonts = self._generate_font_list(template['font_sets'])
        
        # Generate plugin list
        plugins = self._generate_plugins(fingerprint_type)
        
        # Generate connection information
        connection_info = self._generate_connection_info()
        
        # Create fingerprint
        fingerprint = FingerprintConfig(
            # Browser identification
            user_agent=user_agent,
            browser_name=template['browser_name'],
            browser_version=self._extract_version_from_ua(user_agent),
            browser_engine=template['browser_engine'],
            browser_language=locale_config['locale'],
            
            # Platform information
            platform=random.choice(template['common_platforms']),
            platform_version=self._generate_platform_version(fingerprint_type),
            architecture=self._get_architecture(fingerprint_type),
            device_type=template['device_type'],
            
            # Hardware information
            hardware_concurrency=hardware['hardware_concurrency'],
            device_memory=hardware['device_memory'],
            max_touch_points=3 if template['device_type'] in ['mobile', 'tablet'] else 0,
            cpu_cores=hardware['cpu_cores'],
            cpu_brand=hardware['cpu_brand'],
            gpu_vendor=hardware['gpu_vendor'],
            gpu_renderer=hardware['gpu_renderer'],
            
            # Screen properties
            screen_width=screen_width,
            screen_height=screen_height,
            color_depth=24,
            pixel_ratio=round(random.uniform(1.0, 2.5), 2),
            screen_orientation={
                'type': 'landscape-primary' if screen_width > screen_height else 'portrait-primary',
                'angle': 0
            },
            
            # Time and locale
            timezone=locale_config['timezone'],
            timezone_offset=locale_config['timezone_offset'],
            locale=locale_config['locale'],
            languages=locale_config['languages'],
            
            # Web capabilities
            webgl_vendor=webgl_vendor,
            webgl_renderer=webgl_renderer,
            webgl_version='WebGL 2.0',
            webgl_extensions=self._generate_webgl_extensions(),
            canvas_hash=self._generate_canvas_hash(),
            audio_hash=self._generate_audio_hash(),
            
            # Font information
            fonts=fonts,
            font_hash=hashlib.md5(','.join(sorted(fonts)).encode()).hexdigest(),
            
            # Plugin information
            plugins=plugins,
            mime_types=self._generate_mime_types(plugins),
            
            # Network information
            connection_type=connection_info['type'],
            effective_type=connection_info['effective_type'],
            downlink=connection_info['downlink'],
            rtt=connection_info['rtt'],
            
            # Browser features
            cookie_enabled=True,
            do_not_track=random.choice(['1', '0', 'unspecified']),
            java_enabled=False,
            pdf_viewer_enabled=True,
            flash_enabled=False,
            
            # Additional properties
            session_id=f"fp_{int(time.time())}_{random.randint(1000, 9999)}",
            fingerprint_hash=self._calculate_fingerprint_hash(),
            created_at=time.time(),
            expires_at=time.time() + 3600,  # 1 hour validity
            
            # Security properties
            webdriver=False,
            chrome=(fingerprint_type in [FingerprintType.DESKTOP_CHROME, 
                                        FingerprintType.MOBILE_CHROME, 
                                        FingerprintType.TABLET_CHROME,
                                        FingerprintType.EDGE]),
            permissions=self._generate_permissions()
        )
        
        self.current_fingerprint = fingerprint
        self.fingerprint_history.append(fingerprint)
        self.stats['fingerprints_generated'] += 1
        
        # Keep only recent fingerprints
        if len(self.fingerprint_history) > 50:
            self.fingerprint_history = self.fingerprint_history[-50:]
        
        return fingerprint
    
    def _select_fingerprint_type(self) -> FingerprintType:
        """Select fingerprint type based on probabilities"""
        
        types = [
            FingerprintType.DESKTOP_CHROME,
            FingerprintType.DESKTOP_FIREFOX,
            FingerprintType.DESKTOP_SAFARI,
            FingerprintType.MOBILE_CHROME,
            FingerprintType.MOBILE_SAFARI,
            FingerprintType.TABLET_CHROME,
            FingerprintType.LINUX_FIREFOX,
            FingerprintType.EDGE
        ]
        
        # Real-world browser market share weights (approx)
        weights = [0.65, 0.05, 0.03, 0.20, 0.03, 0.02, 0.01, 0.01]
        
        return random.choices(types, weights=weights, k=1)[0]
    
    def _select_hardware_profile(self, fingerprint_type: FingerprintType) -> str:
        """Select appropriate hardware profile"""
        
        if fingerprint_type in [FingerprintType.MOBILE_CHROME, FingerprintType.MOBILE_SAFARI]:
            profiles = ['mobile_high_end', 'mobile_mid_end', 'mobile_low_end']
            weights = [0.3, 0.5, 0.2]
        elif fingerprint_type == FingerprintType.TABLET_CHROME:
            return 'tablet'
        elif fingerprint_type == FingerprintType.DESKTOP_SAFARI:
            return 'laptop'  # Most Macs are laptops
        else:
            profiles = ['desktop_high_end', 'desktop_mid_end', 'desktop_low_end', 'laptop']
            weights = [0.2, 0.3, 0.2, 0.3]
        
        return random.choices(profiles, weights=weights, k=1)[0]
    
    def _generate_user_agent(self, fingerprint_type: FingerprintType) -> str:
        """Generate realistic user agent"""
        
        ua_templates = {
            FingerprintType.DESKTOP_CHROME: [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36",
                "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36"
            ],
            FingerprintType.DESKTOP_FIREFOX: [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{version}) Gecko/20100101 Firefox/{version}",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:{version}) Gecko/20100101 Firefox/{version}",
                "Mozilla/5.0 (X11; Linux x86_64; rv:{version}) Gecko/20100101 Firefox/{version}"
            ],
            FingerprintType.DESKTOP_SAFARI: [
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{version} Safari/605.1.15",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{version} Safari/605.1.15"
            ],
            FingerprintType.MOBILE_CHROME: [
                "Mozilla/5.0 (Linux; Android {android_version}; {device_model}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android {android_version}; {device_model}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Mobile Safari/537.36"
            ],
            FingerprintType.MOBILE_SAFARI: [
                "Mozilla/5.0 (iPhone; CPU iPhone OS {ios_version} like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{version} Mobile/15E148 Safari/604.1"
            ],
            FingerprintType.TABLET_CHROME: [
                "Mozilla/5.0 (Linux; Android {android_version}; {tablet_model}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36"
            ],
            FingerprintType.LINUX_FIREFOX: [
                "Mozilla/5.0 (X11; Linux x86_64; rv:{version}) Gecko/20100101 Firefox/{version}"
            ],
            FingerprintType.EDGE: [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36 Edg/{version}"
            ]
        }
        
        template = random.choice(ua_templates[fingerprint_type])
        
        # Generate version numbers
        if fingerprint_type in [FingerprintType.DESKTOP_CHROME, 
                              FingerprintType.MOBILE_CHROME,
                              FingerprintType.TABLET_CHROME,
                              FingerprintType.EDGE]:
            version = f"{random.randint(120, 125)}.0.{random.randint(0, 9999)}.{random.randint(0, 999)}"
        elif fingerprint_type in [FingerprintType.DESKTOP_FIREFOX, 
                                FingerprintType.LINUX_FIREFOX]:
            version = f"{random.randint(120, 125)}.0"
        elif fingerprint_type == FingerprintType.DESKTOP_SAFARI:
            version = f"{random.randint(17, 18)}.{random.randint(0, 3)}"
        elif fingerprint_type == FingerprintType.MOBILE_SAFARI:
            version = f"{random.randint(16, 17)}.{random.randint(0, 3)}"
        else:
            version = "120.0"
        
        # Fill template variables
        if '{android_version}' in template:
            android_versions = ['13', '14', '15']
            device_models = ['SM-G991B', 'SM-S901B', 'Pixel 7', 'Pixel 8', 'OnePlus 9']
            tablet_models = ['SM-X700', 'SM-X800', 'Pixel Tablet']
            
            if fingerprint_type == FingerprintType.TABLET_CHROME:
                model = random.choice(tablet_models)
            else:
                model = random.choice(device_models)
            
            ua = template.format(
                android_version=random.choice(android_versions),
                device_model=model,
                tablet_model=model,
                version=version
            )
        elif '{ios_version}' in template:
            ios_versions = ['17_2', '17_3', '17_4']
            ua = template.format(
                ios_version=random.choice(ios_versions),
                version=version
            )
        else:
            ua = template.format(version=version)
        
        return ua
    
    def _extract_version_from_ua(self, user_agent: str) -> str:
        """Extract version from user agent"""
        
        # Simple version extraction
        if 'Chrome/' in user_agent:
            parts = user_agent.split('Chrome/')
            if len(parts) > 1:
                version = parts[1].split(' ')[0]
                return version.split('.')[0]  # Return major version
        
        elif 'Firefox/' in user_agent:
            parts = user_agent.split('Firefox/')
            if len(parts) > 1:
                return parts[1].split(' ')[0].split('.')[0]
        
        elif 'Safari/' in user_agent and 'Version/' in user_agent:
            parts = user_agent.split('Version/')
            if len(parts) > 1:
                version = parts[1].split(' ')[0]
                return version.split('.')[0]
        
        elif 'Edg/' in user_agent:
            parts = user_agent.split('Edg/')
            if len(parts) > 1:
                return parts[1].split(' ')[0].split('.')[0]
        
        return "120.0"  # Default
    
    def _select_locale(self, fingerprint_type: FingerprintType) -> Dict[str, Any]:
        """Select locale based on fingerprint type"""
        
        # Map device types to common locales
        locale_mapping = {
            'desktop': ['en-US', 'en-GB', 'de-DE', 'fr-FR', 'es-ES'],
            'mobile': ['en-US', 'en-IN', 'ja-JP', 'en-GB'],
            'tablet': ['en-US', 'en-GB', 'fr-FR']
        }
        
        device_type = self.templates[fingerprint_type]['device_type']
        
        if device_type in locale_mapping:
            locale = random.choice(locale_mapping[device_type])
        else:
            locale = 'en-US'
        
        return self.locale_data[locale]
    
    def _generate_platform_version(self, fingerprint_type: FingerprintType) -> str:
        """Generate platform version"""
        
        if fingerprint_type == FingerprintType.DESKTOP_CHROME:
            return random.choice(['10.0', '11.0', 'NT 10.0', 'NT 11.0'])
        elif fingerprint_type == FingerprintType.DESKTOP_SAFARI:
            return random.choice(['10_15_7', '14_2_1', '13_5_2'])
        elif fingerprint_type in [FingerprintType.MOBILE_CHROME, FingerprintType.TABLET_CHROME]:
            return random.choice(['13', '14', '15'])
        elif fingerprint_type == FingerprintType.MOBILE_SAFARI:
            return random.choice(['17_2', '17_3', '17_4'])
        else:
            return '10.0'
    
    def _get_architecture(self, fingerprint_type: FingerprintType) -> str:
        """Get architecture string"""
        
        if fingerprint_type in [FingerprintType.DESKTOP_CHROME, 
                              FingerprintType.DESKTOP_FIREFOX,
                              FingerprintType.DESKTOP_SAFARI,
                              FingerprintType.LINUX_FIREFOX,
                              FingerprintType.EDGE]:
            return random.choice(['x86', 'x64'])
        elif fingerprint_type in [FingerprintType.MOBILE_CHROME,
                                FingerprintType.MOBILE_SAFARI,
                                FingerprintType.TABLET_CHROME]:
            return random.choice(['arm', 'arm64', 'aarch64'])
        else:
            return 'x64'
    
    def _generate_webgl_renderer(self, vendor: str, fingerprint_type: FingerprintType) -> str:
        """Generate WebGL renderer string"""
        
        renderers = {
            'Google Inc.': ['ANGLE (Google, Vulkan 1.3.0 (SwiftShader Device (Subzero) (0x0000C0DE)), SwiftShader driver)'],
            'Intel Inc.': [
                'Intel(R) UHD Graphics 620',
                'Intel(R) UHD Graphics 630',
                'Intel(R) Iris(R) Xe Graphics',
                'Intel(R) HD Graphics 6000'
            ],
            'NVIDIA Corporation': [
                'NVIDIA GeForce RTX 3060',
                'NVIDIA GeForce RTX 3070',
                'NVIDIA GeForce GTX 1660',
                'NVIDIA GeForce GTX 1060'
            ],
            'AMD': [
                'AMD Radeon RX 6700 XT',
                'AMD Radeon RX 580',
                'AMD Radeon RX 5700 XT'
            ],
            'Mozilla': ['Mozilla'],
            'Apple Inc.': ['Apple GPU', 'Apple M1 GPU', 'Apple M2 GPU'],
            'Qualcomm': ['Adreno 660', 'Adreno 650', 'Adreno 640'],
            'ARM': ['Mali-G78', 'Mali-G77', 'Mali-G76']
        }
        
        if vendor in renderers:
            return random.choice(renderers[vendor])
        else:
            return 'WebKit WebGL'
    
    def _generate_webgl_extensions(self) -> List[str]:
        """Generate WebGL extensions"""
        
        common_extensions = [
            'ANGLE_instanced_arrays',
            'EXT_blend_minmax',
            'EXT_color_buffer_float',
            'EXT_color_buffer_half_float',
            'EXT_disjoint_timer_query',
            'EXT_float_blend',
            'EXT_frag_depth',
            'EXT_shader_texture_lod',
            'EXT_sRGB',
            'EXT_texture_compression_bptc',
            'EXT_texture_compression_rgtc',
            'EXT_texture_filter_anisotropic',
            'KHR_parallel_shader_compile',
            'OES_element_index_uint',
            'OES_fbo_render_mipmap',
            'OES_standard_derivatives',
            'OES_texture_float',
            'OES_texture_float_linear',
            'OES_texture_half_float',
            'OES_texture_half_float_linear',
            'OES_vertex_array_object',
            'WEBGL_color_buffer_float',
            'WEBGL_compressed_texture_astc',
            'WEBGL_compressed_texture_etc',
            'WEBGL_compressed_texture_etc1',
            'WEBGL_compressed_texture_s3tc',
            'WEBGL_compressed_texture_s3tc_srgb',
            'WEBGL_debug_renderer_info',
            'WEBGL_debug_shaders',
            'WEBGL_depth_texture',
            'WEBGL_draw_buffers',
            'WEBGL_lose_context',
            'WEBGL_multi_draw'
        ]
        
        # Return random subset
        num_extensions = random.randint(15, 25)
        return random.sample(common_extensions, num_extensions)
    
    def _generate_canvas_hash(self) -> str:
        """Generate canvas fingerprint hash"""
        
        # Simulate canvas fingerprint with noise
        canvas_data = f"{random.getrandbits(256):064x}"
        return hashlib.sha256(canvas_data.encode()).hexdigest()
    
    def _generate_audio_hash(self) -> str:
        """Generate audio context hash"""
        
        # Simulate audio fingerprint
        audio_data = f"{random.getrandbits(256):064x}"
        return hashlib.sha256(audio_data.encode()).hexdigest()[:32]
    
    def _generate_font_list(self, font_set: str) -> List[str]:
        """Generate font list based on font set"""
        
        font_sets = {
            'windows': [
                'Arial', 'Arial Black', 'Calibri', 'Cambria', 'Candara',
                'Comic Sans MS', 'Consolas', 'Constantia', 'Corbel',
                'Courier New', 'Georgia', 'Impact', 'Lucida Console',
                'Microsoft Sans Serif', 'Segoe UI', 'Tahoma', 'Times New Roman',
                'Trebuchet MS', 'Verdana', 'Webdings', 'Wingdings',
                'MS Gothic', 'MS Mincho', 'Meiryo', 'Yu Gothic'
            ],
            'mac': [
                'Arial', 'Arial Black', 'Avenir', 'Baskerville', 'Chalkboard',
                'Charter', 'Cochin', 'Comic Sans MS', 'Courier New', 'Futura',
                'Geneva', 'Georgia', 'Gill Sans', 'Helvetica', 'Helvetica Neue',
                'Herculanum', 'Hoefler Text', 'Impact', 'Lucida Grande',
                'Monaco', 'Optima', 'Palatino', 'Papyrus', 'Skia', 'Tahoma',
                'Times New Roman', 'Trebuchet MS', 'Verdana', 'Zapfino',
                'Hiragino Sans', 'Hiragino Mincho Pro'
            ],
            'linux': [
                'Arial', 'Liberation Sans', 'DejaVu Sans', 'Ubuntu',
                'FreeSans', 'Bitstream Vera Sans', 'Nimbus Sans L',
                'Courier New', 'Liberation Mono', 'DejaVu Mono',
                'FreeMono', 'Bitstream Vera Mono', 'Nimbus Mono L',
                'Times New Roman', 'Liberation Serif', 'DejaVu Serif',
                'FreeSerif', 'Bitstream Vera Serif', 'Nimbus Roman',
                'Noto Sans', 'Roboto', 'Open Sans'
            ],
            'android': [
                'Roboto', 'Noto Sans', 'Droid Sans', 'Open Sans',
                'sans-serif', 'monospace', 'serif',
                'Arial', 'Verdana', 'Times New Roman',
                'Courier New', 'Georgia'
            ],
            'ios': [
                'San Francisco', 'Helvetica Neue', 'Arial',
                'Times New Roman', 'Courier New', 'Georgia',
                'Verdana', 'Trebuchet MS', 'Comic Sans MS'
            ],
            'mixed': [
                'Arial', 'Helvetica', 'Times New Roman', 'Courier New',
                'Verdana', 'Georgia', 'Tahoma', 'Trebuchet MS',
                'Comic Sans MS', 'Impact', 'Lucida Console'
            ]
        }
        
        fonts = font_sets.get(font_set, font_sets['mixed'])
        
        # Select random subset (15-30 fonts)
        num_fonts = random.randint(15, 30)
        selected = random.sample(fonts, min(num_fonts, len(fonts)))
        
        return sorted(selected)
    
    def _generate_plugins(self, fingerprint_type: FingerprintType) -> List[str]:
        """Generate plugin list"""
        
        common_plugins = [
            'Chrome PDF Viewer',
            'Chromium PDF Viewer',
            'Microsoft Edge PDF Viewer',
            'WebKit built-in PDF',
            'Native Client'
        ]
        
        if fingerprint_type == FingerprintType.DESKTOP_CHROME:
            additional = [
                'Chrome PDF Viewer',
                'Chromium PDF Viewer',
                'Native Client'
            ]
            plugins = common_plugins + additional[:random.randint(0, 2)]
        elif fingerprint_type == FingerprintType.DESKTOP_FIREFOX:
            plugins = ['default']
        elif fingerprint_type == FingerprintType.DESKTOP_SAFARI:
            plugins = ['WebKit built-in PDF']
        elif fingerprint_type in [FingerprintType.MOBILE_CHROME, 
                                FingerprintType.MOBILE_SAFARI,
                                FingerprintType.TABLET_CHROME]:
            plugins = common_plugins[:random.randint(1, 3)]
        else:
            plugins = common_plugins
        
        return plugins
    
    def _generate_mime_types(self, plugins: List[str]) -> List[str]:
        """Generate MIME types based on plugins"""
        
        mime_types = [
            'application/pdf',
            'text/pdf',
            'application/x-google-chrome-pdf',
            'application/x-nacl',
            'application/x-pnacl'
        ]
        
        if len(plugins) > 2:
            mime_types.extend([
                'application/x-shockwave-flash',
                'application/futuresplash',
                'application/x-silverlight'
            ])
        
        return random.sample(mime_types, random.randint(2, len(mime_types)))
    
    def _generate_connection_info(self) -> Dict[str, Any]:
        """Generate connection information"""
        
        connection_types = ['wifi', 'cellular', 'ethernet']
        connection_weights = [0.6, 0.3, 0.1]
        connection_type = random.choices(connection_types, weights=connection_weights, k=1)[0]
        
        if connection_type == 'wifi':
            effective_type = random.choice(['4g', 'wifi'])
            downlink = random.choice([10, 25, 50, 100, 300, 500, 1000])
            rtt = random.randint(20, 100)
        elif connection_type == 'cellular':
            effective_type = random.choice(['4g', '3g', '2g'])
            downlink = random.choice([1, 5, 10, 25, 50])
            rtt = random.randint(100, 500)
        else:  # ethernet
            effective_type = '4g'
            downlink = random.choice([100, 300, 500, 1000])
            rtt = random.randint(10, 50)
        
        return {
            'type': connection_type,
            'effective_type': effective_type,
            'downlink': downlink,
            'rtt': rtt,
            'save_data': random.choice([True, False])
        }
    
    def _generate_permissions(self) -> Dict[str, str]:
        """Generate browser permissions"""
        
        permissions = {
            'geolocation': random.choice(['granted', 'denied', 'prompt']),
            'notifications': random.choice(['granted', 'denied', 'prompt']),
            'camera': random.choice(['denied', 'prompt']),
            'microphone': random.choice(['denied', 'prompt']),
            'background-sync': 'granted',
            'persistent-storage': random.choice(['granted', 'prompt'])
        }
        
        return permissions
    
    def _calculate_fingerprint_hash(self) -> str:
        """Calculate fingerprint hash for uniqueness"""
        
        components = [
            str(random.getrandbits(128)),
            str(time.time()),
            platform.node() if hasattr(platform, 'node') else '',
            str(psutil.cpu_count() if hasattr(psutil, 'cpu_count') else 4)
        ]
        
        data = '-'.join(components)
        return hashlib.sha256(data.encode()).hexdigest()[:32]
    
    def rotate_fingerprint(self, 
                          force_rotation: bool = False,
                          min_time_between: int = 300) -> Optional[FingerprintConfig]:
        """Rotate to a new fingerprint if needed"""
        
        current_time = time.time()
        
        # Check if rotation is needed
        if not self.current_fingerprint:
            return self.generate_fingerprint()
        
        # Check expiration
        if current_time > self.current_fingerprint.expires_at:
            print("🔄 Fingerprint expired, rotating...")
            return self.generate_fingerprint()
        
        # Check if forced rotation
        if force_rotation:
            print("🔄 Forced fingerprint rotation...")
            return self.generate_fingerprint()
        
        # Check time-based rotation
        time_since_last = current_time - self.current_fingerprint.created_at
        if time_since_last > min_time_between:
            print(f"🔄 Time-based fingerprint rotation ({time_since_last:.0f}s)...")
            return self.generate_fingerprint()
        
        # No rotation needed
        return None
    
    def get_fingerprint_for_playwright(self) -> Dict[str, Any]:
        """Get current fingerprint formatted for Playwright"""
        
        if not self.current_fingerprint:
            self.current_fingerprint = self.generate_fingerprint()
        
        return self.current_fingerprint.get_browser_context()
    
    def get_fingerprint_statistics(self) -> Dict[str, Any]:
        """Get fingerprint rotation statistics"""
        
        unique_fingerprints = len(set(fp.fingerprint_hash for fp in self.fingerprint_history))
        
        return {
            **self.stats,
            'current_fingerprint_age': time.time() - self.current_fingerprint.created_at 
                                      if self.current_fingerprint else 0,
            'fingerprints_in_history': len(self.fingerprint_history),
            'unique_fingerprints_generated': unique_fingerprints,
            'average_fingerprint_lifetime': self._calculate_average_lifetime(),
            'rotation_frequency': self.stats['rotations_performed'] / 
                                 max(1, self.stats['fingerprints_generated']),
            'fingerprint_types_used': self._get_fingerprint_type_distribution()
        }
    
    def _calculate_average_lifetime(self) -> float:
        """Calculate average fingerprint lifetime"""
        
        if len(self.fingerprint_history) < 2:
            return 0
        
        lifetimes = []
        for i in range(1, len(self.fingerprint_history)):
            lifetime = self.fingerprint_history[i].created_at - self.fingerprint_history[i-1].created_at
            lifetimes.append(lifetime)
        
        return sum(lifetimes) / len(lifetimes) if lifetimes else 0
    
    def _get_fingerprint_type_distribution(self) -> Dict[str, int]:
        """Get distribution of fingerprint types used"""
        
        distribution = {}
        for fp in self.fingerprint_history:
            # Determine type from user agent
            ua = fp.user_agent.lower()
            if 'chrome' in ua and 'mobile' in ua:
                fp_type = 'mobile_chrome'
            elif 'chrome' in ua and 'android' in ua:
                fp_type = 'tablet_chrome'
            elif 'chrome' in ua and 'edg' in ua:
                fp_type = 'edge'
            elif 'chrome' in ua:
                fp_type = 'desktop_chrome'
            elif 'firefox' in ua:
                fp_type = 'desktop_firefox'
            elif 'safari' in ua and 'iphone' in ua:
                fp_type = 'mobile_safari'
            elif 'safari' in ua:
                fp_type = 'desktop_safari'
            else:
                fp_type = 'unknown'
            
            distribution[fp_type] = distribution.get(fp_type, 0) + 1
        
        return distribution
    
    def export_fingerprint_data(self, format_type: str = 'json') -> str:
        """Export fingerprint data for analysis"""
        
        if format_type == 'json':
            data = {
                'current_fingerprint': self.current_fingerprint.to_dict() 
                                      if self.current_fingerprint else None,
                'fingerprint_history': [fp.to_dict() for fp in self.fingerprint_history[-10:]],  # Last 10
                'statistics': self.get_fingerprint_statistics(),
                'templates': {k.value: v for k, v in self.templates.items()}
            }
            return json.dumps(data, indent=2, default=str)
        
        elif format_type == 'csv':
            # Simple CSV export
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Header
            writer.writerow([
                'timestamp', 'user_agent', 'platform', 'screen_resolution',
                'timezone', 'locale', 'fingerprint_hash'
            ])
            
            # Data
            for fp in self.fingerprint_history:
                writer.writerow([
                    datetime.fromtimestamp(fp.created_at).isoformat(),
                    fp.user_agent[:50],  # Truncate
                    fp.platform,
                    f"{fp.screen_width}x{fp.screen_height}",
                    fp.timezone,
                    fp.locale,
                    fp.fingerprint_hash[:16]  # First 16 chars
                ])
            
            return output.getvalue()
        
        else:
            return f"Unsupported format: {format_type}"
    
    def validate_fingerprint(self, fingerprint: FingerprintConfig) -> Dict[str, Any]:
        """Validate fingerprint for consistency and realism"""
        
        issues = []
        warnings = []
        
        # Check user agent consistency
        ua = fingerprint.user_agent.lower()
        
        if fingerprint.device_type == 'desktop':
            if 'mobile' in ua or 'android' in ua or 'iphone' in ua:
                issues.append("Desktop fingerprint has mobile user agent")
        elif fingerprint.device_type in ['mobile', 'tablet']:
            if 'windows' in ua or 'macintosh' in ua:
                issues.append("Mobile fingerprint has desktop user agent")
        
        # Check screen resolution consistency
        if fingerprint.device_type == 'desktop':
            if fingerprint.screen_width < 1024 or fingerprint.screen_height < 768:
                warnings.append("Desktop screen resolution seems small")
        elif fingerprint.device_type == 'mobile':
            if fingerprint.screen_width > 500 or fingerprint.screen_height > 1000:
                warnings.append("Mobile screen resolution seems large")
        
        # Check timezone consistency with locale
        locale_region = fingerprint.locale.split('-')[-1]
        if locale_region == 'US' and not fingerprint.timezone.startswith('America/'):
            warnings.append(f"US locale with non-US timezone: {fingerprint.timezone}")
        elif locale_region == 'GB' and not fingerprint.timezone.startswith('Europe/London'):
            warnings.append(f"GB locale with non-UK timezone: {fingerprint.timezone}")
        
        # Check WebGL consistency
        if fingerprint.gpu_vendor == 'NVIDIA Corporation' and 'NVIDIA' not in fingerprint.webgl_renderer:
            warnings.append("GPU vendor mismatch with WebGL renderer")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'score': self._calculate_fingerprint_score(fingerprint, issues, warnings)
        }
    
    def _calculate_fingerprint_score(self, 
                                    fingerprint: FingerprintConfig,
                                    issues: List[str],
                                    warnings: List[str]) -> float:
        """Calculate fingerprint quality score"""
        
        score = 100.0
        
        # Deduct for issues
        score -= len(issues) * 20
        
        # Deduct for warnings
        score -= len(warnings) * 5
        
        # Bonus for uniqueness
        unique_hash = fingerprint.fingerprint_hash
        same_hash_count = sum(1 for fp in self.fingerprint_history 
                            if fp.fingerprint_hash == unique_hash)
        if same_hash_count == 1:
            score += 10  # Bonus for unique fingerprint
        
        # Bonus for recent browser version
        try:
            version = int(fingerprint.browser_version.split('.')[0])
            if version >= 120:  # Recent version
                score += 5
        except:
            pass
        
        return max(0, min(100, score))

# Utility functions for easy use
def create_fingerprint_rotator(config_path: str = "config_advanced.json") -> FingerprintRotator:
    """Create and initialize a fingerprint rotator"""
    return FingerprintRotator(config_path)

def get_fingerprint_for_session(rotator: FingerprintRotator, 
                               session_type: str = "desktop") -> Dict[str, Any]:
    """Get fingerprint for a session"""
    
    if session_type == "desktop":
        fp_type = random.choice([
            FingerprintType.DESKTOP_CHROME,
            FingerprintType.DESKTOP_FIREFOX,
            FingerprintType.DESKTOP_SAFARI,
            FingerprintType.EDGE
        ])
    elif session_type == "mobile":
        fp_type = random.choice([
            FingerprintType.MOBILE_CHROME,
            FingerprintType.MOBILE_SAFARI
        ])
    elif session_type == "tablet":
        fp_type = FingerprintType.TABLET_CHROME
    else:
        fp_type = None
    
    fingerprint = rotator.generate_fingerprint(fp_type)
    return fingerprint.to_dict()

if __name__ == "__main__":
    # Test the fingerprint rotator
    rotator = FingerprintRotator()
    
    print("🧪 Testing Fingerprint Rotator")
    print("=" * 60)
    
    # Generate a fingerprint
    fingerprint = rotator.generate_fingerprint()
    print(f"✅ Generated fingerprint: {fingerprint.session_id}")
    print(f"   User Agent: {fingerprint.user_agent[:80]}...")
    print(f"   Screen: {fingerprint.screen_width}x{fingerprint.screen_height}")
    print(f"   Platform: {fingerprint.platform}")
    print(f"   Locale: {fingerprint.locale}")
    print(f"   Timezone: {fingerprint.timezone}")
    
    # Validate
    validation = rotator.validate_fingerprint(fingerprint)
    print(f"📊 Validation: {'✅ Valid' if validation['valid'] else '❌ Invalid'}")
    print(f"   Score: {validation['score']}/100")
    
    if validation['issues']:
        print(f"   Issues: {', '.join(validation['issues'])}")
    if validation['warnings']:
        print(f"   Warnings: {', '.join(validation['warnings'])}")
    
    # Statistics
    stats = rotator.get_fingerprint_statistics()
    print(f"\n📈 Statistics:")
    print(f"   Fingerprints Generated: {stats['fingerprints_generated']}")
    print(f"   Unique Fingerprints: {stats['unique_fingerprints_generated']}")
    print(f"   Current Age: {stats['current_fingerprint_age']:.0f}s")