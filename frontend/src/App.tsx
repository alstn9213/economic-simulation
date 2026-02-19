import './App.css';
import { useEconomy } from './useEconomy';

function App() {
  const {
    economy,
    stimulus,
    setStimulus,
    loading,
    handleNextTurn,
    handleReset
  } = useEconomy();


  // 화면 렌더링
  if (!economy) return <div className="loading">경제 데이터 로딩 중...</div>;

  return (
    <div className="container">
      <header>
        <h1>🏛️ 국가 경제 시뮬레이터</h1>
        <p>당신은 경제 정책 결정자입니다. 물가와 행복의 균형을 맞추세요.</p>
      </header>

      {/* 대시보드 섹션 */}
      <section className="dashboard">
        <div className="card">
          <h3>📅 분기 (Turn)</h3>
          <p className="value">{economy.turn}</p>
        </div>
        <div className="card">
          <h3>💰 시중 통화량</h3>
          <p className="value">{economy.money_supply.toFixed(1)}조 원</p>
        </div>
        <div className={`card ${economy.national_debt > economy.gdp * 0.6 ? 'danger' : ''}`}>
          <h3>📉 국가 부채</h3>
          <p className="value">{economy.national_debt.toFixed(1)}조 원</p>
        </div>
        <div className="card">
          <h3>📊 명목 GDP</h3>
          <p className="value">{economy.gdp.toFixed(1)}조 원</p>
        </div>
        <div className={`card ${economy.gdp_growth_rate < 0 ? 'danger' : ''}`}>
          <h3>🚀 경제 성장률</h3>
          <p className="value">{economy.gdp_growth_rate.toFixed(2)}%</p>
        </div>
        <div className={`card ${economy.inflation_rate > 4 ? 'danger' : ''}`}>
          <h3>📈 물가상승률</h3>
          <p className="value">{economy.inflation_rate.toFixed(2)}%</p>
        </div>
        <div className="card">
          <h3>🏦 기준 금리</h3>
          <p className="value">{economy.interest_rate.toFixed(2)}%</p>
        </div>
        <div className="card">
          <h3>😊 국민 행복도</h3>
          <p className="value">{economy.happiness.toFixed(1)}</p>
        </div>
      </section>

      {/* 컨트롤 패널 섹션 */}
      <section className="controls">
        <h2>정책 결정</h2>
        <div className="input-group">
          <label>이번 분기 재난지원금 규모 (조 원):</label>
          <input
            type="number"
            min="0"
            value={stimulus}
            onChange={(e) => {
              const val = parseFloat(e.target.value);
              setStimulus(e.target.value);
            }}
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
            상태 초기화
          </button>
        </div>
      </section>
    </div>
  );
}

export default App;