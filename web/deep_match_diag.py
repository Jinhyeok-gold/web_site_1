import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from youth_road.matching_service import MatchingEngine
from youth_road.services import OntongWelfareService
from django.contrib.auth.models import User

def deep_diagnose_matching():
    print("🧪 [Deep Match Diagnosis]")
    
    # 1. Check Service directly
    print("\n1. Testing OntongWelfareService.get_welfare_policies directly...")
    items = OntongWelfareService.get_welfare_policies(29, "Seoul")
    print(f"   Items found: {len(items)}")
    for i in items[:2]:
        print(f"   - {i['name']} ({i['org']})")

    # 2. Check Match Engine
    print("\n2. Simulating Match Engine (Full Report)...")
    # Mock a profile or get first user
    user = User.objects.first()
    if not user:
        print("   ❌ No user found, skip.")
        return
        
    class MockProfile:
        age = 29
        sido = "서울"
        sigungu = "강남구"
        income = 3000
        net_assets = 5000
        debt = 0
        subscription_count = 24
        subscription_amount = 2400000
        marital_status = "미혼"
        children_count = 0
    
    instance = MatchingEngine.map_profile_to_instance(MockProfile())
    report = MatchingEngine.get_full_report(instance)
    
    welfare = report['welfare']
    print(f"   Welfare Match Result: {welfare['top_1']['title']}")
    if welfare.get('list'):
        print(f"   Matches found: {len(welfare['list'])}")
    else:
        print("   ❌ NO welfare matches found in engine.")

if __name__ == "__main__":
    deep_diagnose_matching()
