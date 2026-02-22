from dataclasses import dataclass, field
from typing import Callable, Optional
import numpy as np


@dataclass
class WavetableInput:
    """Definisce la forma d'onda. Specifica esattamente UNA sorgente."""
    funzione: Optional[Callable] = None     # es. lambda x: np.sin(x)
    campioni: Optional[np.ndarray] = None   # array grezzo
    file_wav: Optional[str] = None          # path a .wav esistente
    n_frame: int = 8                        # quanti frame generare (se da funzione)


@dataclass
class ParametroInput:
    """Un singolo parametro statico di Serum (valore 0.0 – 1.0)."""
    nome: str
    valore: float


@dataclass
class ModulazioneInput:
    """Un collegamento nella mod matrix di Serum."""
    sorgente: str                           # es. "LFO1"
    destinazione: str                       # es. "FILTER_CUTOFF"
    quantita: float                         # -1.0 – 1.0
    aux: Optional[str] = None              # sorgente secondaria opzionale


@dataclass
class EnvelopeInput:
    """Forma ADSR di un envelope."""
    attack: float = 0.01
    decay: float = 0.1
    sustain: float = 0.7
    release: float = 0.3
    target: str = "ENV1"                   # quale envelope di Serum


@dataclass
class PresetInput:
    """Input completo per generare un preset .fxp di Serum."""
    nome: str
    base_fxp: str                          # path al preset .fxp di partenza
    wavetable: Optional[WavetableInput] = None
    parametri: list[ParametroInput] = field(default_factory=list)
    modulazioni: list[ModulazioneInput] = field(default_factory=list)
    envelopes: list[EnvelopeInput] = field(default_factory=list)
