from models.input_schema import PresetInput


def assembla_fxp(preset: PresetInput) -> PresetInput:
    """
    Stadio 5 della pipeline.
    Legge il file .fxp base e applica tutte le modifiche calcolate
    nei passi precedenti. Produce il bytearray finale.
    """
    with open(preset.base_fxp, "rb") as f:
        data = bytearray(f.read())

    # Applica patch parametri statici
    if hasattr(preset, "_param_patch"):
        for offset, valore_bytes in preset._param_patch.items():
            if offset + 4 <= len(data):
                data[offset:offset + 4] = valore_bytes
            else:
                print(f"[WARN] Offset 0x{offset:X} fuori dal file, ignorato.")

    # Applica mod matrix
    if hasattr(preset, "_mod_bytes"):
        OFFSET_MOD_MATRIX = 0x2A0
        fine = OFFSET_MOD_MATRIX + len(preset._mod_bytes)
        if fine <= len(data):
            data[OFFSET_MOD_MATRIX:fine] = preset._mod_bytes
        else:
            print("[WARN] Mod matrix fuori dal file, ignorata.")

    preset._fxp_bytes = data
    return preset
