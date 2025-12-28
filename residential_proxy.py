#!/usr/bin/env python3
"""
Residential Proxy Manager
Manages proxy rotation for realistic network simulation
"""

import random
import asyncio
import aiohttp
import json
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class ProxyType(Enum):
    """Proxy types"""
    RESIDENTIAL = "residential"
    DATACENTER = "datacenter"
    MOBILE = "mobile"
    FREE = "free"

@dataclass
class Proxy:
    """Proxy configuration"""
    server: str
    username: str = ""
    password: str = ""
    type: ProxyType = ProxyType.RESIDENTIAL
    country: str = "US"
    city: str = ""
    isp: str = ""
    latency: int = 0
    success_rate: float = 0.0
    last_used: float = 0.0
    usage_count: int = 0
    blacklisted: bool = False

class ResidentialProxyManager:
    """Manage residential proxies for realistic IP rotation"""
    
    def __init__(self, use_proxy: bool = False, config_path: str = "config_advanced.json"):
        self.use_proxy = use_proxy
        self.proxies: List[Proxy] = []
        self.blacklist: List[str] = []
        self.rotation_index = 0
        self.stats = {
            'total_requests': 0,
            'failed_requests': 0,
            'success_rate': 0.0,
            'avg_latency': 0.0
        }
        
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Free proxy sources (for educational use only)
        self.free_sources = [
            "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
            "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
            "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.json"
        ]
        
        # Paid proxy services (placeholder - for production use)
        self.paid_services = {
            'brightdata': {
                'url': 'https://brightdata.com',
                'format': 'http://{zone}-session-{session}:{password}@zproxy.lum-superproxy.io:{port}',
                'countries': ['us', 'gb', 'de', 'fr', 'jp', 'ca', 'au', 'in']
            },
            'oxylabs': {
                'url': 'https://oxylabs.io',
                'format': 'http://customer-{username}:{password}@pr.oxylabs.io:7777',
                'countries': ['us', 'gb', 'de', 'fr', 'jp', 'ca', 'au', 'in']
            },
            'smartproxy': {
                'url': 'https://smartproxy.com',
                'format': 'http://{username}:{password}@gate.smartproxy.com:{port}',
                'countries': ['us', 'gb', 'de', 'fr', 'jp', 'ca', 'au', 'in']
            }
        }
        
        # ISP data for residential simulation
        self.isp_data = {
            'comcast': {
                'asn': 'AS7922',
                'ip_ranges': ['24.0.0.0/12', '50.0.0.0/10', '73.0.0.0/8'],
                'dns_servers': ['75.75.75.75', '75.75.76.76'],
                'locations': ['US'],
                'bandwidth_range': (50, 1000)
            },
            'verizon': {
                'asn': 'AS701',
                'ip_ranges': ['71.0.0.0/10', '72.0.0.0/10', '96.0.0.0/6'],
                'dns_servers': ['4.2.2.1', '4.2.2.2'],
                'locations': ['US'],
                'bandwidth_range': (25, 940)
            },
            'att': {
                'asn': 'AS7018',
                'ip_ranges': ['12.0.0.0/8', '65.0.0.0/8', '208.0.0.0/8'],
                'dns_servers': ['68.94.156.1', '68.94.157.1'],
                'locations': ['US'],
                'bandwidth_range': (10, 1000)
            },
            'spectrum': {
                'asn': 'AS11351',
                'ip_ranges': ['24.0.0.0/12', '65.0.0.0/8', '71.0.0.0/10'],
                'dns_servers': ['1.1.1.1', '1.0.0.1'],
                'locations': ['US'],
                'bandwidth_range': (100, 940)
            }
        }
        
        # Initialize proxy pool
        if self.use_proxy:
            asyncio.create_task(self.initialize_proxies())
    
    async def initialize_proxies(self):
        """Initialize proxy pool"""
        print("🔧 Initializing proxy pool...")
        
        if self.config['network_settings']['proxy_service'] == 'free':
            await self.load_free_proxies()
        elif self.config['network_settings']['proxy_service'] == 'paid':
            await self.load_paid_proxies()
        else:
            await self.generate_simulated_proxies()
        
        print(f"✅ Proxy pool initialized: {len(self.proxies)} proxies available")
    
    async def load_free_proxies(self):
        """Load proxies from free sources"""
        print("📥 Loading free proxies...")
        
        all_proxies = []
        
        async with aiohttp.ClientSession() as session:
            for source in self.free_sources:
                try:
                    print(f"  Fetching from {source}")
                    async with session.get(source, timeout=10) as response:
                        if response.status == 200:
                            content = await response.text()
                            
                            if source.endswith('.json'):
                                # JSON format
                                data = json.loads(content)
                                proxies = self._parse_json_proxies(data)
                            else:
                                # Text format
                                proxies = self._parse_text_proxies(content)
                            
                            all_proxies.extend(proxies)
                            print(f"    Found {len(proxies)} proxies")
                            
                except Exception as e:
                    print(f"    Failed to fetch from {source}: {e}")
        
        # Convert to Proxy objects
        for proxy_str in all_proxies:
            proxy = self._create_proxy_from_string(proxy_str)
            if proxy:
                self.proxies.append(proxy)
        
        # Test proxies
        await self.test_proxies()
    
    def _parse_text_proxies(self, content: str) -> List[str]:
        """Parse text-based proxy lists"""
        proxies = []
        lines = content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                proxies.append(line)
        
        return proxies
    
    def _parse_json_proxies(self, data: dict) -> List[str]:
        """Parse JSON-based proxy lists"""
        proxies = []
        
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    ip = item.get('ip')
                    port = item.get('port')
                    if ip and port:
                        proxies.append(f"{ip}:{port}")
                elif isinstance(item, str):
                    proxies.append(item)
        elif isinstance(data, dict):
            # Handle different JSON structures
            if 'data' in data and isinstance(data['data'], list):
                for item in data['data']:
                    ip = item.get('ip')
                    port = item.get('port')
                    if ip and port:
                        proxies.append(f"{ip}:{port}")
        
        return proxies
    
    def _create_proxy_from_string(self, proxy_str: str) -> Optional[Proxy]:
        """Create Proxy object from string"""
        
        try:
            # Parse proxy string
            if '://' in proxy_str:
                # Has protocol
                protocol, rest = proxy_str.split('://', 1)
                if '@' in rest:
                    # Has auth
                    auth, server = rest.split('@', 1)
                    if ':' in auth:
                        username, password = auth.split(':', 1)
                    else:
                        username, password = auth, ""
                else:
                    server = rest
                    username, password = "", ""
            else:
                # No protocol
                server = proxy_str
                username, password = "", ""
                protocol = "http"
            
            # Add protocol if missing
            if not server.startswith(('http://', 'https://', 'socks5://')):
                server = f"{protocol}://{server}"
            
            # Determine proxy type based on characteristics
            proxy_type = ProxyType.FREE
            
            # Try to extract IP for analysis
            ip_part = server.split('://')[-1].split(':')[0].split('@')[-1]
            
            # Check if it looks like residential (based on common patterns)
            if any(isp in server.lower() for isp in self.isp_data.keys()):
                proxy_type = ProxyType.RESIDENTIAL
            elif any(keyword in server.lower() for keyword in ['mobile', 'cell', '4g', '5g']):
                proxy_type = ProxyType.MOBILE
            elif any(keyword in server.lower() for keyword in ['datacenter', 'dc', 'server']):
                proxy_type = ProxyType.DATACENTER
            
            # Guess country from common TLDs
            country = "US"  # Default
            tld_countries = {
                '.us': 'US', '.uk': 'GB', '.de': 'DE', '.fr': 'FR',
                '.jp': 'JP', '.ca': 'CA', '.au': 'AU', '.in': 'IN'
            }
            
            for tld, country_code in tld_countries.items():
                if tld in server.lower():
                    country = country_code
                    break
            
            return Proxy(
                server=server,
                username=username,
                password=password,
                type=proxy_type,
                country=country,
                latency=random.randint(50, 500),
                success_rate=random.uniform(0.5, 0.9),
                last_used=0.0,
                usage_count=0,
                blacklisted=False
            )
            
        except Exception as e:
            print(f"Failed to parse proxy {proxy_str}: {e}")
            return None
    
    async def load_paid_proxies(self):
        """Load proxies from paid services"""
        print("💳 Loading paid proxies (simulated)...")
        
        # For educational purposes, we simulate paid proxies
        # In production, you would integrate with actual paid services
        
        service = self.config['network_settings'].get('proxy_service', 'brightdata')
        service_config = self.paid_services.get(service, self.paid_services['brightdata'])
        
        # Generate simulated paid proxies
        countries = service_config['countries']
        num_proxies = 20  # Simulated number
        
        for i in range(num_proxies):
            country = random.choice(countries)
            city = random.choice(['New York', 'Los Angeles', 'Chicago', 'London', 'Berlin', 'Tokyo'])
            isp = random.choice(list(self.isp_data.keys()))
            
            # Generate proxy using service format
            proxy_server = service_config['format'].format(
                zone=f'{country}-{city.lower().replace(" ", "-")}',
                session=f'sess{i:04d}',
                password='password123',
                username='user123',
                port=random.choice([22225, 24000, 30000])
            )
            
            proxy = Proxy(
                server=proxy_server,
                username=f'user{i:04d}',
                password='password123',
                type=ProxyType.RESIDENTIAL,
                country=country.upper(),
                city=city,
                isp=isp,
                latency=random.randint(20, 100),
                success_rate=random.uniform(0.8, 0.99),
                last_used=0.0,
                usage_count=0,
                blacklisted=False
            )
            
            self.proxies.append(proxy)
        
        print(f"✅ Generated {len(self.proxies)} simulated paid proxies")
    
    async def generate_simulated_proxies(self):
        """Generate simulated residential proxies"""
        print("🔄 Generating simulated residential proxies...")
        
        num_proxies = 50
        
        for i in range(num_proxies):
            # Select random ISP
            isp_name = random.choice(list(self.isp_data.keys()))
            isp_info = self.isp_data[isp_name]
            
            # Generate IP within ISP range
            ip_range = random.choice(isp_info['ip_ranges'])
            ip_parts = ip_range.split('/')[0].split('.')
            ip_parts[-1] = str(random.randint(1, 254))
            ip = '.'.join(ip_parts)
            
            # Select location
            country = random.choice(isp_info['locations'])
            city = random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'])
            
            # Create proxy
            proxy = Proxy(
                server=f"http://{ip}:8080",
                username="",
                password="",
                type=ProxyType.RESIDENTIAL,
                country=country,
                city=city,
                isp=isp_name,
                latency=random.randint(20, 100),
                success_rate=random.uniform(0.9, 1.0),
                last_used=0.0,
                usage_count=0,
                blacklisted=False
            )
            
            self.proxies.append(proxy)
        
        print(f"✅ Generated {len(self.proxies)} simulated residential proxies")
    
    async def test_proxies(self, test_url: str = "https://httpbin.org/ip"):
        """Test proxies for functionality"""
        print("🧪 Testing proxies...")
        
        valid_proxies = []
        
        # Test a subset of proxies
        test_subset = random.sample(self.proxies, min(10, len(self.proxies)))
        
        for proxy in test_subset:
            try:
                start_time = time.time()
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        test_url,
                        proxy=proxy.server,
                        timeout=5
                    ) as response:
                        if response.status == 200:
                            latency = (time.time() - start_time) * 1000
                            proxy.latency = int(latency)
                            proxy.success_rate = 1.0
                            valid_proxies.append(proxy)
                            print(f"  ✅ {proxy.server[:50]}... - {latency:.0f}ms")
                        else:
                            proxy.blacklisted = True
                            print(f"  ❌ {proxy.server[:50]}... - HTTP {response.status}")
                
            except Exception as e:
                proxy.blacklisted = True
                print(f"  ❌ {proxy.server[:50]}... - {str(e)[:50]}")
        
        # Update statistics
        if valid_proxies:
            self.proxies = [p for p in self.proxies if not p.blacklisted]
            avg_latency = sum(p.latency for p in valid_proxies) / len(valid_proxies)
            self.stats['avg_latency'] = avg_latency
            self.stats['success_rate'] = len(valid_proxies) / len(test_subset)
            
            print(f"📊 Proxy test complete: {len(valid_proxies)}/{len(test_subset)} working "
                  f"(avg latency: {avg_latency:.0f}ms)")
        else:
            print("⚠️  No working proxies found!")
    
    def get_proxy(self, country: str = None, proxy_type: ProxyType = None) -> Optional[Proxy]:
        """Get a proxy with optional filtering"""
        
        if not self.use_proxy or not self.proxies:
            return None
        
        # Filter proxies
        filtered = self.proxies.copy()
        
        if country:
            filtered = [p for p in filtered if p.country == country.upper()]
        
        if proxy_type:
            filtered = [p for p in filtered if p.type == proxy_type]
        
        # Remove blacklisted
        filtered = [p for p in filtered if not p.blacklisted]
        
        if not filtered:
            return None
        
        # Selection strategies
        strategy = self.config['network_settings'].get('proxy_selection', 'round_robin')
        
        if strategy == 'round_robin':
            # Round-robin selection
            proxy = filtered[self.rotation_index % len(filtered)]
            self.rotation_index += 1
            
        elif strategy == 'random':
            # Random selection
            proxy = random.choice(filtered)
            
        elif strategy == 'best_latency':
            # Best latency
            proxy = min(filtered, key=lambda p: p.latency)
            
        elif strategy == 'best_success_rate':
            # Best success rate
            proxy = max(filtered, key=lambda p: p.success_rate)
            
        elif strategy == 'least_used':
            # Least used
            proxy = min(filtered, key=lambda p: p.usage_count)
            
        else:
            proxy = random.choice(filtered)
        
        # Update proxy stats
        proxy.usage_count += 1
        proxy.last_used = time.time()
        
        # Update manager stats
        self.stats['total_requests'] += 1
        
        return proxy
    
    def get_proxy_for_playwright(self, country: str = None) -> Optional[Dict]:
        """Get proxy formatted for Playwright"""
        
        proxy = self.get_proxy(country)
        if not proxy:
            return None
        
        proxy_config = {
            'server': proxy.server,
            'bypass': '*.google.com,*.youtube.com,*.googlevideo.com,*.ytimg.com,*.googleapis.com',
        }
        
        if proxy.username and proxy.password:
            proxy_config['username'] = proxy.username
            proxy_config['password'] = proxy.password
        
        return proxy_config
    
    def simulate_residential_network(self) -> Dict[str, Any]:
        """Simulate residential network characteristics"""
        
        # Select random ISP
        isp_name = random.choice(list(self.isp_data.keys()))
        isp_info = self.isp_data[isp_name]
        
        # Generate realistic IP
        ip_range = random.choice(isp_info['ip_ranges'])
        ip_parts = ip_range.split('/')[0].split('.')
        ip_parts[-1] = str(random.randint(1, 254))
        ip = '.'.join(ip_parts)
        
        # Generate network metrics
        bandwidth = random.randint(*isp_info['bandwidth_range'])
        latency = random.randint(20, 100)
        jitter = random.randint(1, 20)
        packet_loss = random.uniform(0, 0.5)
        
        # DNS servers
        dns_servers = random.sample(isp_info['dns_servers'], 2)
        
        # Connection type
        connection_types = ['wifi', 'ethernet', 'cellular']
        connection_weights = [0.6, 0.3, 0.1]
        connection_type = random.choices(connection_types, weights=connection_weights, k=1)[0]
        
        # Effective type based on connection
        if connection_type == 'wifi':
            effective_type = random.choice(['4g', 'wifi'])
        elif connection_type == 'ethernet':
            effective_type = '4g'
        else:  # cellular
            effective_type = random.choice(['4g', '3g', '2g'])
        
        return {
            'ip_address': ip,
            'isp': isp_name,
            'asn': isp_info['asn'],
            'country': random.choice(isp_info['locations']),
            'city': random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']),
            'dns_servers': dns_servers,
            'bandwidth_mbps': bandwidth,
            'latency_ms': latency,
            'jitter_ms': jitter,
            'packet_loss_percent': round(packet_loss, 2),
            'connection_type': connection_type,
            'effective_type': effective_type,
            'dns_resolution_ms': random.randint(50, 300),
            'tcp_handshake_ms': random.randint(100, 500),
            'tls_handshake_ms': random.randint(200, 800),
            'http_request_ms': random.randint(50, 200),
            'ip_version': 'IPv4',
            'proxy_detected': False,
            'vpn_detected': False,
            'tor_detected': False
        }
    
    def blacklist_proxy(self, proxy_server: str, reason: str = "Failed"):
        """Blacklist a proxy"""
        
        for proxy in self.proxies:
            if proxy.server == proxy_server:
                proxy.blacklisted = True
                print(f"🚫 Blacklisted proxy: {proxy_server[:50]}... - {reason}")
                break
        
        self.blacklist.append(proxy_server)
        self.stats['failed_requests'] += 1
        
        # Update success rate
        if self.stats['total_requests'] > 0:
            self.stats['success_rate'] = (
                (self.stats['total_requests'] - self.stats['failed_requests']) / 
                self.stats['total_requests'] * 100
            )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get proxy manager statistics"""
        
        working_proxies = [p for p in self.proxies if not p.blacklisted]
        
        return {
            **self.stats,
            'total_proxies': len(self.proxies),
            'working_proxies': len(working_proxies),
            'blacklisted_proxies': len(self.blacklist),
            'proxy_types': {
                'residential': len([p for p in working_proxies if p.type == ProxyType.RESIDENTIAL]),
                'datacenter': len([p for p in working_proxies if p.type == ProxyType.DATACENTER]),
                'mobile': len([p for p in working_proxies if p.type == ProxyType.MOBILE]),
                'free': len([p for p in working_proxies if p.type == ProxyType.FREE])
            },
            'countries': {
                p.country: len([proxy for proxy in working_proxies if proxy.country == p.country])
                for p in working_proxies[:10]  # Top 10 countries
            }
        }
    
    async def rotate_proxies(self):
        """Rotate proxy pool (fetch new proxies)"""
        
        print("🔄 Rotating proxy pool...")
        
        old_count = len(self.proxies)
        
        # Clear old proxies (keep only recently used)
        recent_threshold = time.time() - 3600  # 1 hour
        self.proxies = [p for p in self.proxies if p.last_used > recent_threshold]
        
        print(f"  Kept {len(self.proxies)} recent proxies")
        
        # Load new proxies
        if self.config['network_settings']['proxy_service'] == 'free':
            await self.load_free_proxies()
        elif self.config['network_settings']['proxy_service'] == 'paid':
            await self.load_paid_proxies()
        else:
            await self.generate_simulated_proxies()
        
        new_count = len(self.proxies)
        print(f"✅ Proxy rotation complete: {new_count} proxies available "
              f"(added {new_count - old_count})")