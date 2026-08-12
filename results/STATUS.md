# STATUS — 2026-08-11T22:28:42+09:00

- template: primary
- raw_results rows (현 template): 9600 / 6000
- attn_profile rows: 600 / 600

## 단계 이벤트 로그 (stage_times.jsonl)

- 2026-08-11T13:21:07+09:00 [start] 00_token_probe (s) 
- 2026-08-11T13:21:11+09:00 [end] 00_token_probe (4s) 
- 2026-08-11T13:21:11+09:00 [start] 00_eval_50 (s) 
- 2026-08-11T13:21:36+09:00 [end] 00_eval_50 (25s) 
- 2026-08-11T13:21:36+09:00 [start] 00_profiler_check (s) 
- 2026-08-11T13:21:37+09:00 [end] 00_profiler_check (1s) 
- 2026-08-11T13:21:37+09:00 [start] 00_analyze_dryrun (s) 
- 2026-08-11T13:21:38+09:00 [end] 00_analyze_dryrun (1s) 
- 2026-08-11T13:21:57+09:00 [start] 02_sanity2_grounding (s) 
- 2026-08-11T13:22:09+09:00 [end] 02_sanity2_grounding (12s) 
- 2026-08-11T13:22:09+09:00 [start] 02_sanity1_t0_vs_s (s) 
- 2026-08-11T13:22:56+09:00 [end] 02_sanity1_t0_vs_s (47s) 
- 2026-08-11T13:22:56+09:00 [start] 02_sanity3_s_acc (s) 
- 2026-08-11T13:23:40+09:00 [end] 02_sanity3_s_acc (44s) 
- 2026-08-11T13:23:54+09:00 [start] 03_main_shard0 (s) 
- 2026-08-11T14:10:14+09:00 [end] 03_main_shard0 (2780s) 
- 2026-08-11T14:10:18+09:00 [start] 04_profile_shard0 (s) 
- 2026-08-11T14:15:47+09:00 [end] 04_profile_shard0 (329s) 
- 2026-08-11T14:15:51+09:00 [start] 05_analyze (s) 
- 2026-08-11T14:15:52+09:00 [end] 05_analyze (1s) 
- 2026-08-11T14:16:02+09:00 [start] 05_analyze (s) 
- 2026-08-11T14:16:02+09:00 [end] 05_analyze (1s) 
- 2026-08-11T14:18:40+09:00 [start] 05_analyze (s) 
- 2026-08-11T14:18:41+09:00 [end] 05_analyze (1s) 
- 2026-08-11T20:13:09+09:00 [start] 07_relational (s) 
- 2026-08-11T20:34:07+09:00 [end] 07_relational (1258s) 
- 2026-08-11T20:34:10+09:00 [start] 08_headwise_profile (s) 
- 2026-08-11T20:39:36+09:00 [end] 08_headwise_profile (327s) 
- 2026-08-11T20:39:36+09:00 [start] 08_feature_sweep (s) 
- 2026-08-11T20:39:37+09:00 [end] 08_feature_sweep (0s) 
- 2026-08-11T20:39:39+09:00 [start] 09_compaction_bench (s) 
- 2026-08-11T20:41:42+09:00 [end] 09_compaction_bench (123s) 
- 2026-08-11T20:41:50+09:00 [start] 11_allocation (s) 
- 2026-08-11T21:52:25+09:00 [end] 11_allocation (4235s) 
- 2026-08-11T21:52:30+09:00 [start] 12_clip_baseline (s) 
- 2026-08-11T21:52:30+09:00 [error] 12_clip_baseline (0s) 
- 2026-08-11T21:52:41+09:00 [start] 03_main_shard0 (s) 
- 2026-08-11T22:23:06+09:00 [end] 03_main_shard0 (1825s) 
- 2026-08-11T22:23:09+09:00 [start] 04_profile_shard0 (s) 
- 2026-08-11T22:28:39+09:00 [end] 04_profile_shard0 (330s) 

## BLOCKED

없음