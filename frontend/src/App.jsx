import { useState, useEffect, useCallback } from 'react';
import './App.css';

const USER_ID = 1;

// ── API helpers ───────────────────────────────────
async function fetchQuest() {
  const r = await fetch(`/api/v1/daily-quest/${USER_ID}`);
  if (!r.ok) throw new Error('Could not load quest');
  return r.json();
}

async function fetchDueCards() {
  const r = await fetch(`/api/v1/srs/due-cards/${USER_ID}`);
  if (!r.ok) throw new Error('Could not load cards');
  return r.json();
}

async function completeRing(ring) {
  const r = await fetch(`/api/v1/complete/${USER_ID}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ring }),
  });
  if (!r.ok) throw new Error('Could not complete ring');
  return r.json();
}

// ── DrillScreen ───────────────────────────────────
function DrillScreen({ onBack, onComplete }) {
  const [cards, setCards] = useState(null);
  const [idx, setIdx] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [done, setDone] = useState(false);
  const [err, setErr] = useState(null);

  useEffect(() => {
    fetchDueCards()
      .then(c => setCards(c.length ? c : []))
      .catch(e => setErr(e.message));
  }, []);

  const advance = useCallback(() => {
    setFlipped(false);
    setTimeout(() => {
      if (idx + 1 >= cards.length) {
        setDone(true);
      } else {
        setIdx(i => i + 1);
      }
    }, 200);
  }, [idx, cards]);

  if (err) return (
    <div className="screen">
      <div className="drill-header">
        <button className="back-btn" onClick={onBack}>← Back</button>
      </div>
      <div className="center-msg"><span className="err-icon">⚠️</span>{err}</div>
    </div>
  );

  if (!cards) return (
    <div className="screen">
      <div className="drill-header">
        <button className="back-btn" onClick={onBack}>← Back</button>
      </div>
      <div className="center-msg"><div className="spinner" /></div>
    </div>
  );

  if (cards.length === 0) return (
    <div className="screen">
      <div className="drill-header">
        <button className="back-btn" onClick={onBack}>← Back</button>
      </div>
      <div className="drill-done">
        <div className="big">🎉</div>
        <h2>All caught up!</h2>
        <p>No cards due today. Come back tomorrow.</p>
        <button onClick={onComplete}>Mark Drill Done</button>
      </div>
    </div>
  );

  if (done) return (
    <div className="screen">
      <div className="drill-header">
        <button className="back-btn" onClick={onBack}>← Back</button>
      </div>
      <div className="drill-done">
        <div className="big">✅</div>
        <h2>Drill complete!</h2>
        <p>Reviewed {cards.length} card{cards.length > 1 ? 's' : ''}.</p>
        <button onClick={onComplete}>Claim XP</button>
      </div>
    </div>
  );

  const card = cards[idx];
  return (
    <div className="screen">
      <div className="drill-header">
        <button className="back-btn" onClick={onBack}>← Back</button>
        <div className="drill-progress">{idx + 1} / {cards.length}</div>
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
            <div className="card-hint">Tap to reveal</div>
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
        <button
          className="btn-again"
          disabled={!flipped}
          onClick={advance}
        >
          Again
        </button>
        <button
          className="btn-good"
          disabled={!flipped}
          onClick={advance}
        >
          Got it ✓
        </button>
      </div>
    </div>
  );
}

// ── TaskScreen ────────────────────────────────────
function TaskScreen({ task, ring, alreadyDone, onBack, onComplete }) {
  const [loading, setLoading] = useState(false);

  async function handleDone() {
    setLoading(true);
    try {
      await completeRing(ring);
      onComplete();
    } finally {
      setLoading(false);
    }
  }

  const isMedia = task.task_type === 'MEDIA';

  return (
    <div className="screen">
      <div className="drill-header">
        <button className="back-btn" onClick={onBack}>← Back</button>
      </div>

      <div className="task-card">
        <span className={`task-type-tag ${isMedia ? 'media' : 'action'}`}>
          {isMedia ? 'Input task' : 'Action task'}
        </span>
        <div className="task-title">{task.title}</div>
        <div className="task-desc">{task.description}</div>
        {task.url && (
          <a className="task-link" href={task.url} target="_blank" rel="noreferrer">
            Open resource ↗
          </a>
        )}
        {task.duration_minutes && (
          <div className="task-duration">⏱ ~{task.duration_minutes} minutes</div>
        )}
      </div>

      <button
        className="task-done-btn"
        disabled={alreadyDone || loading}
        onClick={handleDone}
      >
        {alreadyDone ? '✓ Done' : loading ? 'Saving…' : "I've done this! +10 XP"}
      </button>
    </div>
  );
}

// ── QuestScreen ───────────────────────────────────
function RingCard({ icon, color, name, sub, done, btnLabel, btnClass, onClick }) {
  return (
    <div className={`ring-card${done ? ' done' : ''}`}>
      <div className={`ring-icon ${color}`}>{icon}</div>
      <div className="ring-info">
        <div className="ring-name">{name}</div>
        <div className="ring-sub">{sub}</div>
      </div>
      <button
        className={`ring-btn ${done ? 'done-btn' : btnClass}`}
        onClick={onClick}
        disabled={done}
      >
        {done ? '✓' : btnLabel}
      </button>
    </div>
  );
}

function QuestScreen({ quest, onStartDrill, onStartTask }) {
  const mediaTask  = quest.tasks.find(t => t.ring === 'media');
  const actionTask = quest.tasks.find(t => t.ring === 'action');

  return (
    <div className="screen">
      <div className="section-title">Today's Quest</div>

      {quest.all_complete && (
        <div className="complete-banner">
          <div className="big">🏆</div>
          <h2>All rings complete!</h2>
          <p>Great work today. Come back tomorrow for a new quest.</p>
        </div>
      )}

      <RingCard
        icon="🃏"
        color="drill"
        name="Vocabulary Drill"
        sub={quest.drill_complete ? 'Completed' : 'Review your due cards'}
        done={quest.drill_complete}
        btnLabel="Start"
        btnClass="start-drill"
        onClick={onStartDrill}
      />

      {mediaTask && (
        <RingCard
          icon="🎧"
          color="media"
          name="Input"
          sub={quest.media_complete ? 'Completed' : mediaTask.title}
          done={quest.media_complete}
          btnLabel="Open"
          btnClass="start-media"
          onClick={() => onStartTask(mediaTask, 'media')}
        />
      )}

      {actionTask && (
        <RingCard
          icon="🗣️"
          color="action"
          name="Real-World Action"
          sub={quest.action_complete ? 'Completed' : actionTask.title}
          done={quest.action_complete}
          btnLabel="Start"
          btnClass="start-action"
          onClick={() => onStartTask(actionTask, 'action')}
        />
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

  const loadQuest = useCallback(() => {
    setLoading(true);
    setErr(null);
    fetchQuest()
      .then(q => { setQuest(q); setXp(q.xp_awarded); })
      .catch(e => setErr(e.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { loadQuest(); }, [loadQuest]);

  function handleDrillComplete() {
    completeRing('drill')
      .then(res => {
        setQuest(res.quest);
        setXp(res.quest.xp_awarded);
        setScreen('quest');
      })
      .catch(() => setScreen('quest'));
  }

  function handleTaskComplete() {
    loadQuest();
    setScreen('quest');
  }

  if (loading) return (
    <div className="app">
      <div className="center-msg"><div className="spinner" /></div>
    </div>
  );

  if (err) return (
    <div className="app">
      <div className="center-msg">
        <span className="err-icon">⚠️</span>
        <span>{err}</span>
        <button className="retry-btn" onClick={loadQuest}>Retry</button>
      </div>
    </div>
  );

  return (
    <div className="app">
      <header className="header">
        <div className="header-title">🇩🇪 German Quest</div>
        <div className="xp-badge"><span>⚡</span>{xp} XP today</div>
      </header>

      {screen === 'quest' && quest && (
        <QuestScreen
          quest={quest}
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
