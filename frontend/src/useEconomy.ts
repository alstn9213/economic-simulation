import { useState, useEffect } from 'react';

export interface EconomyState {
  turn: number;
  money_supply: number;
  inflation_rate: number;
  interest_rate: number;
  happiness: number;
  national_debt: number;
  gdp: number;
  gdp_growth_rate: number;
}

export const useEconomy = () => {
  const [economy, setEconomy] = useState<EconomyState | null>(null);
  const [stimulus, setStimulus] = useState<string>("0");
  const [loading, setLoading] = useState<boolean>(false);

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
    const amount = parseFloat(stimulus);
    if (isNaN(amount) || amount < 0) {
      alert("재난지원금은 0 이상이어야 합니다.");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/next-turn`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ stimulus: amount }),
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

  // 상태 초기화
  const handleReset = async () => {
    if (!window.confirm("정말 초기화 하시겠습니까?")) return;

    try {
      await fetch(`${API_URL}/reset`, { method: "POST" });
      setStimulus("0");
      fetchStatus(); // 상태 다시 불러오기
    } catch (error) {
      console.error("초기화 실패:", error);
    }
  };

  // 시작 시 데이터 불러오기
  useEffect(() => {
    fetchStatus();
  }, []);

  return {
    economy,
    stimulus,
    setStimulus,
    loading,
    handleNextTurn,
    handleReset,
  };
};