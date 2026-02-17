import random

class EconomySimulation:
    def __init__(self):
        self.reset()

    def reset(self):
        """초기 상태로 되돌립니다."""
        # 현실 고증: 대한민국 M2(광의통화)는 약 4000조 원 규모 (2024-2025 기준)
        # 예산은 약 650조 원 규모
        self.money_supply = 4000.0      # 조 원
        self.prev_money_supply = 4000.0 # 이전 턴 통화량
        self.inflation_rate = 2.0     # %
        self.interest_rate = 1.5      # % (현실적인 중립 금리 수준에서 시작)
        self.happiness = 60.0         # 점수
        self.turn = 1                 # 분기
        self.budget = 650.0           # 국가 예산 (조 원)
        self.stimulus_velocity_impact = 0.0 # 재난지원금의 단기 물가 충격 (화폐유통속도)

    def apply_policy(self, stimulus_amount: float):
        """재난지원금 정책 반영"""
        # 예산 부족 시 남은 예산만큼만 집행
        if stimulus_amount > self.budget:
            stimulus_amount = self.budget

        self.budget -= stimulus_amount

        if stimulus_amount > 0:
            # 승수효과: 현금 살포는 신용 창출보다 승수효과가 낮을 수 있음 (저축 등)
            multiplier = 1.2
            self.money_supply += stimulus_amount * multiplier
            
            # [현실성 보강] 화폐 유통 속도(Velocity) 효과
            # 금액 비중은 작아도(14조/4000조), 현금 살포는 단기 소비 심리를 자극해 물가 압력을 줌
            # 14조 투입 시 약 0.2~0.3%p 정도의 추가 인플레 압력을 주도록 설정
            self.stimulus_velocity_impact = stimulus_amount * 0.02
            
            # 단기적 행복 상승 (한계효용 체감 적용: 금액이 커질수록 행복 증가폭 감소)
            self.happiness += (stimulus_amount ** 0.7) * 0.5

    def calculate_market_reaction(self):
        """시장 반응 계산 (핵심 로직)"""
        # --- 인플레이션 계산 (통화량 증가율 + 금리 효과 + 관성) ---
        
        # 통화량 증가율
        money_growth_rate = 0
        if self.prev_money_supply > 0:
            money_growth_rate = ((self.money_supply - self.prev_money_supply) / self.prev_money_supply) * 100

        # [현실성 보강] 경제 성장률(GDP)에 의한 통화 흡수
        # 경제가 성장하면(분기당 0.5% 가정) 통화가 늘어도 물가가 바로 오르지 않음
        potential_gdp_growth = 0.5
        excess_money_growth = money_growth_rate - potential_gdp_growth

        # 금리 효과: 중립 금리(2.0%)보다 높으면 물가 억제 효과
        rate_effect = (self.interest_rate - 2.0) * 0.8
        
        # 신규 압력
        # 기본 2.0% + 초과 통화량 + 단기 유통속도 충격 - 금리 효과
        target_inflation = 2.0 + (excess_money_growth * 0.5) + self.stimulus_velocity_impact - rate_effect
        
        # 인플레이션: 관성(0.6) + 신규 압력(0.4) - 물가는 서서히 변함
        self.inflation_rate = (self.inflation_rate * 0.6) + (target_inflation * 0.4)

        self.prev_money_supply = self.money_supply

        # --- 금리 조정 (중앙은행 자동 대응) ---
        
        if self.inflation_rate > 3.0:
            self.interest_rate = min(10.0, self.interest_rate + 0.25)
            # 금리 인상 고통
            self.happiness -= (2.0 + self.interest_rate * 0.5)
        elif self.inflation_rate < 1.0:
            self.interest_rate = max(0.0, self.interest_rate - 0.25)
            
        # 단기 충격 초기화 (일회성)
        self.stimulus_velocity_impact = 0.0

        # --- 행복도 조정 ---
        # 고금리 고통 (이자 부담): 금리가 2.0%를 초과하면 매 턴 행복도 감소
        if self.interest_rate > 2.0:
            self.happiness -= ((self.interest_rate - 2.0) ** 2) * 1.0

        # 고물가 패널티
        if self.inflation_rate > 4.0:
            # 물가가 높을수록 행복도가 기하급수적으로(제곱) 떨어짐
            self.happiness -= (self.inflation_rate ** 2) * 0.5
        
        # 범위 제한
        self.happiness = max(0, min(100, self.happiness))
        
        self.turn += 1

    def get_state(self):
        """현재 상태를 딕셔너리로 반환 (API 응답용)"""
        return {
            "turn": self.turn,
            "money_supply": round(self.money_supply, 1),
            "inflation_rate": round(self.inflation_rate, 2),
            "interest_rate": round(self.interest_rate, 2),
            "happiness": round(self.happiness, 1),
            "budget": round(self.budget, 1)
        }