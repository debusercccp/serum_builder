import os
from models.input_schema import PresetInput, WavetableInput, ModulazioneInput, ParametroInput
from maps.sources import SORGENTI
from maps.destinations import DESTINAZIONI


def valida_input(preset: PresetInput) -> PresetInput:
    """
    Stadio 1 della pipeline.
    Controlla che tutti gli input siano corretti prima di procedere.
    Lancia ValueError con lista di tutti gli errori trovati.
    """
    errori = []

    # Controlla file base
    if not os.path.exists(preset.base_fxp):
        errori.append(f"File base non trovato: {preset.base_fxp}")

    # Controlla wavetable
    if preset.wavetable:
        errori += _valida_wavetable(preset.wavetable)

    # Controlla modulazioni
    for mod in preset.modulazioni:
        errori += _valida_modulazione(mod)

    # Controlla parametri
    for par in preset.parametri:
        errori += _valida_parametro(par)

    # Controlla envelopes
    for env in preset.envelopes:
        errori += _valida_envelope(env)

    if errori:
        raise ValueError("Errori di validazione:\n" + "\n".join(f"  - {e}" for e in errori))

    return preset  # passa allo stadio successivo


def _valida_wavetable(wt: WavetableInput) -> list[str]:
    errori = []
    fonti = [wt.funzione, wt.campioni, wt.file_wav]
    n_fonti = sum(f is not None for f in fonti)

    if n_fonti == 0:
        errori.append("WavetableInput: nessuna sorgente specificata (funzione, campioni o file_wav)")
    elif n_fonti > 1:
        errori.append("WavetableInput: specifica esattamente UNA sorgente")

    if wt.file_wav and not os.path.exists(wt.file_wav):
        errori.append(f"WavetableInput: file non trovato: {wt.file_wav}")

    if wt.n_frame < 1 or wt.n_frame > 256:
        errori.append(f"WavetableInput: n_frame deve essere tra 1 e 256 (ricevuto {wt.n_frame})")

    return errori


def _valida_modulazione(mod: ModulazioneInput) -> list[str]:
    errori = []

    if mod.sorgente not in SORGENTI:
        errori.append(f"Modulazione: sorgente sconosciuta '{mod.sorgente}'. "
                      f"Disponibili: {list(SORGENTI.keys())}")

    if mod.destinazione not in DESTINAZIONI:
        errori.append(f"Modulazione: destinazione sconosciuta '{mod.destinazione}'. "
                      f"Disponibili: {list(DESTINAZIONI.keys())}")

    if not -1.0 <= mod.quantita <= 1.0:
        errori.append(f"Modulazione {mod.sorgente}→{mod.destinazione}: "
                      f"quantità {mod.quantita} fuori range [-1.0, 1.0]")

    if mod.aux and mod.aux not in SORGENTI:
        errori.append(f"Modulazione: aux sorgente sconosciuta '{mod.aux}'")

    return errori


def _valida_parametro(par: ParametroInput) -> list[str]:
    if not 0.0 <= par.valore <= 1.0:
        return [f"Parametro '{par.nome}': valore {par.valore} fuori range [0.0, 1.0]"]
    return []


def _valida_envelope(env) -> list[str]:
    errori = []
    campi_tempo = {"attack": env.attack, "decay": env.decay, "release": env.release}
    for nome, val in campi_tempo.items():
        if val < 0:
            errori.append(f"Envelope {env.target}: {nome} non può essere negativo")
    if not 0.0 <= env.sustain <= 1.0:
        errori.append(f"Envelope {env.target}: sustain {env.sustain} fuori range [0.0, 1.0]")
    return errori
