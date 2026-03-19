#!/usr/bin/env python3
# scripts/generate_report.py - Generate performance report

import asyncio
import json
from datetime import datetime, timedelta
from src.core.engine.performance_tracker import PerformanceTracker
from src.services.firebase import FirebaseService

async def generate_report():
    """Generate performance report"""
    print("📊 Generating performance report...")
    
    tracker = PerformanceTracker()
    firebase = FirebaseService()
    firebase.initialize()
    
    # Get metrics
    report = await tracker.get_roi_report()
    
    # Add timestamp
    report['generated_at'] = datetime.now().isoformat()
    report['period'] = 'last_30_days'
    
    # Save report
    with open(f"reports/report_{datetime.now().strftime('%Y%m%d')}.json", 'w') as f:
        json.dump(report, f, indent=2)
        
    # Save to Firebase
    await firebase.db.collection('reports').add(report)
    
    print("✅ Report generated")
    print(json.dumps(report, indent=2))
    
if __name__ == "__main__":
    asyncio.run(generate_report())