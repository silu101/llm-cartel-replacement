# Exact commands used

All commands run from `collusion_hackathon/llm-cartel/` (the sprint starter repo) with an `OPENROUTER_API_KEY` in `../compute.env`. Copy this repo's `scripts/branch_game_neutral.py` into that folder first.

## 1. Model pilot (neutral prompt P0, 80 rounds, seed 0)

```bash
bash scripts/pilot_models.sh
# then, with a larger output budget for the two models whose reasoning ran out of tokens:
uv run python run_game.py --models deepseek/deepseek-v4.1-flash --prefix P0 --rounds 80 --seeds 0 --max_tokens 16000 --overwrite -y
uv run python run_game.py --models qwen/qwen3.8-flash          --prefix P0 --rounds 80 --seeds 0 --max_tokens 16000 --overwrite -y
uv run python run_game.py --models google/gemini-3.8-flash     --prefix P0 --rounds 80 --seeds 0 -y
uv run python run_game.py --models anthropic/claude-sonnet-5.5 --prefix P0 --rounds 80 --seeds 0 -y
# Claude Haiku 5.5 from scratch (also the "Haiku baseline"):
for s in 0 1 2 3 4 5 6 7; do uv run python run_game.py --models anthropic/claude-haiku-5.5 --prefix P0 --rounds 120 --seeds $s -y; done
```

## 2. Base cartels (Gemini 3.8 Flash, P0, 100 rounds, 8 seeds)

```bash
for s in 0 1 2 3 4 5 6 7; do uv run python run_game.py --models google/gemini-3.8-flash --prefix P0 --rounds 100 --seeds $s -y; done
```

Seed 1 never formed a cartel (gain 0.03) and is excluded by the pre-registered rule (gain over rounds 80–99 > 0.5).

## 3. Main replacement arms A0–A6 (branch at round 99, 50 rounds)

```bash
JOBS=3 bash scripts/run_branches.sh          # arms A0 A1 A2 A3 A4 A5 A6, seeds 0 2 3 4 5 6 7
```

## 4. Competitive-history placebo (A4p)

```bash
RUN=$(ls results/jsonl/2agents_prefix_P0-P0_*gemini-3p8*seed1.jsonl)
for k in 0 1 2 3 4; do
  uv run python branch_game.py "$RUN" --rounds 50 --at_round 99 --label A4p_placebo_competitive_s$k --seed $((100+k)) \
    --replace 0=anthropic/claude-haiku-5.5 1=anthropic/claude-haiku-5.5 --replace_prefix P0 --max_retries 30 -y
done
```

## 5. History-window arms (A4-k1, A4-k10)

Copies of the base runs with the saved `window` set to k (`results/jsonl_window/`), then:

```bash
for k in 1 10; do for s in 0 2 3 4 5 6 7; do
  uv run python branch_game.py results/jsonl_window/gemini_P0_seed${s}_win${k}.jsonl --rounds 50 --at_round 99 \
    --label A4w${k}_theseus_window${k} --replace 0=anthropic/claude-haiku-5.5 1=anthropic/claude-haiku-5.5 --replace_prefix P0 --max_retries 30 -y
done; done
```

## 6. 2×2 history × incumbent design (30 rounds, neutral warm-up for hidden-history newcomers)

```bash
for s in 0 2 3 4 5 6 7; do RUN=$(ls results/jsonl/2agents_prefix_P0-P0_*gemini-3p8*seed${s}.jsonl)
  uv run python branch_game_neutral.py $RUN --rounds 30 --at_round 99 --label F_inc1_hist1 --replace 1=anthropic/claude-haiku-5.5 --replace_prefix P0 --max_retries 30 -y
  uv run python branch_game_neutral.py $RUN --rounds 30 --at_round 99 --label F_inc1_hist0 --replace 1=anthropic/claude-haiku-5.5 --replace_prefix P0 --replacement_window 100 --max_retries 30 -y
  uv run python branch_game_neutral.py $RUN --rounds 30 --at_round 99 --label F_inc0_hist0 --replace 0=anthropic/claude-haiku-5.5 1=anthropic/claude-haiku-5.5 --replace_prefix P0 --replacement_window 100 --max_retries 30 -y
done
```

The fourth cell (no incumbent, history kept) is arm A4, evaluated over the same post-branch rounds 11–30.

## 7. Analysis and figures (no API calls)

```bash
python3 -I scripts/factorial_analysis.py
uv run --with matplotlib python scripts/mechanism_analysis.py   # intent vocabulary, matching moves, Figure 2
uv run --with matplotlib python scripts/make_figure.py          # Figure 1
```
