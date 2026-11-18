# Regression gate

Status: **FAIL**

- Protected tasks lost

| Metric | Base | Candidate |
|---|---:|---:|
| successes | 48 | 36 |
| episodes | 90 | 90 |
| median_tokens | 12450.0 | 12450.0 |
| median_seconds | 8.255705100018531 | 8.047591950016795 |

## Base

- Batch `base_final_20261118_172416_841840`
- Version `base`
- Evaluation commit `43c216b7083eddbda22f7d7081cc9d0c2e6d64f3`
- Manifest `versions/base/manifest.json`
- Manifest SHA-256 `8748937fcff760a03d6935c0b013d2058ebf455c5f34b39c6faaef2c52d4a399`

## Candidate

- Batch `truncate2000_final_20261118_190525_502247`
- Version `truncate2000`
- Evaluation commit `dfeeb5e2fa15f7bef98d4dd020854c8e2ecbdc90`
- Manifest `versions/truncate2000/manifest.json`
- Manifest SHA-256 `1b6dc9d758fa0375ec345e34cb1737587649b60ba8802b374bd92b16ab6edba3`

Protected tasks: 16

Lost tasks: 5

Token median change: +0.00%

Time median change: -2.52%

## Changed tasks


### user_task_17

- Base, run 1, utility=True, [trace tr-d5b50c4f8c1d21785967cc94a79097b4](http://127.0.0.1:5007/#/experiments/3/traces?workflowType=genai&traceId=tr-d5b50c4f8c1d21785967cc94a79097b4), record `results/base_final_20261118_172416_841840/user_task_17_run1.json`
- Base, run 2, utility=True, [trace tr-5af92cc225748c3e74a34404c23db96d](http://127.0.0.1:5007/#/experiments/3/traces?workflowType=genai&traceId=tr-5af92cc225748c3e74a34404c23db96d), record `results/base_final_20261118_172416_841840/user_task_17_run2.json`
- Base, run 3, utility=True, [trace tr-72e2c7b209d1f3e1ad845df4246e4973](http://127.0.0.1:5007/#/experiments/3/traces?workflowType=genai&traceId=tr-72e2c7b209d1f3e1ad845df4246e4973), record `results/base_final_20261118_172416_841840/user_task_17_run3.json`
- Candidate, run 1, utility=False, [trace tr-7faf3d541089417a2daac13b2d8d25ff](http://127.0.0.1:5007/#/experiments/3/traces?workflowType=genai&traceId=tr-7faf3d541089417a2daac13b2d8d25ff), record `results/truncate2000_final_20261118_190525_502247/user_task_17_run1.json`
- Candidate, run 2, utility=False, [trace tr-265e992e496b49a2d59aa78b2c395b6d](http://127.0.0.1:5007/#/experiments/3/traces?workflowType=genai&traceId=tr-265e992e496b49a2d59aa78b2c395b6d), record `results/truncate2000_final_20261118_190525_502247/user_task_17_run2.json`
- Candidate, run 3, utility=False, [trace tr-cad03ae64733013b6f52802989818bd1](http://127.0.0.1:5007/#/experiments/3/traces?workflowType=genai&traceId=tr-cad03ae64733013b6f52802989818bd1), record `results/truncate2000_final_20261118_190525_502247/user_task_17_run3.json`

### user_task_25

- Base, run 1, utility=True, [trace tr-485bf783c65dbb441d31114febb692db](http://127.0.0.1:5007/#/experiments/3/traces?workflowType=genai&traceId=tr-485bf783c65dbb441d31114febb692db), record `results/base_final_20261118_172416_841840/user_task_25_run1.json`
- Base, run 2, utility=True, [trace tr-e7f80ad964beaa9f1422bb04bd2c1ef0](http://127.0.0.1:5007/#/experiments/3/traces?workflowType=genai&traceId=tr-e7f80ad964beaa9f1422bb04bd2c1ef0), record `results/base_final_20261118_172416_841840/user_task_25_run2.json`
- Base, run 3, utility=True, [trace tr-3037624942e304b6dd8575eee09f6bd8](http://127.0.0.1:5007/#/experiments/3/traces?workflowType=genai&traceId=tr-3037624942e304b6dd8575eee09f6bd8), record `results/base_final_20261118_172416_841840/user_task_25_run3.json`
- Candidate, run 1, utility=False, [trace tr-c9621263a7bdaf3c53246fc05bca8038](http://127.0.0.1:5007/#/experiments/3/traces?workflowType=genai&traceId=tr-c9621263a7bdaf3c53246fc05bca8038), record `results/truncate2000_final_20261118_190525_502247/user_task_25_run1.json`
- Candidate, run 2, utility=False, [trace tr-09ce719fb2ab591ef1fa16eed9f6638d](http://127.0.0.1:5007/#/experiments/3/traces?workflowType=genai&traceId=tr-09ce719fb2ab591ef1fa16eed9f6638d), record `results/truncate2000_final_20261118_190525_502247/user_task_25_run2.json`
- Candidate, run 3, utility=False, [trace tr-219dee75a3d8d3911350e504c249c683](http://127.0.0.1:5007/#/experiments/3/traces?workflowType=genai&traceId=tr-219dee75a3d8d3911350e504c249c683), record `results/truncate2000_final_20261118_190525_502247/user_task_25_run3.json`

### user_task_26

- Base, run 1, utility=True, [trace tr-630cd9538c91b43c164c949e1e9e2a12](http://127.0.0.1:5007/#/experiments/3/traces?workflowType=genai&traceId=tr-630cd9538c91b43c164c949e1e9e2a12), record `results/base_final_20261118_172416_841840/user_task_26_run1.json`
- Base, run 2, utility=True, [trace tr-07222dca4655d3a8b04426879446cb40](http://127.0.0.1:5007/#/experiments/3/traces?workflowType=genai&traceId=tr-07222dca4655d3a8b04426879446cb40), record `results/base_final_20261118_172416_841840/user_task_26_run2.json`
- Base, run 3, utility=True, [trace tr-4d0f880c9a6386bcc1df6218cf1828f6](http://127.0.0.1:5007/#/experiments/3/traces?workflowType=genai&traceId=tr-4d0f880c9a6386bcc1df6218cf1828f6), record `results/base_final_20261118_172416_841840/user_task_26_run3.json`
- Candidate, run 1, utility=False, [trace tr-b70bb55bcd54fac1dbc1567db71f22fb](http://127.0.0.1:5007/#/experiments/3/traces?workflowType=genai&traceId=tr-b70bb55bcd54fac1dbc1567db71f22fb), record `results/truncate2000_final_20261118_190525_502247/user_task_26_run1.json`
- Candidate, run 2, utility=False, [trace tr-ffecb927e06ff2b2fcc9b5fecc62c679](http://127.0.0.1:5007/#/experiments/3/traces?workflowType=genai&traceId=tr-ffecb927e06ff2b2fcc9b5fecc62c679), record `results/truncate2000_final_20261118_190525_502247/user_task_26_run2.json`
- Candidate, run 3, utility=False, [trace tr-c43e18e4e3f2cf44f9f91c5ad07489f5](http://127.0.0.1:5007/#/experiments/3/traces?workflowType=genai&traceId=tr-c43e18e4e3f2cf44f9f91c5ad07489f5), record `results/truncate2000_final_20261118_190525_502247/user_task_26_run3.json`

### user_task_35

- Base, run 1, utility=True, [trace tr-8b03625c8bd0558fd3cb619eb99e1bd1](http://127.0.0.1:5007/#/experiments/3/traces?workflowType=genai&traceId=tr-8b03625c8bd0558fd3cb619eb99e1bd1), record `results/base_final_20261118_172416_841840/user_task_35_run1.json`
- Base, run 2, utility=True, [trace tr-49a17efcb937ccb7b0db201dbe5fb027](http://127.0.0.1:5007/#/experiments/3/traces?workflowType=genai&traceId=tr-49a17efcb937ccb7b0db201dbe5fb027), record `results/base_final_20261118_172416_841840/user_task_35_run2.json`
- Base, run 3, utility=True, [trace tr-23be2345de670090e4c1010925fcf5f1](http://127.0.0.1:5007/#/experiments/3/traces?workflowType=genai&traceId=tr-23be2345de670090e4c1010925fcf5f1), record `results/base_final_20261118_172416_841840/user_task_35_run3.json`
- Candidate, run 1, utility=False, [trace tr-08a2235cc30169947e0276fa7d153040](http://127.0.0.1:5007/#/experiments/3/traces?workflowType=genai&traceId=tr-08a2235cc30169947e0276fa7d153040), record `results/truncate2000_final_20261118_190525_502247/user_task_35_run1.json`
- Candidate, run 2, utility=False, [trace tr-a01dee87ac2c81be882b1c8423bb31c0](http://127.0.0.1:5007/#/experiments/3/traces?workflowType=genai&traceId=tr-a01dee87ac2c81be882b1c8423bb31c0), record `results/truncate2000_final_20261118_190525_502247/user_task_35_run2.json`
- Candidate, run 3, utility=False, [trace tr-5b13f5b124c0576badbc97f78d9b2161](http://127.0.0.1:5007/#/experiments/3/traces?workflowType=genai&traceId=tr-5b13f5b124c0576badbc97f78d9b2161), record `results/truncate2000_final_20261118_190525_502247/user_task_35_run3.json`

### user_task_39

- Base, run 1, utility=True, [trace tr-08be181086ff9134d1972f07893baa03](http://127.0.0.1:5007/#/experiments/3/traces?workflowType=genai&traceId=tr-08be181086ff9134d1972f07893baa03), record `results/base_final_20261118_172416_841840/user_task_39_run1.json`
- Base, run 2, utility=True, [trace tr-6fc530b674c12d99591ec9987b335c6f](http://127.0.0.1:5007/#/experiments/3/traces?workflowType=genai&traceId=tr-6fc530b674c12d99591ec9987b335c6f), record `results/base_final_20261118_172416_841840/user_task_39_run2.json`
- Base, run 3, utility=True, [trace tr-cc9dda58c5d7d4788795642c4af3b2cb](http://127.0.0.1:5007/#/experiments/3/traces?workflowType=genai&traceId=tr-cc9dda58c5d7d4788795642c4af3b2cb), record `results/base_final_20261118_172416_841840/user_task_39_run3.json`
- Candidate, run 1, utility=False, [trace tr-02b2e069b682092a0d57821dc9ad655a](http://127.0.0.1:5007/#/experiments/3/traces?workflowType=genai&traceId=tr-02b2e069b682092a0d57821dc9ad655a), record `results/truncate2000_final_20261118_190525_502247/user_task_39_run1.json`
- Candidate, run 2, utility=False, [trace tr-1a8e8f8d859841fda53ae67c6844ff67](http://127.0.0.1:5007/#/experiments/3/traces?workflowType=genai&traceId=tr-1a8e8f8d859841fda53ae67c6844ff67), record `results/truncate2000_final_20261118_190525_502247/user_task_39_run2.json`
- Candidate, run 3, utility=False, [trace tr-3c48a990ab31393d78c5098d7deff0c2](http://127.0.0.1:5007/#/experiments/3/traces?workflowType=genai&traceId=tr-3c48a990ab31393d78c5098d7deff0c2), record `results/truncate2000_final_20261118_190525_502247/user_task_39_run3.json`

### user_task_34

- Base, run 1, utility=False, [trace tr-5b7db4cd7c885a3b985145170d96545f](http://127.0.0.1:5007/#/experiments/3/traces?workflowType=genai&traceId=tr-5b7db4cd7c885a3b985145170d96545f), record `results/base_final_20261118_172416_841840/user_task_34_run1.json`
- Base, run 2, utility=False, [trace tr-c3e0c3addf8af4695b609069e9bf88f1](http://127.0.0.1:5007/#/experiments/3/traces?workflowType=genai&traceId=tr-c3e0c3addf8af4695b609069e9bf88f1), record `results/base_final_20261118_172416_841840/user_task_34_run2.json`
- Base, run 3, utility=False, [trace tr-226e70cd8604c94c8d14aea1e0b15eed](http://127.0.0.1:5007/#/experiments/3/traces?workflowType=genai&traceId=tr-226e70cd8604c94c8d14aea1e0b15eed), record `results/base_final_20261118_172416_841840/user_task_34_run3.json`
- Candidate, run 1, utility=True, [trace tr-754b3220e0b0fd953ee045e43330efd3](http://127.0.0.1:5007/#/experiments/3/traces?workflowType=genai&traceId=tr-754b3220e0b0fd953ee045e43330efd3), record `results/truncate2000_final_20261118_190525_502247/user_task_34_run1.json`
- Candidate, run 2, utility=True, [trace tr-8a55a29c12454c589cecf9eacf1f14c8](http://127.0.0.1:5007/#/experiments/3/traces?workflowType=genai&traceId=tr-8a55a29c12454c589cecf9eacf1f14c8), record `results/truncate2000_final_20261118_190525_502247/user_task_34_run2.json`
- Candidate, run 3, utility=True, [trace tr-535564d96f33d79537dddf27828e07b4](http://127.0.0.1:5007/#/experiments/3/traces?workflowType=genai&traceId=tr-535564d96f33d79537dddf27828e07b4), record `results/truncate2000_final_20261118_190525_502247/user_task_34_run3.json`
