import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.input_schema import PresetInput
from core.validator import valida_input
from core.wavetable import risolvi_wavetable
from core.modulation import codifica_modulazioni, codifica_parametri
from core.encoder import assembla_fxp
from output_io.writer import scrivi_output

PIPELINE = [
    valida_input,
    risolvi_wavetable,
    codifica_modulazioni,
    codifica_parametri,
    assembla_fxp,
    scrivi_output,
]

def esegui_pipeline(preset: PresetInput) -> PresetInput:
    print(f"\n▶ Avvio pipeline per preset: '{preset.nome}'")
    print(f"  Stadi totali: {len(PIPELINE)}\n")
    for i, stadio in enumerate(PIPELINE, 1):
        nome_stadio = stadio.__name__
        try:
            print(f"  [{i}/{len(PIPELINE)}] {nome_stadio}...")
            preset = stadio(preset)
            print(f"         ✓ completato")
        except Exception as e:
            print(f"         ✗ ERRORE in {nome_stadio}:\n           {e}")
            raise
    print(f"\n✅ Pipeline completata.\n")
    return preset
