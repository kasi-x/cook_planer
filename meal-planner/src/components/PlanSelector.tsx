import { useState } from 'react';
import type { MenuPlan, SchoolGradeLevel } from '../types';
import { GRADE_LABELS } from '../types';

interface Props {
  plans: MenuPlan[];
  currentPlan: MenuPlan | null;
  onSelect: (plan: MenuPlan) => void;
  onCreate: (name: string, grade: SchoolGradeLevel, start: string, end: string) => Promise<MenuPlan>;
  onDelete: (planId: number) => Promise<void>;
}

export default function PlanSelector({ plans, currentPlan, onSelect, onCreate, onDelete }: Props) {
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState('');
  const [newGrade, setNewGrade] = useState<SchoolGradeLevel>('elementary_mid');
  const [newStart, setNewStart] = useState('');
  const [newEnd, setNewEnd] = useState('');

  const handleSelectChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const plan = plans.find(p => p.id === Number(e.target.value));
    if (plan) onSelect(plan);
  };

  const handleCreate = async () => {
    if (!newName || !newStart || !newEnd) return;
    await onCreate(newName, newGrade, newStart, newEnd);
    setShowCreate(false);
    setNewName('');
    setNewStart('');
    setNewEnd('');
  };

  const handleDelete = async () => {
    if (!currentPlan) return;
    if (!confirm(`「${currentPlan.name}」を削除しますか？`)) return;
    await onDelete(currentPlan.id);
  };

  return (
    <>
      <div className="plan-selector">
        <select value={currentPlan?.id ?? ''} onChange={handleSelectChange}>
          <option value="">-- 献立計画を選択 --</option>
          {plans.map(p => (
            <option key={p.id} value={p.id}>{p.name}</option>
          ))}
        </select>
        <button className="btn-primary" onClick={() => setShowCreate(true)}>+ 新規作成</button>
        {currentPlan && (
          <button className="btn-danger" onClick={handleDelete}>削除</button>
        )}
      </div>

      {showCreate && (
        <div className="modal-overlay" onClick={() => setShowCreate(false)}>
          <div className="modal-content" style={{ maxWidth: 480 }} onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>新しい献立計画</h2>
              <button className="modal-close" onClick={() => setShowCreate(false)}>&times;</button>
            </div>
            <div className="create-plan-form">
              <div className="form-group">
                <label>計画名</label>
                <input
                  type="text"
                  value={newName}
                  onChange={e => setNewName(e.target.value)}
                  placeholder="例: 6月第1週〜第4週"
                />
              </div>
              <div className="form-group">
                <label>学年区分</label>
                <select value={newGrade} onChange={e => setNewGrade(e.target.value as SchoolGradeLevel)}>
                  {(Object.entries(GRADE_LABELS) as [SchoolGradeLevel, string][]).map(([k, v]) => (
                    <option key={k} value={k}>{v}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>開始日</label>
                <input type="date" value={newStart} onChange={e => setNewStart(e.target.value)} />
              </div>
              <div className="form-group">
                <label>終了日</label>
                <input type="date" value={newEnd} onChange={e => setNewEnd(e.target.value)} />
              </div>
            </div>
            <div className="modal-footer">
              <button onClick={() => setShowCreate(false)}>キャンセル</button>
              <button className="btn-primary" onClick={handleCreate}>作成</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
