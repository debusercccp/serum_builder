import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
from models.input_schema import (
    PresetInput, WavetableInput, ModulazioneInput,
    ParametroInput, EnvelopeInput
)
from core.pipeline import esegui_pipeline


def esempio():
    """
    Esempio completo: genera un preset con wavetable da funzione,
    parametri statici, modulazioni e un envelope personalizzato.
    
    NOTA: sostituisci 'base.fxp' con un preset .fxp reale di Serum.
    """

    preset = PresetInput(
        nome="SerieArmoniche",
        base_fxp="base.fxp",   # ← metti qui il tuo preset base

        # --- Wavetable da funzione matematica ---
        wavetable=WavetableInput(
            funzione=lambda x: np.sin(x) + np.sin(3*x)/3 + np.sin(5*x)/5,
            n_frame=16,
        ),

        # --- Parametri statici ---
        parametri=[
            ParametroInput("filter_cutoff", 0.4),
            ParametroInput("filter_res",    0.55),
            ParametroInput("master_vol",    0.85),
        ],

        # --- Modulazioni (collegamento sorgente → destinazione) ---
        modulazioni=[
            ModulazioneInput("LFO1", "FILTER_CUTOFF", quantita=0.8),
            ModulazioneInput("ENV2", "OSC_A_PITCH",   quantita=0.3),
            ModulazioneInput("MODWHEEL", "LFO1_RATE", quantita=1.0),
            ModulazioneInput("VELOCITY", "MASTER_VOL", quantita=0.5),
        ],

        # --- Envelope ---
        envelopes=[
            EnvelopeInput(attack=0.02, decay=0.15, sustain=0.6, release=0.5, target="ENV1"),
            EnvelopeInput(attack=0.5,  decay=0.8,  sustain=0.3, release=1.2, target="ENV2"),
        ],
    )

    esegui_pipeline(preset)


if __name__ == "__main__":
    esempio()
