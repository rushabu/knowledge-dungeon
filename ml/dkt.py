"""Deep Knowledge Tracing (Piech et al., 2015) benchmark on ASSISTments 2009."""
import numpy as np
import torch
from sklearn.metrics import roc_auc_score
from torch import nn

from .data import NUM_SKILLS

MAX_LEN = 200


class DKT(nn.Module):
    def __init__(self, num_skills=NUM_SKILLS, hidden=100):
        super().__init__()
        self.num_skills = num_skills
        self.embed = nn.Embedding(2 * num_skills + 1, hidden, padding_idx=0)
        self.lstm = nn.LSTM(hidden, hidden, batch_first=True)
        self.drop = nn.Dropout(0.2)
        self.out = nn.Linear(hidden, num_skills)

    def forward(self, x):
        h, _ = self.lstm(self.embed(x))
        return self.out(self.drop(h))


def _chunks(seqs):
    """Split long sequences into MAX_LEN windows (standard DKT practice)."""
    out = []
    for s in seqs:
        for i in range(0, len(s.skills), MAX_LEN):
            sk, co = s.skills[i:i + MAX_LEN], s.correct[i:i + MAX_LEN]
            if len(sk) >= 2:
                out.append((sk, co))
    return out


def _batch(chunks):
    L = max(len(sk) for sk, _ in chunks) - 1
    B = len(chunks)
    x = torch.zeros(B, L, dtype=torch.long)
    q = torch.zeros(B, L, dtype=torch.long)
    y = torch.zeros(B, L)
    m = torch.zeros(B, L, dtype=torch.bool)
    for i, (sk, co) in enumerate(chunks):
        n = len(sk) - 1
        # input: (skill, correct) at t; target: correctness of skill at t+1
        x[i, :n] = torch.from_numpy(sk[:-1] + co[:-1] * NUM_SKILLS)
        q[i, :n] = torch.from_numpy(sk[1:] - 1)
        y[i, :n] = torch.from_numpy(co[1:]).float()
        m[i, :n] = True
    return x, q, y, m


def _predict(model, chunks, bs=64):
    model.eval()
    preds, labels = [], []
    with torch.no_grad():
        for i in range(0, len(chunks), bs):
            x, q, y, m = _batch(chunks[i:i + bs])
            p = torch.sigmoid(model(x).gather(2, q.unsqueeze(2)).squeeze(2))
            preds.append(p[m].numpy())
            labels.append(y[m].numpy())
    return np.concatenate(labels), np.concatenate(preds)


def train_dkt(train, valid, test, epochs=20, bs=64, seed=0, log=print):
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    tr, va, te = _chunks(train), _chunks(valid), _chunks(test)
    model = DKT()
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    lossf = nn.BCEWithLogitsLoss()
    best_auc, best_state, patience = 0.0, None, 0
    for ep in range(epochs):
        model.train()
        order = rng.permutation(len(tr))
        for i in range(0, len(order), bs):
            x, q, y, m = _batch([tr[j] for j in order[i:i + bs]])
            logits = model(x).gather(2, q.unsqueeze(2)).squeeze(2)
            loss = lossf(logits[m], y[m])
            opt.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            opt.step()
        auc = roc_auc_score(*_predict(model, va))
        log(f"  DKT epoch {ep + 1:2d}  valid AUC {auc:.4f}")
        if auc > best_auc:
            best_auc, patience = auc, 0
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
        else:
            patience += 1
            if patience >= 3:
                break
    model.load_state_dict(best_state)
    y, p = _predict(model, te)
    return model, {"valid_auc": best_auc, "test_auc": float(roc_auc_score(y, p))}
