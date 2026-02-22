import struct
from models.input_schema import PresetInput, ModulazioneInput, EnvelopeInput
from maps.sources import SORGENTI
from maps.destinations import DESTINAZIONI

# Offset della mod matrix nel file .fxp (da verificare con hex editor)
OFFSET_MOD_MATRIX = 0x2A0
SLOT_SIZE = 16        # byte per slot (4 float × 4 byte)
MAX_SLOT = 32         # Serum ha 32 slot nella mod matrix


def codifica_modulazioni(preset: PresetInput) -> PresetInput:
    """
    Stadio 3 della pipeline.
    Converte ogni ModulazioneInput in bytes pronti per il file .fxp.
    Aggiunge i bytes come attributo _mod_bytes al preset.
    """
    if len(preset.modulazioni) > MAX_SLOT:
        raise ValueError(f"Troppi collegamenti: massimo {MAX_SLOT}, ricevuti {len(preset.modulazioni)}")

    slots = []
    for mod in preset.modulazioni:
        slots.append(_codifica_slot(mod))

    # Pad con slot vuoti fino a MAX_SLOT
    slot_vuoto = struct.pack(">ffff", 255.0, 255.0, 0.5, 255.0)
    while len(slots) < MAX_SLOT:
        slots.append(slot_vuoto)

    preset._mod_bytes = b"".join(slots)
    return preset


def _codifica_slot(mod: ModulazioneInput) -> bytes:
    src_idx = float(SORGENTI[mod.sorgente])
    dst_idx = float(DESTINAZIONI[mod.destinazione])
    qty_norm = (mod.quantita + 1.0) / 2.0  # da [-1,1] a [0,1]
    aux_idx = float(SORGENTI[mod.aux]) if mod.aux else 255.0

    return struct.pack(">ffff", src_idx, dst_idx, qty_norm, aux_idx)


def codifica_parametri(preset: PresetInput) -> PresetInput:
    """
    Stadio 4 della pipeline.
    Converte parametri statici ed envelopes in una mappa offset→bytes.
    """
    # Mappa nome parametro → offset nel file (da verificare/estendere)
    OFFSET_PARAMETRI: dict[str, int] = {
        "filter_cutoff": 0x1A4,
        "filter_res":    0x1A8,
        "filter_drive":  0x1AC,
        "master_vol":    0x3F0,
        "master_pan":    0x3F4,
    }

    OFFSET_ENVELOPE: dict[str, dict[str, int]] = {
        "ENV1": {"attack": 0x280, "decay": 0x284, "sustain": 0x288, "release": 0x28C},
        "ENV2": {"attack": 0x290, "decay": 0x294, "sustain": 0x298, "release": 0x29C},
        "ENV3": {"attack": 0x2A0, "decay": 0x2A4, "sustain": 0x2A8, "release": 0x2AC},
    }

    patch: dict[int, bytes] = {}

    for par in preset.parametri:
        if par.nome in OFFSET_PARAMETRI:
            offset = OFFSET_PARAMETRI[par.nome]
            patch[offset] = struct.pack(">f", par.valore)
        else:
            print(f"[WARN] Parametro '{par.nome}' non mappato, ignorato.")

    for env in preset.envelopes:
        if env.target in OFFSET_ENVELOPE:
            offsets = OFFSET_ENVELOPE[env.target]
            patch[offsets["attack"]]  = struct.pack(">f", env.attack)
            patch[offsets["decay"]]   = struct.pack(">f", env.decay)
            patch[offsets["sustain"]] = struct.pack(">f", env.sustain)
            patch[offsets["release"]] = struct.pack(">f", env.release)

    preset._param_patch = patch
    return preset
