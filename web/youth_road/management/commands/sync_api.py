import os
import requests
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from django.core.management.base import BaseCommand
from youth_road.models import HousingProduct, FinanceProduct, WelfareProduct
# from youth_road.firebase_service import FirebaseManager (Removed)
from urllib.parse import unquote

import os
from django.core.management.base import BaseCommand
from youth_road.services import (
    PublicDataHousingService, 
    SubscriptionHomeService, 
    FssFinanceService, 
    OntongWelfareService
)

class Command(BaseCommand):
    help = 'Masterpiece Triple-Split Sync Engine v20 - Consolidated Edition'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("=== Triple-Split Sync Engine v20 Consolidated Started ==="))

        # [STEP 1] 주거 (LH, SH, MyHome, ApplyHome)
        self.stdout.write("Syncing Housing Data...")
        try:
            lh_count = PublicDataHousingService.sync_all()
            self.stdout.write(self.style.SUCCESS(f"  + Housing(LH/SH/MyHome): {lh_count} synced."))
        except Exception as e:
            self.stderr.write(f"Housing Sync Error (LH/SH): {e}")

        try:
            sub_count = SubscriptionHomeService.sync_all()
            self.stdout.write(self.style.SUCCESS(f"  + Housing(ApplyHome): {sub_count} synced."))
        except Exception as e:
            self.stderr.write(f"Housing Sync Error (ApplyHome): {e}")

        # [STEP 2] 금융 (HUG, 시중은행 FSS)
        self.stdout.write("Syncing Finance Data...")
        try:
            fin_count = FssFinanceService.sync_all()
            self.stdout.write(self.style.SUCCESS(f"  + Finance(HUG/FSS): {fin_count} synced."))
        except Exception as e:
            self.stderr.write(f"Finance Sync Error: {e}")

        # [STEP 3] 복지/정책 (온통청년 최종 연동 파라미터 적용)
        self.stdout.write("Syncing Welfare Data...")
        try:
            # 전국 단위로 우선 동기화
            wel_count = OntongWelfareService.sync_all(age=29, region_name='전국')
            self.stdout.write(self.style.SUCCESS(f"  + Welfare(Bokjiro/YouthCenter): {wel_count} synced."))
        except Exception as e:
            self.stderr.write(f"Welfare Sync Error: {e}")

        self.stdout.write(self.style.SUCCESS("🏆 ALL SYSTEM INTEGRATION COMPLETE (v20.0 - Consolidated)!"))
