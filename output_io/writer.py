import os
from scipy.io import wavfile
from models.input_schema import PresetInput


def scrivi_output(preset: PresetInput) -> PresetInput:
    """
    Stadio 6 della pipeline — unico stadio con effetti collaterali.
    Scrive su disco il file .fxp finale e, se presente, la wavetable .wav.
    """
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # Scrivi wavetable .wav
    if preset.wavetable and preset.wavetable.campioni is not None:
        wav_path = os.path.join(output_dir, f"{preset.nome}_wavetable.wav")
        wavfile.write(wav_path, 44100, preset.wavetable.campioni)
        print(f"[OK] Wavetable salvata: {wav_path}")

    # Scrivi preset .fxp
    if hasattr(preset, "_fxp_bytes"):
        fxp_path = os.path.join(output_dir, f"{preset.nome}.fxp")
        with open(fxp_path, "wb") as f:
            f.write(preset._fxp_bytes)
        print(f"[OK] Preset salvato: {fxp_path}")

    return preset
