import numpy as np
from scipy.io import wavfile
from models.input_schema import PresetInput, WavetableInput

FRAME_SIZE = 2048  # dimensione standard di Serum


def risolvi_wavetable(preset: PresetInput) -> PresetInput:
    """
    Stadio 2 della pipeline.
    Converte qualsiasi tipo di sorgente wavetable in un np.ndarray
    di frame normalizzati da FRAME_SIZE campioni ciascuno.
    Il risultato viene salvato in preset.wavetable.campioni.
    """
    if not preset.wavetable:
        return preset

    wt = preset.wavetable

    if wt.funzione:
        frames = _da_funzione(wt.funzione, wt.n_frame)
    elif wt.campioni is not None:
        frames = _da_campioni(wt.campioni)
    elif wt.file_wav:
        frames = _da_file(wt.file_wav)

    # Salva i frame risolti come campioni (sovrascrive la sorgente originale)
    preset.wavetable.campioni = frames
    preset.wavetable.funzione = None
    preset.wavetable.file_wav = None

    return preset


def _da_funzione(f, n_frame: int) -> np.ndarray:
    """Genera n_frame frame applicando la funzione su [0, 2π]."""
    x = np.linspace(0, 2 * np.pi, FRAME_SIZE, endpoint=False)
    frames = []
    for i in range(n_frame):
        # Interpola parametricamente se la funzione accetta due argomenti
        try:
            t = i / max(n_frame - 1, 1)  # t va da 0 a 1
            campioni = f(x, t)
        except TypeError:
            campioni = f(x)
        frames.append(_normalizza(campioni))
    return np.concatenate(frames).astype(np.float32)


def _da_campioni(campioni: np.ndarray) -> np.ndarray:
    """Adatta un array grezzo a multipli di FRAME_SIZE."""
    # Ritaglia o padda per avere multipli esatti di FRAME_SIZE
    n_frame = max(1, len(campioni) // FRAME_SIZE)
    campioni = campioni[:n_frame * FRAME_SIZE]
    frames = campioni.reshape(n_frame, FRAME_SIZE)
    normalizzati = np.array([_normalizza(f) for f in frames])
    return normalizzati.flatten().astype(np.float32)


def _da_file(path: str) -> np.ndarray:
    """Legge un .wav e lo tratta come wavetable multi-frame."""
    rate, data = wavfile.read(path)
    if data.ndim > 1:
        data = data[:, 0]  # prendi solo il canale sinistro
    data = data.astype(np.float32)
    data /= np.iinfo(np.int16).max if data.max() > 1.0 else 1.0
    return _da_campioni(data)


def _normalizza(campioni: np.ndarray) -> np.ndarray:
    """Normalizza tra -1.0 e 1.0, gestisce il caso di silenzio."""
    massimo = np.max(np.abs(campioni))
    if massimo < 1e-10:
        return campioni
    return campioni / massimo
