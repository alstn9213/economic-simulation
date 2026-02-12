import { useState, useEffect } from 'react';
import './App.css';

// 1. 데이터 타입 정의 (백엔드와 약속된 형태)
interface EconomyState {
  turn: number;
  money_supply: number;
  inflation_rate: number;
  interest_rate: number;
  budget: number;
  tax_rate: number;
  ltv_dti_rate: number;
  national_debt: number;
  is_credit_downgraded: boolean;
  cumulative_rnd: number;
  productivity_bonus: number;
  innovation_triggered: boolean;
  welfare_cost: number;
  exchange_rate: number;
  exports: number;
  imports: number;
  foreign_reserves: number;
  real_estate_price: number;
  unemployment_rate: number;
  approval_rating: number;
  is_game_over: boolean;
  is_victory: boolean;
}

function App() {
  // 2. 상태 관리 (React State)
  const [economy, setEconomy] = useState<EconomyState | null>(null);
  const [stimulus, setStimulus] = useState<string>("0"); // 입력값 관리
  const [taxCut, setTaxCut] = useState<string>("0");
  const [publicWorks, setPublicWorks] = useState<string>("0");
  const [taxRate, setTaxRate] = useState<number>(10); // 세율 (기본 10%)
  const [bondIssuance, setBondIssuance] = useState<string>("0");
  const [debtRepayment, setDebtRepayment] = useState<string>("0");
  const [rndInvestment, setRnDInvestment] = useState<string>("0");
  const [currencyDefense, setCurrencyDefense] = useState<string>("0");
  const [housingSupply, setHousingSupply] = useState<string>("0");
  const [ltvDtiRate, setLtvDtiRate] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(false);

  // 3. API 통신 함수들
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const API_URL = "http://127.0.0.1:8000";

  // 현재 상태 가져오기
  const fetchStatus = async () => {
    try {
      const response = await fetch(`${API_URL}/status`);
      const data = await response.json();
      setEconomy(data);
      setTaxRate(data.tax_rate); // 현재 세율로 UI 동기화
      setLtvDtiRate(data.ltv_dti_rate || 0);
      setErrorMessage(null);
    } catch (error) {
      console.error("서버 연결 실패:", error);
      alert("서버가 켜져 있는지 확인해주세요!");
    }
  };

  // 다음 턴 진행 (정책 실행)
  const handleNextTurn = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/next-turn`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ 
          stimulus: parseFloat(stimulus) || 0,
          tax_cut: parseFloat(taxCut) || 0,
          public_works: parseFloat(publicWorks) || 0,
          tax_rate: taxRate,
          bond_issuance: parseFloat(bondIssuance) || 0,
          debt_repayment: parseFloat(debtRepayment) || 0,
          rnd_investment: parseFloat(rndInvestment) || 0, 
          housing_supply: parseFloat(housingSupply) || 0,
          currency_defense: parseFloat(currencyDefense) || 0,
          ltv_dti_rate: ltvDtiRate
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setEconomy(data); // 갱신된 데이터로 화면 업데이트
        setErrorMessage(null);
      } else {
        const errorData = await response.json();
        setErrorMessage(
          errorData.detail || "정책 실행 실패. 서버 오류를 확인해주세요."
        );
      }
    } catch (error) {
      console.error("API 오류:", error);
    }
    setLoading(false);
  };

   // 게임 초기화
  const handleReset = async () => {
    if (!window.confirm("정말 초기화 하시겠습니까?")) return;
    
    try {
      await fetch(`${API_URL}/reset`, { method: "POST" });
      setStimulus("0");
      setTaxCut("0");
      setPublicWorks("0");
      setTaxRate(10);
      setBondIssuance("0");
      setDebtRepayment("0");
      setRnDInvestment("0");
      setHousingSupply("0");
      setCurrencyDefense("0");
      setLtvDtiRate(0);
      fetchStatus(); // 상태 다시 불러오기
    } catch (error) {
      console.error("초기화 실패:", error);
    }
  };

  // 4. 앱 시작 시 데이터 불러오기
  useEffect(() => {
    fetchStatus();
  }, []);

  // 5. 화면 렌더링
  if (!economy) return <div className="loading">경제 데이터 로딩 중...</div>;

  // 게임 오버 화면
  if (economy.is_game_over) {
    return (
      <div className="container" style={{ textAlign: 'center', color: 'red' }}>
        <h1>💀 GAME OVER 💀</h1>
        <p>지지율이 5% 미만으로 떨어져 정권이 붕괴되었습니다.</p>
        <button onClick={handleReset} className="btn-danger">새로운 정권 수립 (재시작)</button>
      </div>
    );
  }

  // 승리 화면
  if (economy.is_victory) {
    return (
      <div className="container" style={{ textAlign: 'center', color: '#2ecc71' }}>
        <h1>🎉 VICTORY! 🎉</h1>
        <p>축하합니다! 20분기 동안 경제를 성공적으로 이끌었습니다.</p>
        <p>최종 지지율: <strong>{economy.approval_rating.toFixed(1)}%</strong></p>
        <button onClick={handleReset} className="btn-primary">다시 도전하기</button>
      </div>
    );
  }

  return (
    <div className="container">
      <header>
        <h1>🏛️ 국가 경제 시뮬레이터</h1>
        <p>당신은 경제 정책 결정자입니다. 물가와 행복의 균형을 맞추세요.</p>
      </header>

      {/* 신용등급 강등 경고 */}
      {economy.is_credit_downgraded && (
        <div className="error-message" style={{ marginBottom: '20px', fontSize: '1.2rem' }}>
          🚨 국가 신용등급 강등! 부채 과다로 이자율이 폭등하고 있습니다! 🚨
        </div>
      )}

      {/* 기술 혁신 성공 메시지 */}
      {economy.innovation_triggered && (
        <div className="success-message" style={{ marginBottom: '20px', fontSize: '1.2rem', color: '#2ecc71', fontWeight: 'bold' }}>
          🚀 기술 혁신 성공! 국가 생산성이 영구적으로 향상되었습니다! (총 +{economy.productivity_bonus.toFixed(1)}%)
        </div>
      )}

      {/* 대시보드 섹션 */}
      <section className="dashboard">
        <div className="card">
          <h3>📅 분기 (Turn)</h3>
          <p className="value">{economy.turn}</p>
        </div>
        <div className="card">
          <h3>🏦 국가 예산</h3>
          <p className="value">{economy.budget.toFixed(1)}조 원</p>
        </div>
        <div className="card">
          <h3>🧾 세금 징수율</h3>
          <p className="value">{economy.tax_rate.toFixed(1)}%</p>
        </div>
        <div className="card">
          <h3>📉 국가 채무</h3>
          <p className="value" style={{ color: 'red' }}>{economy.national_debt.toFixed(1)}조 원</p>
        </div>
        <div className="card">
          <h3>👵 복지 비용 (고령화)</h3>
          <p className="value" style={{ color: 'orange' }}>-{economy.welfare_cost.toFixed(1)}조 원</p>
        </div>
        <div className="card">
          <h3>💵 외환 보유고</h3>
          <p className="value">{economy.foreign_reserves.toFixed(1)}억 달러</p>
        </div>
        <div className={`card ${economy.real_estate_price > 120 ? 'danger' : ''}`}>
          <h3>🏠 부동산 지수</h3>
          <p className="value">{economy.real_estate_price.toFixed(1)}</p>
          <small>기준: 100 {economy.real_estate_price > 120 && "(과열)"}</small>
        </div>
         <div className="card">
          <h3> 실업률</h3>
          <p className="value">{economy.unemployment_rate.toFixed(1)}%</p>
        </div>
        <div className="card">
          <h3>📉 LTV/DTI 규제</h3>
          <p className="value">{economy.ltv_dti_rate}%</p>
        </div>
        <div className="card">
          <h3>� 환율 (원/달러)</h3>
          <p className="value">{economy.exchange_rate.toFixed(0)}원</p>
        </div>
        <div className="card">
          <h3>🚢 무역 수지</h3>
          <p className="value" style={{ color: (economy.exports - economy.imports) >= 0 ? 'blue' : 'red' }}>
            {(economy.exports - economy.imports).toFixed(1)}조 원
          </p>
          <small style={{ fontSize: '0.8rem' }}>수출: {economy.exports.toFixed(0)} / 수입: {economy.imports.toFixed(0)}</small>
        </div>
        <div className="card">
          <h3>💰 시중 통화량</h3>
          <p className="value">{economy.money_supply.toFixed(1)}조 원</p>
        </div>
        <div className={`card ${economy.inflation_rate > 4 ? 'danger' : ''}`}>
          <h3>📈 물가상승률</h3>
          <p className="value">{economy.inflation_rate.toFixed(2)}%</p>
        </div>
        <div className={`card ${economy.is_credit_downgraded ? 'danger' : ''}`}>
          <h3>🏦 기준 금리</h3>
          <p className="value">{economy.interest_rate.toFixed(2)}%</p>
        </div>
        <div className="card">
          <h3>📊 정당 지지율</h3>
          <p className="value">{economy.approval_rating.toFixed(1)}%</p>
        </div>
      </section>

      {/* 컨트롤 패널 섹션 */}
      <section className="controls">
        <h2>정책 결정</h2>
        <div className="input-group">
          <label>💸 재난지원금 (지지율↑ 물가↑)</label>
          <input
            type="number"
            value={stimulus}
            onChange={(e) => setStimulus(e.target.value)}
            placeholder="0"
          />
        </div>

        <div className="input-group">
          <label>🏭 법인세 인하 (성장↑ 지지율-)</label>
          <input
            type="number"
            value={taxCut}
            onChange={(e) => setTaxCut(e.target.value)}
            placeholder="0"
          />
        </div>

        <div className="input-group">
          <label>🏗️ 공공 사업 (성장+ 지지율+)</label>
          <input
            type="number"
            value={publicWorks}
            onChange={(e) => setPublicWorks(e.target.value)}
            placeholder="0"
          />
        </div>

        <div className="input-group">
          <label>🧾 세금 징수율 설정: {taxRate}%</label>
          <input
            type="range"
            min="0"
            max="30"
            step="1"
            value={taxRate}
            onChange={(e) => setTaxRate(parseInt(e.target.value))}
          />
          <small>높으면 예산 확보, 낮으면 지지율/성장 상승</small>
        </div>

        <div className="input-group">
          <label>📜 국채 발행 (예산 확보, 이자 발생)</label>
          <input
            type="number"
            value={bondIssuance}
            onChange={(e) => setBondIssuance(e.target.value)}
            placeholder="0"
          />
        </div>

        <div className="input-group">
          <label>💸 부채 상환 (이자 부담 감소)</label>
          <input
            type="number"
            value={debtRepayment}
            onChange={(e) => setDebtRepayment(e.target.value)}
            placeholder="0"
          />
        </div>

        <div className="input-group">
          <label>🔬 R&D 투자 (누적: {economy.cumulative_rnd.toFixed(0)}/50조)</label>
          <input
            type="number"
            value={rndInvestment}
            onChange={(e) => setRnDInvestment(e.target.value)}
            placeholder="0"
          />
        </div>

         <div className="input-group">
          <label>🏘️ 주택 건설 (집값 하락)</label>
          <input
            type="number"
            value={housingSupply}
            onChange={(e) => setHousingSupply(e.target.value)}
            placeholder="0"
          />
        </div>

        <div className="input-group">
          <label>📉 LTV/DTI 규제 강도: {ltvDtiRate}%</label>
          <input
            type="range"
            min="0"
            max="100"
            step="10"
            value={ltvDtiRate}
            onChange={(e) => setLtvDtiRate(parseInt(e.target.value))}
          />
          <small>높으면 집값 하락, 경제 성장 둔화</small>
        </div>

        <div className="input-group">
          <label>🛡️ 환율 방어 (외환 보유고 사용)</label>
          <input
            type="number"
            value={currencyDefense}
            onChange={(e) => setCurrencyDefense(e.target.value)}
            placeholder="0"
          />
        </div>
        
        <div className="button-group">
          <button 
            onClick={handleNextTurn} 
            disabled={loading}
            className="btn-primary"
          >
            {loading ? "처리 중..." : "정책 실행 & 다음 턴"}
          </button>
          
          <button onClick={handleReset} className="btn-danger">
            게임 초기화
          </button>
        </div>
      </section>
      {errorMessage && (
        <div className="error-message">{errorMessage}</div>
      )}
    </div>
  );
}

export default App;