#!/usr/bin/env python3
"""
GitHub Merge Analytics
A tool to analyze and visualize daily merge counts for GitHub repositories.
"""

import argparse
import os
import re
import sys
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Optional, Tuple
import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


class GitHubAnalytics:
    """GitHub repository merge analytics tool."""
    
    def __init__(self):
        self.api_base = "https://api.github.com"
        self.session = requests.Session()
        # Set user agent as required by GitHub API
        self.session.headers.update({
            'User-Agent': 'github-merge-analytics/1.0'
        })
        
        # Add GitHub token authentication if available
        github_token = os.getenv('GITHUB_TOKEN')
        if github_token:
            self.session.headers.update({
                'Authorization': f'Bearer {github_token}'
            })
            print("Using GitHub token authentication (5000 requests/hour limit)")
        else:
            print("No GitHub token found - using unauthenticated requests (60 requests/hour limit)")
    
    def parse_repo_url(self, url: str) -> Tuple[str, str]:
        """Parse GitHub repository URL to extract owner and repo name."""
        # Match various GitHub URL formats
        patterns = [
            r'github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?/?$',
            r'^([^/]+)/([^/]+)$'  # owner/repo format
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                owner, repo = match.groups()
                return owner, repo
        
        raise ValueError(f"Invalid GitHub repository URL: {url}")
    
    def fetch_merged_prs(self, owner: str, repo: str, since_date: datetime) -> List[Dict]:
        """Fetch merged pull requests since the given date."""
        url = f"{self.api_base}/repos/{owner}/{repo}/pulls"
        params = {
            'state': 'closed',
            'sort': 'updated',
            'direction': 'desc',
            'per_page': 100
        }
        
        merged_prs = []
        page = 1
        
        while True:
            params['page'] = page
            
            try:
                response = self.session.get(url, params=params)
                response.raise_for_status()
                
                # Check rate limiting
                if response.status_code == 403 and 'rate limit' in response.text.lower():
                    print("Rate limit exceeded. Please wait or use authentication.")
                    sys.exit(1)
                
                prs = response.json()
                if not prs:
                    break
                
                # Filter for merged PRs within our date range
                for pr in prs:
                    if pr['merged_at']:
                        merged_at = datetime.fromisoformat(pr['merged_at'].replace('Z', '+00:00'))
                        if merged_at.replace(tzinfo=None) >= since_date:
                            merged_prs.append(pr)
                        else:
                            # Since PRs are sorted by updated date, we can stop here
                            # if we encounter an old PR (though this isn't perfect)
                            pass
                
                # Check if we should continue to next page
                if len(prs) < 100:
                    break
                
                page += 1
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching data from GitHub API: {e}")
                sys.exit(1)
        
        return merged_prs
    
    def process_daily_counts(self, merged_prs: List[Dict], days: int = 30) -> Dict[str, int]:
        """Process merged PRs into daily counts."""
        daily_counts = defaultdict(int)
        
        # Initialize all days in the range with 0
        end_date = datetime.now()
        for i in range(days):
            date = end_date - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            daily_counts[date_str] = 0
        
        # Count merges by day
        for pr in merged_prs:
            if pr['merged_at']:
                merged_at = datetime.fromisoformat(pr['merged_at'].replace('Z', '+00:00'))
                date_str = merged_at.strftime('%Y-%m-%d')
                if date_str in daily_counts:
                    daily_counts[date_str] += 1
        
        return dict(daily_counts)
    
    def generate_graph(self, daily_counts: Dict[str, int], owner: str, repo: str):
        """Generate and display a graph of daily merge counts."""
        # Sort dates
        sorted_dates = sorted(daily_counts.keys())
        dates = [datetime.strptime(date, '%Y-%m-%d') for date in sorted_dates]
        counts = [daily_counts[date] for date in sorted_dates]
        
        # Create the plot
        plt.figure(figsize=(12, 6))
        plt.plot(dates, counts, marker='o', linewidth=2, markersize=4)
        plt.title(f'Daily Merge Count - {owner}/{repo}\n(Past {len(dates)} days)', 
                  fontsize=14, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Number of Merges', fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # Format x-axis
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//10)))
        plt.xticks(rotation=45)
        
        # Add some statistics
        total_merges = sum(counts)
        avg_merges = total_merges / len(counts) if counts else 0
        max_merges = max(counts) if counts else 0
        
        stats_text = f'Total: {total_merges} | Avg: {avg_merges:.1f}/day | Peak: {max_merges}'
        plt.figtext(0.5, 0.02, stats_text, ha='center', fontsize=10, style='italic')
        
        plt.tight_layout()
        plt.show()
    
    def analyze_repository(self, repo_url: str, days: int = 30):
        """Main method to analyze a repository."""
        try:
            # Parse repository URL
            owner, repo = self.parse_repo_url(repo_url)
            print(f"Analyzing repository: {owner}/{repo}")
            
            # Calculate date range
            since_date = datetime.now() - timedelta(days=days)
            print(f"Fetching merge data from {since_date.strftime('%Y-%m-%d')} to present...")
            
            # Fetch merged PRs
            merged_prs = self.fetch_merged_prs(owner, repo, since_date)
            print(f"Found {len(merged_prs)} merged pull requests in the specified period.")
            
            # Process daily counts
            daily_counts = self.process_daily_counts(merged_prs, days)
            
            # Generate graph
            self.generate_graph(daily_counts, owner, repo)
            
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error: {e}")
            sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Analyze and visualize GitHub repository merge analytics.',
        epilog='Example: python main.py --repo https://github.com/owner/repo'
    )
    
    parser.add_argument(
        '--repo', 
        required=True,
        help='GitHub repository URL (e.g., https://github.com/owner/repo or owner/repo)'
    )
    
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Number of days to analyze (default: 30)'
    )
    
    args = parser.parse_args()
    
    # Validate days parameter
    if args.days <= 0:
        print("Error: --days must be a positive integer")
        sys.exit(1)
    
    # Create analyzer and run analysis
    analyzer = GitHubAnalytics()
    analyzer.analyze_repository(args.repo, args.days)


if __name__ == '__main__':
    main()