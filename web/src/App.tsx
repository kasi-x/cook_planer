import { FoodSelector } from './components/FoodSelector';
import { ResultPanel } from './components/ResultPanel';
import { StrategySelector } from './components/StrategySelector';
import { useFoods } from './hooks/useFoods';

export default function App() {
  const {
    foods,
    selectedFoods,
    fixedFoods,
    strategy,
    scoringParams,
    result,
    loading,
    optimizing,
    error,
    toggleFood,
    setFixedAmount,
    setStrategy,
    setScoringParams,
    selectAll,
    clearAll,
    optimize,
  } = useFoods();

  if (loading) {
    return (
      <div className="container">
        <h1>栄養最適化アプリ</h1>
        <div className="loading">読み込み中...</div>
      </div>
    );
  }

  const hasSelection = selectedFoods.size > 0 || fixedFoods.size > 0;

  return (
    <div className="container">
      <h1>栄養最適化アプリ</h1>

      <main className="layout">
        <div className="left">
          <FoodSelector
            foods={foods}
            selectedFoods={selectedFoods}
            fixedFoods={fixedFoods}
            onToggle={toggleFood}
            onSetFixed={setFixedAmount}
            onSelectAll={selectAll}
            onClearAll={clearAll}
          />
          <StrategySelector
            strategy={strategy}
            scoringParams={scoringParams}
            onStrategyChange={setStrategy}
            onScoringParamsChange={setScoringParams}
          />
          <button
            type="button"
            className="optimize-btn"
            onClick={optimize}
            disabled={optimizing || !hasSelection}
          >
            {optimizing ? '計算中...' : '最適化実行'}
          </button>
        </div>

        <div className="right">
          <ResultPanel result={result} loading={optimizing} error={error} />
        </div>
      </main>
    </div>
  );
}
