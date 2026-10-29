import { useState, useEffect, useCallback, useRef } from 'react';
import './App.css';

const USER_ID = 1;

// ── API ───────────────────────────────────────────
async function fetchQuest() {
  const r = await fetch(`/api/v1/daily-quest/${USER_ID}`);
  if (!r.ok) throw new Error('Could not load today\'s quest');
  return r.json();
}
async function fetchDueCards() {
  const r = await fetch(`/api/v1/srs/due-cards/${USER_ID}`);
  if (!r.ok) throw new Error('Could not load cards');
  return r.json();
}
async function apiCompleteRing(ring) {
  const r = await fetch(`/api/v1/complete/${USER_ID}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ring }),
  });
  if (!r.ok) throw new Error('Could not save progress');
  return r.json();
}

// ── Ring SVG circle ───────────────────────────────
function RingCircle({ done, color, emoji }) {
  const r = 22;
  const circ = 2 * Math.PI * r; // ~138
  return (
    <div className="ring-circle-wrap">
      <svg className="ring-svg" viewBox="0 0 52 52">
        <circle className="ring-bg-circle" cx="26" cy="26" r={r} />
        <circle
          className={`ring-progress-circle ${color}${done ? ' filled' : ''}`}
          cx="26" cy="26" r={r}
          strokeDasharray={circ}
          strokeDashoffset={done ? 0 : circ}
        />
      </svg>
      <div className="ring-emoji">{done ? '✓' : emoji}</div>
    </div>
  );
}

// ── XP popup ──────────────────────────────────────
function XpPopup({ amount, onDone }) {
  return (
    <div className="xp-popup" onAnimationEnd={onDone}>
      +{amount} XP ⚡
    </div>
  );
}

// ── Drill screen ──────────────────────────────────
function DrillScreen({ onBack, onComplete }) {
  const [cards, setCards]   = useState(null);
  const [idx, setIdx]       = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [done, setDone]     = useState(false);
  const [err, setErr]       = useState(null);

  useEffect(() => {
    fetchDueCards()
      .then(c => setCards(c))
      .catch(e => setErr(e.message));
  }, []);

  const advance = useCallback(() => {
    setFlipped(false);
    setTimeout(() => {
      setIdx(i => {
        if (i + 1 >= cards.length) { setDone(true); return i; }
        return i + 1;
      });
    }, 220);
  }, [cards]);

  const pct = cards ? Math.round((idx / Math.max(cards.length, 1)) * 100) : 0;

  if (err) return (
    <div className="screen">
      <div className="drill-header"><button className="back-btn" onClick={onBack}>← Back</button></div>
      <div className="center-msg"><span style={{ fontSize: 28 }}>⚠️</span>{err}</div>
    </div>
  );
  if (!cards) return (
    <div className="screen">
      <div className="drill-header"><button className="back-btn" onClick={onBack}>← Back</button></div>
      <div className="center-msg"><div className="spinner" /></div>
    </div>
  );
  if (cards.length === 0 || done) return (
    <div className="screen">
      <div className="drill-header"><button className="back-btn" onClick={onBack}>← Back</button></div>
      <div className="drill-done">
        <div className="big">{cards.length === 0 ? '🎉' : '🏅'}</div>
        <h2>{cards.length === 0 ? 'All caught up!' : 'Drill complete!'}</h2>
        <p>{cards.length === 0
          ? 'No cards due today. Come back tomorrow.'
          : `You reviewed ${cards.length} card${cards.length > 1 ? 's' : ''}. Great work!`}
        </p>
        <button className="claim-btn" onClick={onComplete}>
          {cards.length === 0 ? 'Mark Done' : 'Claim +10 XP ⚡'}
        </button>
      </div>
    </div>
  );

  const card = cards[idx];
  return (
    <div className="screen">
      <div className="drill-header">
        <button className="back-btn" onClick={onBack}>← Back</button>
        <div className="drill-progress-text">{idx + 1} / {cards.length}</div>
      </div>

      <div className="drill-bar">
        <div className="drill-bar-fill" style={{ width: `${pct}%` }} />
      </div>

      <div
        className="flashcard-wrap"
        onClick={() => setFlipped(f => !f)}
        role="button"
        aria-label="Flip card"
      >
        <div className={`flashcard${flipped ? ' flipped' : ''}`}>
          <div className="card-face front">
            <div className="card-de">{card.german_word}</div>
            <div className="card-hint">👆 Tap to reveal translation</div>
          </div>
          <div className="card-face back">
            <div className="card-ml">{card.malayalam_translation}</div>
            {card.example_sentence && (
              <div className="card-example">"{card.example_sentence}"</div>
            )}
          </div>
        </div>
      </div>

      <div className="drill-actions">
        <button className="btn-again" disabled={!flipped} onClick={advance}>
          😅 Again
        </button>
        <button className="btn-good" disabled={!flipped} onClick={advance}>
          ✓ Got it!
        </button>
      </div>
    </div>
  );
}

// ── Task screen ───────────────────────────────────
function TaskScreen({ task, ring, alreadyDone, onBack, onComplete }) {
  const [opened, setOpened]   = useState(false);
  const [saving, setSaving]   = useState(false);
  const isMedia = task.task_type === 'MEDIA';

  function handleOpen() {
    if (task.url) window.open(task.url, '_blank', 'noopener,noreferrer');
    setOpened(true);
  }

  async function handleDone() {
    setSaving(true);
    try {
      await apiCompleteRing(ring);
      onComplete();
    } finally {
      setSaving(false);
    }
  }

  const canDone = alreadyDone || opened || !task.url;

  return (
    <div className="screen">
      <div className="drill-header">
        <button className="back-btn" onClick={onBack}>← Back</button>
      </div>

      <div className="task-hero">
        <span className={`task-type-tag ${isMedia ? 'media' : 'action'}`}>
          {isMedia ? '🎧 Input' : '🗣️ Action'}
        </span>
        <div className="task-title">{task.title}</div>
        <div className="task-desc">{task.description}</div>
        {task.duration_minutes && (
          <div className="task-meta">⏱ About {task.duration_minutes} min</div>
        )}
      </div>

      {task.url && (
        <button
          className={`open-resource-btn ${isMedia ? '' : 'action-btn'} ${opened ? 'opened' : ''}`}
          onClick={!opened ? handleOpen : undefined}
        >
          {opened ? '✓ Opened!' : `Open ${isMedia ? 'Podcast / Article' : 'Resource'} ↗`}
        </button>
      )}

      {task.url && !opened && !alreadyDone && (
        <div className="open-hint">Open the resource first, then mark it done.</div>
      )}

      <button
        className="task-done-btn"
        disabled={!canDone || saving || alreadyDone}
        onClick={handleDone}
      >
        {alreadyDone ? '✓ Ring Complete' : saving ? 'Saving…' : "I've done this! +10 XP ⚡"}
      </button>
    </div>
  );
}

// ── Quest screen ──────────────────────────────────
function QuestScreen({ quest, xp, onStartDrill, onStartTask }) {
  const mediaTask  = quest.tasks.find(t => t.ring === 'media');
  const actionTask = quest.tasks.find(t => t.ring === 'action');
  const done = [quest.drill_complete, quest.media_complete, quest.action_complete];
  const doneCount = done.filter(Boolean).length;
  const pct = Math.round((doneCount / 3) * 100);

  const today = new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' });

  return (
    <div className="screen">
      <div className="quest-header">
        <div className="quest-day">Day Quest</div>
        <div className="quest-title">{today}</div>
      </div>

      <div className="progress-row">
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${pct}%` }} />
        </div>
        <div className="progress-label">{doneCount} / 3</div>
      </div>

      {quest.all_complete && (
        <div className="complete-banner">
          <div className="trophy">🏆</div>
          <h2>Quest Complete!</h2>
          <p>All three rings done. You earned {xp} XP today. Come back tomorrow!</p>
        </div>
      )}

      {/* Drill ring */}
      <div
        className={`ring-card drill-card${quest.drill_complete ? ' done' : ' pulse'}`}
        onClick={!quest.drill_complete ? onStartDrill : undefined}
        role={quest.drill_complete ? undefined : 'button'}
      >
        <RingCircle done={quest.drill_complete} color="drill-c" emoji="🃏" />
        <div className="ring-info">
          <div className="ring-name">Vocabulary Drill</div>
          <div className="ring-sub">
            {quest.drill_complete ? 'Completed ✓' : 'Flip cards, earn XP'}
          </div>
        </div>
        <div className="ring-chevron">{quest.drill_complete ? '✓' : '›'}</div>
      </div>

      {/* Media ring */}
      {mediaTask && (
        <div
          className={`ring-card media-card${quest.media_complete ? ' done' : ' pulse'}`}
          onClick={!quest.media_complete ? () => onStartTask(mediaTask, 'media') : undefined}
          role={quest.media_complete ? undefined : 'button'}
        >
          <RingCircle done={quest.media_complete} color="media-c" emoji="🎧" />
          <div className="ring-info">
            <div className="ring-name">Input</div>
            <div className="ring-sub">
              {quest.media_complete ? 'Completed ✓' : mediaTask.title}
            </div>
          </div>
          <div className="ring-chevron">{quest.media_complete ? '✓' : '›'}</div>
        </div>
      )}

      {/* Action ring */}
      {actionTask && (
        <div
          className={`ring-card action-card${quest.action_complete ? ' done' : ' pulse'}`}
          onClick={!quest.action_complete ? () => onStartTask(actionTask, 'action') : undefined}
          role={quest.action_complete ? undefined : 'button'}
        >
          <RingCircle done={quest.action_complete} color="action-c" emoji="🗣️" />
          <div className="ring-info">
            <div className="ring-name">Real-World Action</div>
            <div className="ring-sub">
              {quest.action_complete ? 'Completed ✓' : actionTask.title}
            </div>
          </div>
          <div className="ring-chevron">{quest.action_complete ? '✓' : '›'}</div>
        </div>
      )}
    </div>
  );
}

// ── App root ──────────────────────────────────────
export default function App() {
  const [screen, setScreen]   = useState('quest');
  const [quest, setQuest]     = useState(null);
  const [xp, setXp]           = useState(0);
  const [loading, setLoading] = useState(true);
  const [err, setErr]         = useState(null);
  const [taskCtx, setTaskCtx] = useState(null);
  const [xpPopup, setXpPopup] = useState(null); // { amount, key }
  const popupKey = useRef(0);

  const showXpGain = useCallback((amount) => {
    if (amount <= 0) return;
    popupKey.current += 1;
    setXpPopup({ amount, key: popupKey.current });
  }, []);

  const loadQuest = useCallback(() => {
    setLoading(true);
    setErr(null);
    return fetchQuest()
      .then(q => { setQuest(q); setXp(q.xp_awarded); return q; })
      .catch(e => { setErr(e.message); throw e; })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { loadQuest(); }, [loadQuest]);

  function handleDrillComplete() {
    apiCompleteRing('drill')
      .then(res => {
        showXpGain(res.xp_gained);
        setQuest(res.quest);
        setXp(res.quest.xp_awarded);
        setScreen('quest');
      })
      .catch(() => setScreen('quest'));
  }

  function handleTaskComplete() {
    loadQuest()
      .then(q => {
        // xp_gained = difference from what we had
        const gained = q.xp_awarded - xp;
        showXpGain(gained);
      })
      .catch(() => {});
    setScreen('quest');
  }

  if (loading && !quest) return (
    <div className="app">
      <div className="center-msg"><div className="spinner" /></div>
    </div>
  );
  if (err && !quest) return (
    <div className="app">
      <div className="center-msg">
        <span style={{ fontSize: 28 }}>⚠️</span>
        <span>{err}</span>
        <button className="retry-btn" onClick={loadQuest}>Retry</button>
      </div>
    </div>
  );

  const today = new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric' });

  return (
    <div className="app">
      {xpPopup && (
        <XpPopup
          key={xpPopup.key}
          amount={xpPopup.amount}
          onDone={() => setXpPopup(null)}
        />
      )}

      <header className="header">
        <div className="header-left">
          <div className="header-logo">🇩🇪 German Quest</div>
          <div className="header-date">{today}</div>
        </div>
        <div className="header-right">
          <div className="streak-badge">🔥 1</div>
          <div className="xp-badge">⚡ {xp} XP</div>
        </div>
      </header>

      {screen === 'quest' && quest && (
        <QuestScreen
          quest={quest}
          xp={xp}
          onStartDrill={() => setScreen('drill')}
          onStartTask={(task, ring) => { setTaskCtx({ task, ring }); setScreen('task'); }}
        />
      )}

      {screen === 'drill' && (
        <DrillScreen
          onBack={() => setScreen('quest')}
          onComplete={handleDrillComplete}
        />
      )}

      {screen === 'task' && taskCtx && (
        <TaskScreen
          task={taskCtx.task}
          ring={taskCtx.ring}
          alreadyDone={
            taskCtx.ring === 'media' ? quest.media_complete : quest.action_complete
          }
          onBack={() => setScreen('quest')}
          onComplete={handleTaskComplete}
        />
      )}
    </div>
  );
}
