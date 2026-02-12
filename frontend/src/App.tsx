import { useState, useEffect } from 'react';
import './App.css';

// 1. 데이터 타입 정의 (백엔드와 약속된 형태)
interface EconomyState {
  turn: number;
  money_supply: number;
  inflation_rate: number;
  interest_rate: number;
  happiness: number;
}

function App() {
  // 2. 상태 관리 (React State)
  const [economy, setEconomy] = useState<EconomyState | null>(null);
  const [stimulus, setStimulus] = useState<string>("0"); // 입력값 관리
  const [loading, setLoading] = useState<boolean>(false);

  // 3. API 통신 함수들
  const API_URL = "http://127.0.0.1:8000";

  // 현재 상태 가져오기
  const fetchStatus = async () => {
    try {
      const response = await fetch(`${API_URL}/status`);
      const data = await response.json();
      setEconomy(data);
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
        body: JSON.stringify({ stimulus: parseFloat(stimulus) }),
      });

      if (response.ok) {
        const data = await response.json();
        setEconomy(data); // 갱신된 데이터로 화면 업데이트
      }
    } catch (error) {
      console.error("API 오류:", error);
    }
    setLoading(false);
  };

  // 게임 초기화
  const handleReset = async () => {
    if(!window.confirm("정말 초기화 하시겠습니까?")) return;
    
    try {
      await fetch(`${API_URL}/reset`, { method: "POST" });
      setStimulus("0");
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
            value={stimulus}
            onChange={(e) => setStimulus(e.target.value)}
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
    </div>
  );
}

export default App;