import type { OptimizeStrategy, ScoringParams } from '../types';
import { STRATEGY_LABELS } from '../types';

interface Props {
  strategy: OptimizeStrategy;
  scoringParams: ScoringParams;
  onStrategyChange: (strategy: OptimizeStrategy) => void;
  onScoringParamsChange: (params: ScoringParams) => void;
}

export function StrategySelector({
  strategy,
  scoringParams,
  onStrategyChange,
  onScoringParamsChange,
}: Props) {
  const strategies: OptimizeStrategy[] = ['balanced', 'strict', 'calorie_focused', 'custom_score'];

  return (
    <section className="panel strategy-panel">
      <h2>最適化戦略</h2>

      <div className="strategy-options">
        {strategies.map((s) => (
          <label key={s} className={`strategy-option ${strategy === s ? 'selected' : ''}`}>
            <input
              type="radio"
              name="strategy"
              value={s}
              checked={strategy === s}
              onChange={() => onStrategyChange(s)}
            />
            <span className="strategy-label">{STRATEGY_LABELS[s]}</span>
          </label>
        ))}
      </div>

      {strategy === 'custom_score' && (
        <div className="scoring-params">
          <h3>スコアパラメータ</h3>
          <div className="param-grid">
            <label>
              <span>不足ペナルティ (1%あたり)</span>
              <input
                type="number"
                step="0.1"
                value={scoringParams.deficit_penalty}
                onChange={(e) =>
                  onScoringParamsChange({
                    ...scoringParams,
                    deficit_penalty: parseFloat(e.target.value) || 0,
                  })
                }
              />
            </label>
            <label>
              <span>コストボーナス (1円あたり)</span>
              <input
                type="number"
                step="0.01"
                value={scoringParams.cost_bonus}
                onChange={(e) =>
                  onScoringParamsChange({
                    ...scoringParams,
                    cost_bonus: parseFloat(e.target.value) || 0,
                  })
                }
              />
            </label>
            <label>
              <span>カロリー重み</span>
              <input
                type="number"
                step="0.1"
                value={scoringParams.calorie_weight}
                onChange={(e) =>
                  onScoringParamsChange({
                    ...scoringParams,
                    calorie_weight: parseFloat(e.target.value) || 0,
                  })
                }
              />
            </label>
            <label>
              <span>タンパク質重み</span>
              <input
                type="number"
                step="0.1"
                value={scoringParams.protein_weight}
                onChange={(e) =>
                  onScoringParamsChange({
                    ...scoringParams,
                    protein_weight: parseFloat(e.target.value) || 0,
                  })
                }
              />
            </label>
            <label>
              <span>ビタミン重み</span>
              <input
                type="number"
                step="0.1"
                value={scoringParams.vitamin_weight}
                onChange={(e) =>
                  onScoringParamsChange({
                    ...scoringParams,
                    vitamin_weight: parseFloat(e.target.value) || 0,
                  })
                }
              />
            </label>
            <label>
              <span>ミネラル重み</span>
              <input
                type="number"
                step="0.1"
                value={scoringParams.mineral_weight}
                onChange={(e) =>
                  onScoringParamsChange({
                    ...scoringParams,
                    mineral_weight: parseFloat(e.target.value) || 0,
                  })
                }
              />
            </label>
          </div>
        </div>
      )}
    </section>
  );
}
