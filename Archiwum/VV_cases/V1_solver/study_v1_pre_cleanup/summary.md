# V1 Summary

| case | purpose | Re | mesh | upstream | downstream | cells | regime | Cd_mean | Cl_rms | f [Hz] | St | status |
|---|---|---:|---|---:|---:|---:|---|---:|---:|---:|---:|---|
| baseline_coarse_Re160 | mesh-study | 160.0 | coarse | 8.0D | 20.0D | 8598 | periodic | 2.539713778731536 | 0.03519574745916982 | 5.589045598739485 | 0.3318034986059061 | ok |
| baseline_medium_Re100 | transition-sweep | 100.0 | medium | 8.0D | 20.0D | 44492 | steady-or-weakly-unsteady | 3.1014815118309658 | 0.0002664653869761276 | None | None | ok |
| baseline_medium_Re120 | transition-sweep | 120.0 | medium | 8.0D | 20.0D | 44492 | steady-or-weakly-unsteady | 2.8684561890625946 | 0.00037482373668180105 | None | None | ok |
| baseline_medium_Re140 | transition-sweep | 140.0 | medium | 8.0D | 20.0D | 44492 | steady-or-weakly-unsteady | 2.7008767294495706 | 0.0006281986239842069 | None | None | ok |
| baseline_medium_Re160 | mesh-study+transition-sweep | 160.0 | medium | 8.0D | 20.0D | 44492 | periodic | 2.5743133867849854 | 0.0021573052642793423 | 5.763257413779405 | 0.3421458886808354 | ok |
| long_medium_Re160 | streamwise-domain-check | 160.0 | medium | 10.0D | 30.0D | 46040 | periodic | 2.5763303578392858 | 0.002937950541988483 | 5.7644300864504485 | 0.34221550645154375 | ok |
| long_target100k_Re160 | mesh-study replacement around 100k cells | 160.0 | target100k | 10.0D | 30.0D | 104104 | periodic | 2.585379554177505 | 0.005137039700922534 | 5.82586580189343 | 0.3458627454949926 | ok |
