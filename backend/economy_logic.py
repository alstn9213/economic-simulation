import random

class EconomySimulation:
    def __init__(self):
        self.reset()

    def reset(self):
        """게임을 초기 상태로 되돌립니다."""
        self.money_supply = 1000      # 조 원
        self.inflation_rate = 2.0     # %
        self.interest_rate = 1.5      # %
        self.happiness = 70.0         # 점수
        self.turn = 1                 # 분기

    def apply_policy(self, stimulus_amount: float):
        """재난지원금 정책 반영"""
        if stimulus_amount > 0:
            self.money_supply += stimulus_amount
            # 단기적 행복 상승 (금액에 비례)
            self.happiness += (stimulus_amount * 0.5)

    def calculate_market_reaction(self):
        """시장 반응 계산 (핵심 로직)"""
        # 1. 인플레이션 계산 (통화량 증가 -> 물가 상승)
        inflation_pressure = (self.money_supply - 1000) * 0.01
        self.inflation_rate = 2.0 + inflation_pressure + random.uniform(-0.2, 0.2)

        # 2. 금리 조정 (중앙은행 자동 대응)
        # 물가가 3.5% 넘으면 금리 인상, 1.0% 미만이면 인하
        if self.inflation_rate > 3.5:
            self.interest_rate = min(10.0, self.interest_rate + 0.25)
            self.happiness -= 2  # 금리 인상 고통
        elif self.inflation_rate < 1.0:
            self.interest_rate = max(0.0, self.interest_rate - 0.25)

        # 3. 행복도 조정 (고물가 패널티)
        if self.inflation_rate > 4.0:
            self.happiness -= (self.inflation_rate * 1.5)
        
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
            "happiness": round(self.happiness, 1)
        }