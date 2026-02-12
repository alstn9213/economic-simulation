from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from economy_logic import EconomySimulation

app = FastAPI()

# --- CORS 설정 (프론트엔드 연결 필수) ---
origins = [
    "http://localhost:5173",  # Vite 기본 포트
    "http://localhost:3000",  # React 기본 포트
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 게임 상태 관리 (메모리) ---
# 주의: 실제 서비스라면 DB를 써야 하지만, 간단한 연습용이니 전역 변수에 저장합니다.
game = EconomySimulation()

# --- 데이터 모델 정의 (Pydantic) ---
# 프론트엔드에서 보낼 데이터 형식을 정의합니다.
class PolicyRequest(BaseModel):
    stimulus: float = 0     # 재난 지원금
    tax_cut: float = 0      # 법인세 인하
    public_works: float = 0 # 공공 사업
    tax_rate: float = 10.0  # 세금 징수율 (기본 10%)
    bond_issuance: float = 0 # 국채 발행량
    debt_repayment: float = 0 # 부채 상환액
    rnd_investment: float = 0 # R&D 투자액
    currency_defense: float = 0 # 환율 방어 투입액
    housing_supply: float = 0 # 주택 건설 투자액
    ltv_dti_rate: float = 0.0 # LTV/DTI 규제 강도 (0~100%)

# --- API 엔드포인트 ---

@app.get("/")
def read_root():
    return {"message": "경제 시뮬레이션 서버가 실행 중입니다!"}

@app.get("/status")
def get_status():
    """현재 경제 지표를 조회합니다."""
    return game.get_state()

@app.post("/next-turn")
def next_turn(policy: PolicyRequest):
    """정책을 적용하고 다음 턴으로 진행합니다."""
    # 1. 정책 적용
    game.apply_policy(policy.stimulus, policy.tax_cut, policy.public_works, policy.tax_rate, policy.bond_issuance, policy.debt_repayment, policy.rnd_investment, policy.currency_defense, policy.housing_supply, policy.ltv_dti_rate)
    # 2. 시장 반응 계산
    game.calculate_market_reaction()
    # 3. 결과 반환
    return game.get_state()

@app.post("/reset")
def reset_game():
    """게임을 초기화합니다."""
    game.reset()
    return {"message": "게임이 초기화되었습니다.", "status": game.get_state()}