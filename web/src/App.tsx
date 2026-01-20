import { FoodSelector } from './components/FoodSelector';
import { ResultPanel } from './components/ResultPanel';
import { useFoods } from './hooks/useFoods';

export default function App() {
  const {
    foods,
    selectedFoods,
    result,
    loading,
    optimizing,
    error,
    toggleFood,
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

  return (
    <div className="container">
      <h1>栄養最適化アプリ</h1>

      <main className="layout">
        <div className="left">
          <FoodSelector
            foods={foods}
            selectedFoods={selectedFoods}
            onToggle={toggleFood}
            onSelectAll={selectAll}
            onClearAll={clearAll}
          />
          <button
            type="button"
            className="optimize-btn"
            onClick={optimize}
            disabled={optimizing || selectedFoods.size === 0}
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
