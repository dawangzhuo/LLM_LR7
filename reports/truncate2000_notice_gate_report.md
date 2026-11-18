# Regression gate

Status: **FAIL**

- Protected tasks lost

| Metric | Base | Candidate |
|---|---:|---:|
| successes | 48 | 36 |
| episodes | 90 | 90 |
| median_tokens | 12450.0 | 12122.0 |
| median_seconds | 8.255705100018531 | 7.356706049991772 |

## Base

- Batch `base_final_20261118_172416_841840`
- Version `base`
- Evaluation commit `43c216b7083eddbda22f7d7081cc9d0c2e6d64f3`
- Manifest `versions/base/manifest.json`
- Manifest SHA-256 `8748937fcff760a03d6935c0b013d2058ebf455c5f34b39c6faaef2c52d4a399`

## Candidate

- Batch `truncate2000_notice_final_20261118_192648_469535`
- Version `truncate2000_notice`
- Evaluation commit `aaec3b6cf110adb07f079ee4d3ff6133080e10a2`
- Manifest `versions/truncate2000_notice/manifest.json`
- Manifest SHA-256 `e92402284c367266d620a933e415d8abff0fa0614500951311afbc36a1f29a37`

Protected tasks: 16

Lost tasks: 5

Token median change: -2.63%

Time median change: -10.89%

## Changed tasks


### user_task_17

- Base, run 1, utility=True, trace `tr-d5b50c4f8c1d21785967cc94a79097b4`, record `results/base_final_20261118_172416_841840/user_task_17_run1.json`
- Base, run 2, utility=True, trace `tr-5af92cc225748c3e74a34404c23db96d`, record `results/base_final_20261118_172416_841840/user_task_17_run2.json`
- Base, run 3, utility=True, trace `tr-72e2c7b209d1f3e1ad845df4246e4973`, record `results/base_final_20261118_172416_841840/user_task_17_run3.json`
- Candidate, run 1, utility=False, trace `tr-b3383a73cd272c917b878e4055580859`, record `results/truncate2000_notice_final_20261118_192648_469535/user_task_17_run1.json`
- Candidate, run 2, utility=False, trace `tr-8c99cdba4af3dc779ca3f6e22c47565e`, record `results/truncate2000_notice_final_20261118_192648_469535/user_task_17_run2.json`
- Candidate, run 3, utility=False, trace `tr-a6ae44674240e1087d35751179c28bfb`, record `results/truncate2000_notice_final_20261118_192648_469535/user_task_17_run3.json`

### user_task_25

- Base, run 1, utility=True, trace `tr-485bf783c65dbb441d31114febb692db`, record `results/base_final_20261118_172416_841840/user_task_25_run1.json`
- Base, run 2, utility=True, trace `tr-e7f80ad964beaa9f1422bb04bd2c1ef0`, record `results/base_final_20261118_172416_841840/user_task_25_run2.json`
- Base, run 3, utility=True, trace `tr-3037624942e304b6dd8575eee09f6bd8`, record `results/base_final_20261118_172416_841840/user_task_25_run3.json`
- Candidate, run 1, utility=False, trace `tr-5aec95f461196a786c9b17993e7f71c8`, record `results/truncate2000_notice_final_20261118_192648_469535/user_task_25_run1.json`
- Candidate, run 2, utility=False, trace `tr-92a16a2c5233b6ebded38baf401908fe`, record `results/truncate2000_notice_final_20261118_192648_469535/user_task_25_run2.json`
- Candidate, run 3, utility=False, trace `tr-b20282d85b5c18e9552953efe34159f2`, record `results/truncate2000_notice_final_20261118_192648_469535/user_task_25_run3.json`

### user_task_26

- Base, run 1, utility=True, trace `tr-630cd9538c91b43c164c949e1e9e2a12`, record `results/base_final_20261118_172416_841840/user_task_26_run1.json`
- Base, run 2, utility=True, trace `tr-07222dca4655d3a8b04426879446cb40`, record `results/base_final_20261118_172416_841840/user_task_26_run2.json`
- Base, run 3, utility=True, trace `tr-4d0f880c9a6386bcc1df6218cf1828f6`, record `results/base_final_20261118_172416_841840/user_task_26_run3.json`
- Candidate, run 1, utility=False, trace `tr-a1d9d0a24cf8536cfb665e6b0764cc73`, record `results/truncate2000_notice_final_20261118_192648_469535/user_task_26_run1.json`
- Candidate, run 2, utility=False, trace `tr-17c25ebf64a0288d8f8fa61f5d9fd6a8`, record `results/truncate2000_notice_final_20261118_192648_469535/user_task_26_run2.json`
- Candidate, run 3, utility=False, trace `tr-af8f0e24159be523c67a53688926bbd0`, record `results/truncate2000_notice_final_20261118_192648_469535/user_task_26_run3.json`

### user_task_35

- Base, run 1, utility=True, trace `tr-8b03625c8bd0558fd3cb619eb99e1bd1`, record `results/base_final_20261118_172416_841840/user_task_35_run1.json`
- Base, run 2, utility=True, trace `tr-49a17efcb937ccb7b0db201dbe5fb027`, record `results/base_final_20261118_172416_841840/user_task_35_run2.json`
- Base, run 3, utility=True, trace `tr-23be2345de670090e4c1010925fcf5f1`, record `results/base_final_20261118_172416_841840/user_task_35_run3.json`
- Candidate, run 1, utility=False, trace `tr-a3920d7dc06477de825ba02f0c489c37`, record `results/truncate2000_notice_final_20261118_192648_469535/user_task_35_run1.json`
- Candidate, run 2, utility=False, trace `tr-a182553de28f6d54ac70601e63b3b3a1`, record `results/truncate2000_notice_final_20261118_192648_469535/user_task_35_run2.json`
- Candidate, run 3, utility=False, trace `tr-95a768b26a65623a3138f91094bd7e3f`, record `results/truncate2000_notice_final_20261118_192648_469535/user_task_35_run3.json`

### user_task_39

- Base, run 1, utility=True, trace `tr-08be181086ff9134d1972f07893baa03`, record `results/base_final_20261118_172416_841840/user_task_39_run1.json`
- Base, run 2, utility=True, trace `tr-6fc530b674c12d99591ec9987b335c6f`, record `results/base_final_20261118_172416_841840/user_task_39_run2.json`
- Base, run 3, utility=True, trace `tr-cc9dda58c5d7d4788795642c4af3b2cb`, record `results/base_final_20261118_172416_841840/user_task_39_run3.json`
- Candidate, run 1, utility=False, trace `tr-eb4fa29a5e4581839345d4a649601636`, record `results/truncate2000_notice_final_20261118_192648_469535/user_task_39_run1.json`
- Candidate, run 2, utility=False, trace `tr-c917c79a3f30c2e06955e21d5d2a0f23`, record `results/truncate2000_notice_final_20261118_192648_469535/user_task_39_run2.json`
- Candidate, run 3, utility=False, trace `tr-36ecba3fade0164a4101bea78371bcad`, record `results/truncate2000_notice_final_20261118_192648_469535/user_task_39_run3.json`

### user_task_34

- Base, run 1, utility=False, trace `tr-5b7db4cd7c885a3b985145170d96545f`, record `results/base_final_20261118_172416_841840/user_task_34_run1.json`
- Base, run 2, utility=False, trace `tr-c3e0c3addf8af4695b609069e9bf88f1`, record `results/base_final_20261118_172416_841840/user_task_34_run2.json`
- Base, run 3, utility=False, trace `tr-226e70cd8604c94c8d14aea1e0b15eed`, record `results/base_final_20261118_172416_841840/user_task_34_run3.json`
- Candidate, run 1, utility=True, trace `tr-f88e5d8628987c8dc3b1e43898f050bd`, record `results/truncate2000_notice_final_20261118_192648_469535/user_task_34_run1.json`
- Candidate, run 2, utility=True, trace `tr-48174c66185c790550079cf5b682169d`, record `results/truncate2000_notice_final_20261118_192648_469535/user_task_34_run2.json`
- Candidate, run 3, utility=True, trace `tr-309a31276e8ceeb6b1d9b6adb10d9e1b`, record `results/truncate2000_notice_final_20261118_192648_469535/user_task_34_run3.json`
