import random
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class EconomyState:
    """경제 지표 상태 관리 (Data Class)"""
    money_supply: float = 1000.0
    prev_money_supply: float = 1000.0
    money_multiplier: float = 5.0
    inflation_rate: float = 2.0
    interest_rate: float = 1.5
    gdp: float = 2000.0
    gdp_growth_rate: float = 2.5
    population: int = 5170
    approval_rating: float = 40.0
    is_game_over: bool = False
    is_victory: bool = False
    policy_gdp_bonus: float = 0.0
    budget: float = 500.0
    tax_rate: float = 10.0
    national_debt: float = 0.0
    is_credit_downgraded: bool = False
    cumulative_rnd: float = 0.0
    productivity_bonus: float = 0.0
    innovation_triggered: bool = False
    welfare_cost: float = 0.0
    exchange_rate: float = 1200.0
    exports: float = 0.0
    imports: float = 0.0
    foreign_reserves: float = 400.0 # 외환 보유고 (억 달러)
    exchange_rate_defense: float = 0.0 # 환율 방어 효과 (이번 턴)
    real_estate_price: float = 100.0 # 부동산 가격 지수 (기준 100)
    unemployment_rate: float = 3.0  # 실업률 (%)
    ltv_dti_rate: float = 0.0 # LTV/DTI 규제 강도 (0~100%)
    turn: int = 1

def require_budget(policy_name):
    """예산 부족 여부를 확인하는 데코레이터"""
    def decorator(func):
        def wrapper(self, state, amount):
            if amount <= 0:
                return
            if state.budget >= amount:
                func(self, state, amount)
            else:
                print(f"예산 부족으로 {policy_name}을(를) 실행할 수 없습니다.")
        return wrapper
    return decorator

class PolicyStrategy(ABC):
    """정책 전략 인터페이스"""
    @abstractmethod
    def execute(self, state: EconomyState, amount: float):
        pass

class DebtRepaymentPolicy(PolicyStrategy):
    @require_budget("부채 상환")
    def execute(self, state: EconomyState, amount: float):
        actual_repayment = min(amount, state.national_debt)
        state.budget -= actual_repayment
        state.national_debt -= actual_repayment

class StimulusPolicy(PolicyStrategy):
    @require_budget("재난지원금")
    def execute(self, state: EconomyState, amount: float):
        added_money_supply = amount * state.money_multiplier
        state.money_supply += added_money_supply
        state.approval_rating += (amount * 0.5)
        state.budget -= amount

class TaxCutPolicy(PolicyStrategy):
    @require_budget("법인세 인하")
    def execute(self, state: EconomyState, amount: float):
        state.money_supply += amount * (state.money_multiplier * 0.4)
        state.policy_gdp_bonus += (amount * 0.02)
        state.approval_rating += (amount * 0.1)
        state.budget -= amount

class PublicWorksPolicy(PolicyStrategy):
    @require_budget("공공 사업")
    def execute(self, state: EconomyState, amount: float):
        state.money_supply += amount * state.money_multiplier
        state.policy_gdp_bonus += (amount * 0.05)
        state.approval_rating += (amount * 0.3)
        state.budget -= amount

class RnDPolicy(PolicyStrategy):
    @require_budget("R&D 투자")
    def execute(self, state: EconomyState, amount: float):
        # R&D는 장기적인 성장 동력 확보 (높은 GDP 보너스, 낮은 지지율 상승)
        state.money_supply += amount * state.money_multiplier
        state.policy_gdp_bonus += (amount * 0.08) # 공공사업(0.05)보다 높은 성장 효율
        state.approval_rating += (amount * 0.1)   # 당장의 지지율 효과는 낮음
        state.budget -= amount
        state.cumulative_rnd += amount
        
class HousingSupplyPolicy(PolicyStrategy):
    @require_budget("주택 건설")
    def execute(self, state: EconomyState, amount: float):
        # 주택 건설: 단기적인 집값 하락 효과
        # 10조 투자 시 부동산 지수 3 하락
        state.real_estate_price -= (amount * 0.3)
        state.budget -= amount

class CurrencyDefensePolicy(PolicyStrategy):
    def execute(self, state: EconomyState, amount: float):
        if amount <= 0:
            return
        # amount 단위: 억 달러
        if state.foreign_reserves >= amount:
            state.foreign_reserves -= amount
            # 1억 달러당 환율 5원 하락(방어) 효과 가정
            state.exchange_rate_defense += (amount * 5.0)

class PolicyHandler:
    """정책 실행기 (Context)"""
    def __init__(self, state: EconomyState):
        self.state = state
        self.strategies = {
            "debt_repayment": DebtRepaymentPolicy(),
            "stimulus": StimulusPolicy(),
            "tax_cut": TaxCutPolicy(),
            "public_works": PublicWorksPolicy(),
            "rnd": RnDPolicy(),
            "housing_supply": HousingSupplyPolicy(),
            "currency_defense": CurrencyDefensePolicy(),
        }

    def apply(self, stimulus: float, tax_cut: float, public_works: float, tax_rate: float, bond_issuance: float, debt_repayment: float, rnd_investment: float, currency_defense: float, housing_supply: float, ltv_dti_rate: float):
        self.state.policy_gdp_bonus = 0.0 # 초기화
        self.state.tax_rate = tax_rate    # 이번 턴 세율 설정
        self.state.exchange_rate_defense = 0.0 # 환율 방어 효과 초기화
        self.state.ltv_dti_rate = ltv_dti_rate # LTV/DTI 규제 설정

        # 0. 정책 실행
        if bond_issuance > 0:
            self.state.budget += bond_issuance
            self.state.national_debt += bond_issuance

        # 전략 실행
        self.strategies["debt_repayment"].execute(self.state, debt_repayment)
        self.strategies["stimulus"].execute(self.state, stimulus)
        self.strategies["tax_cut"].execute(self.state, tax_cut)
        self.strategies["public_works"].execute(self.state, public_works)
        self.strategies["rnd"].execute(self.state, rnd_investment)
        self.strategies["housing_supply"].execute(self.state, housing_supply)
        self.strategies["currency_defense"].execute(self.state, currency_defense)

class MarketSimulator:
    """시장 반응 및 경제 지표 계산 담당"""
    def __init__(self, state: EconomyState):
        self.state = state

    def update(self):
        # 0. 예산 자동 회복 (세수) - 설정된 세율에 따라 징수
        tax_revenue = self.state.gdp * (self.state.tax_rate / 100)
        self.state.budget += tax_revenue

        # 0-1. 국채 이자 지급 (기준 금리 + 1.0% 가산 금리 적용)
        interest_payment = self.state.national_debt * ((self.state.interest_rate + 1.0) / 100)
        self.state.budget -= interest_payment

        # 0-2. 고령화로 인한 복지 비용 증가 (자동 지출)
        # 턴이 지날수록 비용 증가 (기본 10조 + 턴당 2조 증가)
        self.state.welfare_cost = 10.0 + (self.state.turn * 2.0)
        self.state.budget -= self.state.welfare_cost

        # 1. 인플레이션 계산 (통화량 증가 -> 물가 상승)
        inflation_pressure = (self.state.money_supply - 1000) * 0.01
        self.state.inflation_rate = 2.0 + inflation_pressure + random.uniform(-0.2, 0.2)

        # 2. 금리 조정 (중앙은행 자동 대응)
        # 물가가 3.5% 넘으면 금리 인상, 1.0% 미만이면 인하
        if self.state.inflation_rate > 3.5:
            self.state.interest_rate = min(10.0, self.state.interest_rate + 0.25)
            self.state.approval_rating -= 2  # 금리 인상에 따른 지지율 하락
        elif self.state.inflation_rate < 1.0:
            self.state.interest_rate = max(0.0, self.state.interest_rate - 0.25)

        # 국가 채무 위기 (GDP 대비 100% 초과)
        debt_ratio = self.state.national_debt / self.state.gdp if self.state.gdp > 0 else 0
        if debt_ratio > 1.0:
            self.state.is_credit_downgraded = True
            # 신용등급 강등 -> 이자율 폭등 (최소 15% 보장 + 부채 비율에 따른 가산)
            target_rate = 15.0 + (debt_ratio - 1.0) * 20.0
            self.state.interest_rate = max(self.state.interest_rate, target_rate)
            self.state.approval_rating -= 3.0 # 신용 하락으로 인한 지지율 감소
        else:
            self.state.is_credit_downgraded = False

        # 금리에 따른 통화 승수 변화 (금리가 오르면 대출 감소 -> 승수 하락)
        self.state.money_multiplier = max(2.0, 5.0 - (self.state.interest_rate - 1.5) * 0.5)

        # 기술 혁신 이벤트 (R&D 누적 50조 달성 시)
        self.state.innovation_triggered = False
        if self.state.cumulative_rnd >= 50.0:
            while self.state.cumulative_rnd >= 50.0:
                self.state.cumulative_rnd -= 50.0
                self.state.productivity_bonus += 0.5 # 영구적 성장률 0.5%p 증가
                self.state.innovation_triggered = True
                self.state.approval_rating += 5.0 # 혁신 성공 지지율 보너스

        # 3. 지지율 조정 (고물가 패널티)
        if self.state.inflation_rate > 4.0:
            self.state.approval_rating -= (self.state.inflation_rate * 1.5)
        
        # 세율에 따른 지지율 및 성장률 보정 (기준 10%)
        tax_impact = (10.0 - self.state.tax_rate)
        self.state.approval_rating += (tax_impact * 0.5) # 1%p 인상 시 지지율 0.5 하락

        # --- 무역 시스템 (환율 및 수출입) ---
        # 1. 환율 계산 (기본 1200원)
        # 금리 상승 -> 원화 가치 상승 -> 환율 하락
        # 물가 상승 -> 원화 가치 하락 -> 환율 상승
        rate_change_interest = (self.state.interest_rate - 1.5) * -50.0
        rate_change_inflation = (self.state.inflation_rate - 2.0) * 30.0
        random_fluctuation = random.uniform(-20, 20)
        
        # 환율 방어 효과 반영 (exchange_rate_defense 만큼 환율 하락)
        self.state.exchange_rate = 1200.0 + rate_change_interest + rate_change_inflation + random_fluctuation - self.state.exchange_rate_defense
        self.state.exchange_rate = max(800.0, min(2000.0, self.state.exchange_rate))

        # 2. 수출입 계산 (GDP의 40%가 무역 규모라고 가정)
        # 환율 상승(원화 약세) -> 수출 증가, 수입 감소
        base_trade = self.state.gdp * 0.4
        exchange_ratio = self.state.exchange_rate / 1200.0
        
        self.state.exports = base_trade * (exchange_ratio ** 0.5)
        self.state.imports = base_trade * ((1 / exchange_ratio) ** 0.5)
        
        net_exports = self.state.exports - self.state.imports
        trade_growth_bonus = (net_exports / self.state.gdp) * 5.0 # 순수출의 성장 기여도

        # 3. 외환 보유고 변동 (경상수지 흑자 -> 증가, 적자 -> 감소)
        # 순수출(조 원)을 달러(억 달러)로 환산하여 반영
        # 1조 원 = 10000억 원. 환율 1200원이면 약 8.3억 달러.
        self.state.foreign_reserves += (net_exports * 10000 / self.state.exchange_rate)

        # --- 부동산 시장 ---
        # 금리가 낮으면 유동성 증가로 집값 상승 (기준 금리 2.5% 대비)
        # 금리 1%p 하락 시 지수 약 4 상승 가정
        interest_effect = (2.5 - self.state.interest_rate) * 4.0
        # 물가 상승도 집값 상승 견인
        inflation_effect = self.state.inflation_rate * 0.8
        random_fluctuation = random.uniform(-2.0, 2.0)
        
        # LTV/DTI 규제 효과 (강도 0~100%)
        # 강도가 높을수록 집값 상승 억제 (예: 50% -> 지수 10 하락 압력)
        regulation_effect = self.state.ltv_dti_rate * 0.2
        self.state.real_estate_price -= regulation_effect
        self.state.real_estate_price += (interest_effect + inflation_effect + random_fluctuation)
        self.state.real_estate_price = max(50.0, self.state.real_estate_price) # 하한선

        # 집값 폭등에 따른 지지율 하락 (지수 120 초과 시 페널티)
        if self.state.real_estate_price > 120.0:
            housing_penalty = (self.state.real_estate_price - 120.0) * 0.5
            self.state.approval_rating -= housing_penalty
            
        # --- 실업률 ---
        # 경제 성장률이 낮을수록 실업률 증가
        # gdp 성장률 1%p 하락 시 실업률 0.3%p 상승
        gdp_impact = (self.state.gdp_growth_rate - 2.0) * -0.3
        self.state.unemployment_rate += gdp_impact
        self.state.unemployment_rate = max(0.0, min(10.0, self.state.unemployment_rate)) # 실업률 범위 제한 (0~10%)
        # 실업률 증가는 지지율 하락으로 연결
        self.state.approval_rating -= (self.state.unemployment_rate * 0.2)

        # 4. 경제 성장률 (GDP) 계산
        # 통화량 증가율 계산
        money_growth_pct = 0
        if self.state.prev_money_supply > 0:
            money_growth_pct = ((self.state.money_supply - self.state.prev_money_supply) / self.state.prev_money_supply) * 100
        
        # 스태그플레이션 로직
        inflation_penalty = 0
        if self.state.inflation_rate > 5.0:
            inflation_penalty = (self.state.inflation_rate - 5.0) * 1.0

        # 자본 이탈 (Capital Flight)
        capital_flight_penalty = 0.0
        if self.state.tax_rate > 20.0:
            excess_tax = self.state.tax_rate - 20.0
            capital_flight_penalty = excess_tax * 0.5
            self.state.approval_rating -= (excess_tax * 1.0)

        # 고령화로 인한 생산 가능 인구 감소 페널티 (턴이 지날수록 심화)
        aging_penalty = self.state.turn * 0.05

        # 기본 성장 2.0% + 통화량 증가 효과 - 금리 부담 - 인플레이션 페널티 - 자본 이탈 - 고령화 페널티 + 정책 보너스 + 세율 영향 + 생산성 보너스 + 무역 수지 보너스 + 랜덤 요인
        self.state.gdp_growth_rate = 2.0 + (money_growth_pct * 0.2) - ((self.state.interest_rate - 1.5) * 0.5) - inflation_penalty - capital_flight_penalty - aging_penalty + self.state.policy_gdp_bonus + (tax_impact * 0.1) + self.state.productivity_bonus + trade_growth_bonus + random.uniform(-0.5, 0.5)
        # LTV/DTI 규제로 인한 대출 축소 -> 소비/투자 위축 페널티
        lending_restriction_penalty = self.state.ltv_dti_rate * 0.01

        # 기본 성장 2.0% + 통화량 증가 효과 - 금리 부담 - 인플레이션 페널티 - 자본 이탈 - 고령화 페널티 - 대출 규제 페널티 + 정책 보너스 + 세율 영향 + 생산성 보너스 + 무역 수지 보너스 + 랜덤 요인
        self.state.gdp_growth_rate = 2.0 + (money_growth_pct * 0.2) - ((self.state.interest_rate - 1.5) * 0.5) - inflation_penalty - capital_flight_penalty - aging_penalty - lending_restriction_penalty + self.state.policy_gdp_bonus + (tax_impact * 0.1) + self.state.productivity_bonus + trade_growth_bonus + random.uniform(-0.5, 0.5)
        self.state.gdp = self.state.gdp * (1 + self.state.gdp_growth_rate / 100)

        # 5. 인구수 변동 (자연 증감)
        self.state.population += int(random.uniform(-2, 5))

        # 다음 턴 계산을 위해 현재 통화량 저장
        self.state.prev_money_supply = self.state.money_supply

        # 범위 제한
        self.state.approval_rating = max(0, min(100, self.state.approval_rating))

        # 게임 오버 체크 (지지율 5% 미만)
        if self.state.approval_rating < 5.0:
            self.state.is_game_over = True

        # 승리 체크 (20턴 생존)
        if self.state.turn >= 20 and not self.state.is_game_over:
            self.state.is_victory = True

        self.state.turn += 1

class EconomySimulation:
    def __init__(self):
        self.reset()

    def reset(self):
        """게임을 초기 상태로 되돌립니다."""
        self.state = EconomyState()
        self.policy_handler = PolicyHandler(self.state)
        self.market_simulator = MarketSimulator(self.state)

    def apply_policy(self, stimulus: float, tax_cut: float, public_works: float, tax_rate: float, bond_issuance: float, debt_repayment: float, rnd_investment: float, currency_defense: float, housing_supply: float, ltv_dti_rate: float):
        """다양한 경제 정책 반영 (PolicyHandler 위임)"""
        self.policy_handler.apply(stimulus, tax_cut, public_works, tax_rate, bond_issuance, debt_repayment, rnd_investment, currency_defense)
        self.policy_handler.apply(stimulus, tax_cut, public_works, tax_rate, bond_issuance, debt_repayment, rnd_investment, currency_defense, housing_supply, ltv_dti_rate)

    def calculate_market_reaction(self):
        """시장 반응 계산 (MarketSimulator 위임)"""
        self.market_simulator.update()

    def get_state(self):
        """현재 상태를 딕셔너리로 반환 (API 응답용)"""
        s = self.state
        return {
            "turn": s.turn,
            "budget": round(s.budget, 1),
            "tax_rate": s.tax_rate,
            "ltv_dti_rate": s.ltv_dti_rate,
            "national_debt": round(s.national_debt, 1),
            "is_credit_downgraded": s.is_credit_downgraded,
            "cumulative_rnd": round(s.cumulative_rnd, 1),
            "productivity_bonus": round(s.productivity_bonus, 2),
            "innovation_triggered": s.innovation_triggered,
            "welfare_cost": round(s.welfare_cost, 1),
            "exchange_rate": round(s.exchange_rate, 1),
            "exports": round(s.exports, 1),
            "imports": round(s.imports, 1),
            "foreign_reserves": round(s.foreign_reserves, 1),
            "unemployment_rate": round(s.unemployment_rate, 1),
            "real_estate_price": round(s.real_estate_price, 1),
            "money_supply": round(s.money_supply, 1),
            "money_multiplier": round(s.money_multiplier, 2),
            "inflation_rate": round(s.inflation_rate, 2),
            "interest_rate": round(s.interest_rate, 2),
            "gdp": round(s.gdp, 1),
            "gdp_growth_rate": round(s.gdp_growth_rate, 2),
            "population": s.population,
            "approval_rating": round(s.approval_rating, 1),
            "is_game_over": s.is_game_over,
            "is_victory": s.is_victory
        }