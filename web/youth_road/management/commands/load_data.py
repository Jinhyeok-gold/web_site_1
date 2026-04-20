import os
import re
import pandas as pd
import json
from datetime import datetime
from django.core.management.base import BaseCommand
from youth_road.models import HousingProduct, FinanceProduct, WelfareProduct, HousingMarketData
class Command(BaseCommand):

    help = 'Load products from CSV/Excel folders into DB and Sync to Firebase (Pandas Enhanced)'

    def clean_numeric(self, value, default=0):
        """숫자 외의 문자(콤마, 한글 등)를 제거하고 숫자로 변환"""
        if value is None or pd.isna(value):
            return default
        if isinstance(value, (int, float)):
            return value
        # 숫자와 소수점만 남기기
        cleaned = re.sub(r'[^0-9.]', '', str(value))
        try:
            return float(cleaned) if '.' in cleaned else int(cleaned)
        except ValueError:
            return default

    def handle(self, *args, **options):
        base_path = 'data_storage'

        
        # 각 카테고리별 로드
        self.process_folder(os.path.join(base_path, 'housing'), 'housing')
        self.process_folder(os.path.join(base_path, 'finance'), 'finance')
        self.process_folder(os.path.join(base_path, 'welfare'), 'welfare')

    def process_folder(self, folder_path, category):
        if not os.path.exists(folder_path):
            return
        
        files = [f for f in os.listdir(folder_path) if f.endswith(('.csv', '.xlsx', '.xls'))]
        for filename in files:
            path = os.path.join(folder_path, filename)
            self.stdout.write(f"Processing {category.capitalize()}: {filename}")
            
            try:
                if filename.endswith('.csv'):
                    # 인코딩 에러 방지를 위해 여러 인코딩 시도
                    try:
                        df_dict = {'Sheet1': pd.read_csv(path, encoding='utf-8-sig')}
                    except UnicodeDecodeError:
                        df_dict = {'Sheet1': pd.read_csv(path, encoding='cp949')}
                else:
                    # 엑셀 파일의 모든 시트 읽기
                    df_dict = pd.read_excel(path, sheet_name=None)

                for sheet_name, df in df_dict.items():
                    if df.empty: continue
                    self.stdout.write(f"  - Reading Sheet: {sheet_name} ({len(df)} rows)")
                    self.save_to_db(df, category)
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing {filename}: {e}"))

    def save_to_db(self, df, category):
        # NaN 값을 None으로 변환하여 DB 저장 시 에러 방지
        df = df.where(pd.notnull(df), None)
        all_sync_data = []

        for _, row in df.iterrows():
            try:
                if category == 'housing':
                    self.handle_housing_row(row, all_sync_data)
                else:
                    self.handle_generic_row(row, category)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"  - Row Error: {e} | Data: {row.to_dict()}"))
                continue

    def handle_housing_row(self, row, sync_list):
        # 1. 통계 데이터인지 일반 공고인지 컬럼명으로 판단 (Smart Logic)
        cols = str(row.index.tolist())
        is_market_data = any(x in cols for x in ['경쟁률', '당첨', '평균', '가점', '나이'])

        if is_market_data:
            HousingMarketData.objects.update_or_create(
                region=row.get('지역') or row.get('시도명') or '전국',
                complex_name=row.get('단지명') or row.get('주택명') or '알 수 없음',
                data_year=datetime.now().year,
                defaults={
                    'avg_competition_rate': self.clean_numeric(row.get('경쟁률')),
                    'avg_winner_score': self.clean_numeric(row.get('당첨가점') or row.get('가점')),
                    'avg_winner_age': self.clean_numeric(row.get('당첨자나이') or row.get('평균연령')),
                    'sales_price': int(self.clean_numeric(row.get('분양가') or row.get('실거래가'))),
                    'raw_data': row.to_dict()
                }
            )
        else:
            manage_no = str(row.get('주택관리번호') or row.get('관리번호') or row.get('공고번호'))
            if not manage_no or manage_no == 'None': return

            obj, created = HousingProduct.objects.update_or_create(
                manage_no=manage_no,
                defaults={
                    'pblanc_no': row.get('공고번호'),
                    'title': row.get('주택명') or row.get('공고명'),
                    'category': row.get('주택구분코드명') or row.get('분류'),
                    'region': row.get('공급지역명') or row.get('지역'),
                    'location': row.get('공급위치'),
                    'url': row.get('홈페이지주소') or row.get('URL'),
                    'org': row.get('사업주체명') or row.get('기관'),
                    'raw_data': row.to_dict()
                }
            )
            sync_list.append({'id': manage_no, 'title': obj.title, 'region': obj.region})

    def handle_generic_row(self, row, category):
        """금융/복지 데이터를 공통 로직으로 처리"""
        if category == 'finance':
            prod_id = str(row.get('상품ID') or row.get('id'))
            if not prod_id or prod_id == 'None': return
            FinanceProduct.objects.update_or_create(
                product_id=prod_id,
                defaults={
                    'title': row.get('정책명') or row.get('상품명'),
                    'bank_nm': row.get('금융기관') or row.get('기관'),
                    'category': row.get('상품구분') or '금융지원',
                    'base_rate': self.clean_numeric(row.get('기본금리')),
                    'limit_amt': int(self.clean_numeric(row.get('대출한도'))),
                    'url': row.get('상세URL') or row.get('URL'),
                    'raw_data': row.to_dict()
                }
            )
        elif category == 'welfare':
            pol_id = str(row.get('정책ID') or row.get('id'))
            if not pol_id or pol_id == 'None': return
            WelfareProduct.objects.update_or_create(
                policy_id=pol_id,
                defaults={
                    'title': row.get('정책명') or row.get('상품명'),
                    'org_nm': row.get('주관기관') or row.get('기관'),
                    'benefit_desc': row.get('지원내용') or row.get('혜택'),
                    'target_desc': row.get('지원대상') or row.get('대상'),
                    'url': row.get('상세URL') or row.get('URL'),
                    'raw_data': row.to_dict()
                }
            )
