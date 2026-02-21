class EconomySimulation:
    def __init__(self):
        self.reset()

    def reset(self):
        """초기 상태로 되돌립니다."""
        # 현실 고증: 대한민국 M2(광의통화)는 약 4000조 원 규모 (2024-2025 기준)
        self.money_supply = 4000.0      # 조 원
        self.prev_money_supply = 4000.0 # 이전 턴 통화량
        self.money_growth_rate = 0.0    # 통화량 증가율
        self.inflation_rate = 2.0     # %
        self.prev_inflation_rate = 2.0 # 이전 턴 물가상승률
        self.inflation_change = 0.0   # 물가상승률 변화량 (%p)
        self.interest_rate = 1.5      # % (현실적인 중립 금리 수준에서 시작)
        self.prev_interest_rate = 1.5 # 이전 턴 금리
        self.interest_change = 0.0    # 금리 변화량 (%p)
        self.happiness = 60.0         # 점수
        self.prev_happiness = 60.0    # 이전 턴 행복도
        self.happiness_change = 0.0   # 행복도 변화량
        self.turn = 1                 # 분기
        self.national_debt = 1000.0   # 국가 부채 (조 원) - 초기값 설정
        self.prev_national_debt = 1000.0 # 이전 턴 부채
        self.debt_growth_rate = 0.0   # 부채 증가율
        self.stimulus_velocity_impact = 0.0 # 소비쿠폰의 단기 물가 충격 (화폐유통속도)
        self.gdp = 2200.0             # 명목 GDP (조 원)
        self.prev_gdp = 2200.0        # 이전 턴 GDP
        self.gdp_growth_rate = 0.5    # 분기별 경제 성장률 (%)
        self.prev_stimulus = 0.0      # 이전 턴 지원금 규모 (적응 효과 구현용)
        self.real_purchasing_power = 100.0 # 실질 구매력 (기준 100)
        self.prev_real_purchasing_power = 100.0 # 이전 턴 실질 구매력
        self.real_purchasing_power_change = 0.0 # 실질 구매력 변화량

    def apply_policy(self, stimulus_amount: float):
        """재난지원금 정책 반영"""
        # 소비쿠폰은 일반 예산이 아닌 적자 국채(부채)로 조달한다고 가정
        self.national_debt += stimulus_amount

        if stimulus_amount > 0:
            # 승수효과: 현금 살포는 신용 창출보다 승수효과가 낮을 수 있음 (저축 등)
            multiplier = 1.2
            self.money_supply += stimulus_amount * multiplier
            
            # GDP 부양 효과 (소비쿠폰)
            # 소비쿠폰은 강제 소비를 유도하므로 단기 GDP 부양 효과가 있음
            # 투입 금액의 50% 정도만 실질적인 추가 부가가치 창출로 연결된다고 가정(나머지는 저축 등으로 빠짐)
            fiscal_multiplier = 0.5
            # 인플레이션이 높으면 돈을 풀어도 물가만 오르고 실질 GDP 부양 효과는 떨어짐 (공급 제약)
            if self.inflation_rate > 3.0:
                fiscal_multiplier = 0.2  # 이미 물가가 높으면 부양 효과 급감

            self.gdp += stimulus_amount * fiscal_multiplier

            # 화폐 유통 속도(Velocity) 효과
            # 금액 비중은 작아도(14조/4000조), 현금 살포는 단기 소비 심리를 자극해 물가 압력을 줌
            # (14조 투입 시 약 0.07%p 정도의 심리적 물가 압력만 발생하도록 현실화)
            self.stimulus_velocity_impact = stimulus_amount * 0.005
            
            # 효용 한계 체감
            # 매번 똑같은 돈을 주면 사람들은 당연하게 여겨 행복도가 오르지 않음.
            # "이전보다 더 많이 줬을 때"만 추가적인 행복을 느낌.
            stimulus_delta = stimulus_amount - self.prev_stimulus
            if stimulus_delta > 0:
                self.happiness += (stimulus_delta ** 0.7) * 0.5
            
            self.prev_stimulus = stimulus_amount

    def calculate_market_reaction(self):
        """시장 반응 계산 (핵심 로직)"""
        
        # GDP 대비 부채 비율 계산
        debt_to_gdp_ratio = (self.national_debt / self.gdp) * 100.0

        # --- 1. GDP 변동 계산 (자연 성장 + 금리 영향) ---
        
        # 잠재 성장률 (분기당 0.5% -> 연율 약 2.0% 가정)
        potential_growth = 0.5
        
        # 부채 위기 효과 (구축 효과): 부채가 90%를 넘으면 성장률을 갉아먹음
        debt_drag = 0.0
        if debt_to_gdp_ratio > 90.0:
            debt_drag = (debt_to_gdp_ratio - 90.0) * 0.05

        # 금리 효과: 금리가 높으면 투자/소비 위축으로 성장 둔화
        # 중립금리(2.0) 대비 1%p 상승 시 성장률 0.1%p 하락 가정
        rate_drag = (self.interest_rate - 2.0) * 0.1

        # 인플레이션 불확실성 효과: 고물가는 기업 투자를 위축시킴 (스태그플레이션 압력)
        inflation_drag = 0.0
        if self.inflation_rate > 4.0:
            inflation_drag = (self.inflation_rate - 4.0) * 0.15
        
        # 이번 턴의 성장률 결정 (정책으로 인한 GDP 점프는 apply_policy에서 이미 반영됨)
        current_growth = potential_growth - rate_drag - debt_drag - inflation_drag
        
        # GDP 업데이트
        self.gdp = self.gdp * (1 + current_growth / 100.0)
        
        # 성장률 기록 (전분기 대비)
        if self.prev_gdp > 0:
            self.gdp_growth_rate = ((self.gdp - self.prev_gdp) / self.prev_gdp) * 100
        
        self.prev_gdp = self.gdp

        # --- 2. 인플레이션 계산 (통화량 증가율 + 금리 효과 + 관성) ---
        
        # 통화량 증가율
        money_growth_quarterly = 0
        if self.prev_money_supply > 0:
            money_growth_quarterly = ((self.money_supply - self.prev_money_supply) / self.prev_money_supply) * 100
        self.money_growth_rate = money_growth_quarterly

        # [단위 보정] 인플레이션은 '연율(Annual)' 개념이므로, 분기 변동분을 연율로 환산하여 계산
        money_growth_annual = money_growth_quarterly * 4
        potential_growth_annual = potential_growth * 4  # 0.5 * 4 = 2.0%

        # 화폐적 요인: 경제 성장률(GDP)에 의한 통화 흡수
        # 연율 기준 통화량이 잠재성장률보다 빠르게 늘면 인플레 압력
        excess_money_growth = money_growth_annual - potential_growth_annual

        # 실물적 요인: GDP Gap 효과 (필립스 곡선 반영)
        # 실제 성장률(연율 환산)이 잠재 성장률을 초과하면 물가 상승 압력
        gdp_gap_annual = (self.gdp_growth_rate * 4) - potential_growth_annual
        phillips_curve_effect = gdp_gap_annual * 0.1

        # 금리 효과: 중립 금리(2.0%)보다 높으면 물가 억제 효과
        rate_effect = (self.interest_rate - 2.0) * 0.8
        
        # 신규 인플레이션 압력 계산
        # 기본 2.0% + 초과 통화량(계수 조정) + GDP Gap + 단기 유통속도 충격 - 금리 효과
        target_inflation = 2.0 + (excess_money_growth * 0.2) + phillips_curve_effect + self.stimulus_velocity_impact - rate_effect
        
        # 인플레이션: 관성(0.8) + 신규 압력(0.2)
        # 물가는 경직성(Stickiness)이 강함. 이전 분기 물가의 영향을 80%로 설정해 급격한 변동 방지
        self.inflation_rate = (self.inflation_rate * 0.8) + (target_inflation * 0.2)

        # 실질 구매력 업데이트 (분기별 물가 상승 반영)
        # inflation_rate는 연율(%)이므로 4로 나누어 분기 변동률 적용
        quarterly_inflation = self.inflation_rate / 4
        self.real_purchasing_power = self.real_purchasing_power / (1 + quarterly_inflation / 100.0)

        # 이전 분기 통화량 저장
        self.prev_money_supply = self.money_supply

        # --- 2.5 부채 효과 (이자 비용 및 재정 건전성) ---

        # 부채 비율이 60%를 넘어가면 재정 건전성 우려로 행복도 하락 (EU 권고 기준 등 참고)
        # 부채 패널티 강화: 선형(-)이 아니라 제곱(--)으로 패널티를 주어, 부채가 쌓일수록 공포감 조성
        if debt_to_gdp_ratio > 60.0:
            self.happiness -= ((debt_to_gdp_ratio - 60.0) ** 1.2) * 0.1

        # --- 3. 금리 조정 (중앙은행 자동 대응) ---
        
        if self.inflation_rate > 3.0:
            self.interest_rate = min(10.0, self.interest_rate + 0.25)
            # 금리 인상 고통
            self.happiness -= (2.0 + self.interest_rate * 0.5)
        elif self.inflation_rate < 1.0:
            self.interest_rate = max(0.0, self.interest_rate - 0.25)
            
        # 리스크 프리미엄: 부채 비율이 100%를 넘으면 국가 신용 위험으로 금리 하한선 발생
        # (경제가 안 좋아도 금리를 못 내리는 상황 연출)
        if debt_to_gdp_ratio > 100.0:
            risk_premium_rate = 2.0 + (debt_to_gdp_ratio - 100.0) * 0.1
            self.interest_rate = max(self.interest_rate, risk_premium_rate)
            
        # 단기 충격 초기화 (일회성)
        self.stimulus_velocity_impact = 0.0

        # --- 4. 행복도 조정 ---
        # 경제 성장에 따른 행복도 변화
        if self.gdp_growth_rate > 0.75:
            self.happiness += self.gdp_growth_rate * 1.5
        else:
            self.happiness -= abs(self.gdp_growth_rate) * 3.0 # 역성장은 고통이 큼

        # 가계 부채 고통 (이자 부담): 가계 부채가 많은 상황(GDP 대비 100% 가정)에서 금리 상승은 치명적
        # 금리가 2.0%를 초과하면 이자 상환 부담으로 행복도가 급격히 하락
        if self.interest_rate > 2.0:
            self.happiness -= ((self.interest_rate - 2.0) ** 2) * 1.5

        # 고물가 고통
        if self.inflation_rate > 4.0:
            # 물가가 높을수록 행복도가 기하급수적으로(제곱) 떨어짐
            self.happiness -= (self.inflation_rate ** 2) * 0.5

        # 실질 구매력 변화에 따른 행복도 체감
        # 구매력이 떨어지면(물가 상승 > 소득 상승) 삶의 질 저하로 행복도 급감
        pp_delta = self.real_purchasing_power - self.prev_real_purchasing_power
        if pp_delta < 0:
            # 손실 회피 편향: 잃어버린 구매력에 대해 더 큰 고통을 느낌
            self.happiness -= abs(pp_delta) * 1.2
        else:
            # 구매력 상승은 행복을 주지만, 하락만큼 민감하진 않음
            self.happiness += pp_delta * 0.5

        # 행복의 평균 회귀 (Mean Reversion)
        # 특별한 호재가 없으면 행복도는 서서히 기본값(60)으로 돌아가려는 성질이 있음
        self.happiness = self.happiness * 0.9 + 60.0 * 0.1
        
        # 범위 제한
        self.happiness = max(0, min(100, self.happiness))
        
        # 부채 증가율 계산 및 이전 부채 업데이트
        if self.prev_national_debt > 0:
            self.debt_growth_rate = ((self.national_debt - self.prev_national_debt) / self.prev_national_debt) * 100
        self.prev_national_debt = self.national_debt

        # 물가 및 금리 변화량 계산
        self.inflation_change = self.inflation_rate - self.prev_inflation_rate
        self.interest_change = self.interest_rate - self.prev_interest_rate
        
        # 행복도 및 구매력 변화량 계산
        self.happiness_change = self.happiness - self.prev_happiness
        self.real_purchasing_power_change = self.real_purchasing_power - self.prev_real_purchasing_power
        
        self.prev_inflation_rate = self.inflation_rate
        self.prev_interest_rate = self.interest_rate
        self.prev_happiness = self.happiness
        self.prev_real_purchasing_power = self.real_purchasing_power

        self.turn += 1

    def get_state(self):
        """현재 상태를 딕셔너리로 반환 (API 응답용)"""
        return {
            "turn": self.turn,
            "money_supply": round(self.money_supply, 1),
            "money_growth_rate": round(self.money_growth_rate, 2),
            "inflation_rate": round(self.inflation_rate, 2),
            "inflation_change": round(self.inflation_change, 2),
            "real_purchasing_power": round(self.real_purchasing_power, 1),
            "real_purchasing_power_change": round(self.real_purchasing_power_change, 2),
            "interest_rate": round(self.interest_rate, 2),
            "interest_change": round(self.interest_change, 2),
            "happiness": round(self.happiness, 1),
            "happiness_change": round(self.happiness_change, 2),
            "national_debt": round(self.national_debt, 1),
            "debt_growth_rate": round(self.debt_growth_rate, 2),
            "gdp": round(self.gdp, 1),
            "gdp_growth_rate": round(self.gdp_growth_rate, 2)
        }