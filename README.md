# Serum Builder

Serum Builder è uno strumento da riga di comando per generare preset `.fxp` di Serum partendo da codice. Invece di disegnare wavetable e collegare modulazioni a mano nell'interfaccia grafica, descrivi il suono che vuoi in termini matematici e logici: una funzione, una serie di parametri, una lista di connessioni. Il sistema trasforma tutto questo in un file `.fxp` pronto da caricare in Serum.

Il progetto è costruito come una pipeline modulare a stadi, dove ogni passaggio — dalla validazione degli input alla scrittura su disco — è separato e indipendente. Questo lo rende facile da estendere, testare e adattare a flussi di lavoro automatizzati.

---

## Comandi CLI

### Help

```bash
python cli.py --help
```

### Wavetable da funzione matematica

```bash
# Sinusoide semplice
python cli.py --nome Test --base base.fxp --funzione "sin(x)"

# Serie armonica (approssimazione onda quadra)
python cli.py --nome Quadra --base base.fxp \
  --funzione "sin(x) + sin(3*x)/3 + sin(5*x)/5" \
  --frame 16

# Onda con componenti pari e dispari
python cli.py --nome Complessa --base base.fxp \
  --funzione "sin(x) + sin(2*x)/2 + sin(3*x)/3" \
  --frame 32
```

### Wavetable da file .wav

```bash
python cli.py --nome DaFile --base base.fxp --wav mia_wavetable.wav
```

### Modulazioni

```bash
# Collegamento singolo
python cli.py --nome Mod1 --base base.fxp --mod "LFO1,FILTER_CUTOFF,0.8"

# Più collegamenti (ripeti --mod)
python cli.py --nome Mod2 --base base.fxp \
  --mod "LFO1,FILTER_CUTOFF,0.8" \
  --mod "ENV2,OSC_A_PITCH,0.3" \
  --mod "MODWHEEL,LFO1_RATE,1.0" \
  --mod "VELOCITY,MASTER_VOL,0.5"

# Modulazione inversa (quantità negativa)
python cli.py --nome ModInversa --base base.fxp --mod "LFO1,FILTER_CUTOFF,-0.8"
```

### Parametri statici

```bash
python cli.py --nome Params --base base.fxp \
  --param "filter_cutoff,0.4" \
  --param "filter_res,0.6" \
  --param "master_vol,0.85"
```

### Envelopes

```bash
# Percussivo
python cli.py --nome Perc --base base.fxp --env "ENV1,0.01,0.1,0.5,0.3"

# Lento (pad)
python cli.py --nome Pad --base base.fxp --env "ENV2,0.8,0.5,0.9,1.2"
```

### Comando completo

```bash
python cli.py \
  --nome PresetCompleto \
  --base base.fxp \
  --funzione "sin(x) + sin(3*x)/3 + sin(5*x)/5" \
  --frame 16 \
  --mod "LFO1,FILTER_CUTOFF,0.8" \
  --mod "ENV2,OSC_A_PITCH,0.3" \
  --mod "MODWHEEL,LFO1_RATE,1.0" \
  --param "filter_cutoff,0.4" \
  --param "filter_res,0.55" \
  --param "master_vol,0.85" \
  --env "ENV1,0.01,0.15,0.6,0.5" \
  --env "ENV2,0.5,0.8,0.3,1.2"
```

### Formato degli argomenti ripetibili

```
--mod   "SORGENTE,DESTINAZIONE,QUANTITA"    # quantità da -1.0 a 1.0
--param "NOME,VALORE"                       # valore da 0.0 a 1.0
--env   "TARGET,ATTACK,DECAY,SUSTAIN,RELEASE"
```

---

## Struttura

```
serum_builder/
│
├── cli.py                        # Punto di ingresso da terminale
├── main.py                       # Punto di ingresso con esempio hardcodato
│
├── models/                       # Definizione degli input
│   └── input_schema.py           # PresetInput, WavetableInput, ModulazioneInput,
│                                 # ParametroInput, EnvelopeInput
│
├── maps/                         # Tabelle di conversione nome → indice Serum
│   ├── sources.py                # SORGENTI: LFO1, ENV2, VELOCITY, ecc.
│   └── destinations.py           # DESTINAZIONI: FILTER_CUTOFF, OSC_A_PITCH, ecc.
│
├── core/                         # Logica della pipeline (funzioni pure)
│   ├── pipeline.py               # Orchestratore: esegue gli stadi in sequenza
│   ├── validator.py              # Stadio 1 — controlla errori negli input
│   ├── wavetable.py              # Stadio 2 — funzione/array/file → frame numpy
│   ├── modulation.py             # Stadio 3 — ModulazioneInput → bytes mod matrix
│   │                             # Stadio 4 — ParametroInput/Envelope → patch dict
│   └── encoder.py                # Stadio 5 — applica tutto al .fxp base
│
├── io/                           # Effetti collaterali (unico punto di I/O)
│   └── writer.py                 # Stadio 6 — scrive .fxp e .wav su disco
│
└── output/                       # Cartella generata automaticamente
    ├── NomePreset.fxp            # Preset finale da caricare in Serum
    └── NomePreset_wavetable.wav  # Wavetable generata (se da funzione o array)
```

## Pipeline

```
PresetInput
    │
    ▼
[1] valida_input         → controlla errori prima di procedere
    │
    ▼
[2] risolvi_wavetable    → funzione/array/file → frame numpy normalizzati
    │
    ▼
[3] codifica_modulazioni → ModulazioneInput → bytes (mod matrix)
    │
    ▼
[4] codifica_parametri   → ParametroInput + EnvelopeInput → patch dict
    │
    ▼
[5] assembla_fxp         → applica tutto al file .fxp base
    │
    ▼
[6] scrivi_output        → scrive .fxp e .wav nella cartella output/
```

## Utilizzo

```python
from models.input_schema import *
from core.pipeline import esegui_pipeline
import numpy as np

preset = PresetInput(
    nome="MioPreset",
    base_fxp="base.fxp",
    wavetable=WavetableInput(
        funzione=lambda x: np.sin(x) + np.sin(3*x)/3,
        n_frame=8,
    ),
    modulazioni=[
        ModulazioneInput("LFO1", "FILTER_CUTOFF", quantita=0.75),
    ],
    parametri=[
        ParametroInput("filter_cutoff", 0.4),
    ],
    envelopes=[
        EnvelopeInput(attack=0.01, decay=0.2, sustain=0.5, release=0.8),
    ],
)

esegui_pipeline(preset)
```

## Note importanti

- Gli **offset** nel file `.fxp` (in `modulation.py` e `encoder.py`) vanno
  calibrati sulla tua versione di Serum confrontando due preset con un hex editor.
- Gli **indici** in `sources.py` e `destinations.py` vanno verificati allo stesso modo.
- Il file `base.fxp` deve essere un preset valido di Serum da cui partire.

## Dipendenze

```
pip install numpy scipy
```
