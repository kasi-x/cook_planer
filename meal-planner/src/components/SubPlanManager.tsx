import { useState, useEffect } from 'react';
import type { SubPlan } from '../types';
import { fetchSubPlans, createSubPlan, deleteSubPlan } from '../api';
import AllergenSelector from './AllergenSelector';

interface Props {
  planId: number;
  currentSubPlan: SubPlan | null;
  onSelect: (subPlan: SubPlan | null) => void;
}

export default function SubPlanManager({ planId, currentSubPlan, onSelect }: Props) {
  const [subPlans, setSubPlans] = useState<SubPlan[]>([]);
  const [creating, setCreating] = useState(false);
  const [newName, setNewName] = useState('');
  const [newAllergens, setNewAllergens] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSubPlans(planId).then(setSubPlans).catch(() => {
      setError('サブプランの読み込みに失敗しました');
    });
  }, [planId]);

  const handleCreate = async () => {
    if (!newName.trim()) return;
    setError(null);
    try {
      const sp = await createSubPlan(planId, {
        name: newName,
        excluded_allergens: newAllergens,
      });
      setSubPlans(prev => [...prev, sp]);
      setCreating(false);
      setNewName('');
      setNewAllergens([]);
    } catch {
      setError('サブプランの作成に失敗しました');
    }
  };

  const handleDelete = async (id: number) => {
    setError(null);
    try {
      await deleteSubPlan(id);
      setSubPlans(prev => prev.filter(sp => sp.id !== id));
      if (currentSubPlan?.id === id) onSelect(null);
    } catch {
      setError('サブプランの削除に失敗しました');
    }
  };

  return (
    <div className="sub-plan-manager">
      <div className="sub-plan-header">
        <h4>サブプラン</h4>
        <button className="sub-plan-add-btn" onClick={() => setCreating(!creating)}>
          {creating ? 'キャンセル' : '+ 新規'}
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {creating && (
        <div className="sub-plan-create-form">
          <input
            type="text"
            placeholder="サブプラン名（例：卵アレルギー対応）"
            value={newName}
            onChange={e => setNewName(e.target.value)}
            className="sub-plan-name-input"
          />
          <AllergenSelector selected={newAllergens} onChange={setNewAllergens} />
          <button className="btn-primary" onClick={handleCreate} disabled={!newName.trim()}>
            作成
          </button>
        </div>
      )}

      <div className="sub-plan-tabs">
        <button
          className={`sub-plan-tab ${!currentSubPlan ? 'active' : ''}`}
          onClick={() => onSelect(null)}
        >
          メインプラン
        </button>
        {subPlans.map(sp => (
          <div key={sp.id} className="sub-plan-tab-wrapper">
            <button
              className={`sub-plan-tab ${currentSubPlan?.id === sp.id ? 'active' : ''}`}
              onClick={() => onSelect(sp)}
            >
              {sp.name}
            </button>
            <button
              className="sub-plan-delete-btn"
              onClick={(e) => { e.stopPropagation(); handleDelete(sp.id); }}
              title="削除"
            >
              &times;
            </button>
          </div>
        ))}
      </div>

      {currentSubPlan && (
        <div className="sub-plan-info">
          除外アレルゲン: {currentSubPlan.excluded_allergens.length > 0
            ? currentSubPlan.excluded_allergens.join(', ')
            : 'なし'}
        </div>
      )}
    </div>
  );
}
