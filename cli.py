"""
Serum Builder — CLI
═══════════════════════════════════════════════════════
Utilizzo base:
    python cli.py --nome MioPreset --base base.fxp --funzione "sin(x)"

Wavetable da funzione:
    python cli.py --nome Test --base base.fxp \
        --funzione "sin(x) + sin(3*x)/3" --frame 16

Wavetable da file .wav:
    python cli.py --nome Test --base base.fxp --wav mia_wavetable.wav

Con modulazioni e parametri:
    python cli.py --nome Test --base base.fxp \
        --funzione "sin(x)" \
        --mod "LFO1,FILTER_CUTOFF,0.8" \
        --mod "ENV2,OSC_A_PITCH,0.3" \
        --param "filter_cutoff,0.4" \
        --env "ENV1,0.01,0.2,0.6,0.5" \
        --output "./miei_preset"

Lista sorgenti disponibili:
    python cli.py --lista-sorgenti

Lista destinazioni disponibili:
    python cli.py --lista-destinazioni
═══════════════════════════════════════════════════════
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import argparse
import numpy as np

from models.input_schema import (
    PresetInput, WavetableInput,
    ModulazioneInput, ParametroInput, EnvelopeInput
)
from maps.sources import SORGENTI
from maps.destinations import DESTINAZIONI
from core.pipeline import esegui_pipeline


# ═══════════════════════════════════════════════════════
# PARSER
# ═══════════════════════════════════════════════════════

def crea_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="serum-builder",
        description="Genera preset .fxp di Serum da riga di comando.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="Esempio completo:\n"
               "  python cli.py --nome Pad --base base.fxp \\\n"
               "    --funzione \"sin(x) + sin(3*x)/3\" --frame 16 \\\n"
               "    --mod \"LFO1,FILTER_CUTOFF,0.8\" \\\n"
               "    --param \"filter_cutoff,0.4\" \\\n"
               "    --env \"ENV1,0.01,0.2,0.6,0.5\" \\\n"
               "    --output ./output"
    )

    # ── Obbligatori ──────────────────────────────────
    obbligatori = parser.add_argument_group("Obbligatori")
    obbligatori.add_argument(
        "--nome", required=True,
        metavar="NOME",
        help="Nome del preset (usato per il nome del file output)"
    )
    obbligatori.add_argument(
        "--base", required=True,
        metavar="PATH",
        help="Path al file .fxp base di partenza"
    )

    # ── Wavetable ─────────────────────────────────────
    wt = parser.add_argument_group("Wavetable (scegli uno)")
    wt_group = wt.add_mutually_exclusive_group()
    wt_group.add_argument(
        "--funzione",
        metavar="EXPR",
        help=(
            "Espressione matematica come stringa\n"
            "  Variabile:  x  (da 0 a 2π per ogni frame)\n"
            "  Funzioni:   sin, cos, tan, sqrt, abs, log, exp\n"
            "  Costanti:   pi, e\n"
            "  Esempio:    \"sin(x) + sin(3*x)/3 + sin(5*x)/5\""
        )
    )
    wt_group.add_argument(
        "--wav",
        metavar="PATH",
        help="Path a un file .wav esistente da usare come wavetable"
    )
    parser.add_argument(
        "--frame", type=int, default=8,
        metavar="N",
        help="Numero di frame della wavetable (default: 8)\n"
             "Usato solo con --funzione. Range consigliato: 1–256"
    )

    # ── Modulazioni ───────────────────────────────────
    mod = parser.add_argument_group("Modulazioni")
    mod.add_argument(
        "--mod",
        action="append",
        metavar="SRC,DST,QTY",
        help=(
            "Collegamento sorgente → destinazione\n"
            "  Formato:   SORGENTE,DESTINAZIONE,QUANTITA\n"
            "  Quantità:  da -1.0 (inverso) a 1.0 (massimo)\n"
            "  Esempio:   --mod \"LFO1,FILTER_CUTOFF,0.8\"\n"
            "  Ripetibile più volte (max 32 slot)\n"
            "  Usa --lista-sorgenti e --lista-destinazioni per i nomi"
        )
    )

    # ── Parametri statici ─────────────────────────────
    par = parser.add_argument_group("Parametri statici")
    par.add_argument(
        "--param",
        action="append",
        metavar="NOME,VALORE",
        help=(
            "Parametro statico di Serum\n"
            "  Formato:  NOME,VALORE (valore tra 0.0 e 1.0)\n"
            "  Esempio:  --param \"filter_cutoff,0.4\"\n"
            "  Nomi disponibili: filter_cutoff, filter_res, filter_drive,\n"
            "                    master_vol, master_pan"
        )
    )

    # ── Envelopes ─────────────────────────────────────
    env = parser.add_argument_group("Envelopes ADSR")
    env.add_argument(
        "--env",
        action="append",
        metavar="TARGET,A,D,S,R",
        help=(
            "Envelope ADSR\n"
            "  Formato:  TARGET,ATTACK,DECAY,SUSTAIN,RELEASE\n"
            "  Target:   ENV1, ENV2, ENV3\n"
            "  A/D/R:    secondi  |  S: livello 0.0–1.0\n"
            "  Esempio:  --env \"ENV1,0.01,0.2,0.6,0.5\""
        )
    )

    # ── Output ────────────────────────────────────────
    out = parser.add_argument_group("Output")
    out.add_argument(
        "--output",
        metavar="DIR",
        default="./output",
        help="Cartella di destinazione dei file generati (default: ./output)"
    )

    # ── Utility ───────────────────────────────────────
    util = parser.add_argument_group("Utility")
    util.add_argument(
        "--lista-sorgenti",
        action="store_true",
        help="Mostra tutte le sorgenti di modulazione disponibili ed esci"
    )
    util.add_argument(
        "--lista-destinazioni",
        action="store_true",
        help="Mostra tutte le destinazioni di modulazione disponibili ed esci"
    )

    return parser


# ═══════════════════════════════════════════════════════
# UTILITY — liste
# ═══════════════════════════════════════════════════════

def stampa_sorgenti():
    print("\nSorgenti di modulazione disponibili:")
    print("─" * 35)
    for nome, idx in SORGENTI.items():
        print(f"  {nome:<15} (indice {idx})")
    print()


def stampa_destinazioni():
    print("\nDestinazioni di modulazione disponibili:")
    print("─" * 40)
    for nome, idx in DESTINAZIONI.items():
        print(f"  {nome:<20} (indice {idx})")
    print()


# ═══════════════════════════════════════════════════════
# PARSING ARGOMENTI → OGGETTI
# ═══════════════════════════════════════════════════════

def parse_funzione(expr: str):
    """Converte una stringa matematica in una funzione Python/numpy."""
    contesto = {
        "sin": np.sin,  "cos": np.cos,  "tan": np.tan,
        "sqrt": np.sqrt, "abs": np.abs,
        "log": np.log,  "exp": np.exp,
        "pi": np.pi,    "e": np.e,
    }
    try:
        x_test = np.linspace(0, 2 * np.pi, 16)
        eval(expr, {"__builtins__": {}}, {"x": x_test, **contesto})
    except Exception as err:
        raise ValueError(f"Funzione non valida '{expr}': {err}")

    return lambda x: eval(expr, {"__builtins__": {}}, {"x": x, **contesto})


def parse_mod(raw: str) -> ModulazioneInput:
    parti = [p.strip() for p in raw.split(",")]
    if len(parti) != 3:
        raise ValueError(f"--mod '{raw}': formato atteso SRC,DST,QTY  (es. LFO1,FILTER_CUTOFF,0.8)")
    src, dst, qty_str = parti
    try:
        qty = float(qty_str)
    except ValueError:
        raise ValueError(f"--mod '{raw}': quantità '{qty_str}' non è un numero valido")
    return ModulazioneInput(sorgente=src, destinazione=dst, quantita=qty)


def parse_param(raw: str) -> ParametroInput:
    parti = [p.strip() for p in raw.split(",")]
    if len(parti) != 2:
        raise ValueError(f"--param '{raw}': formato atteso NOME,VALORE  (es. filter_cutoff,0.4)")
    nome, val_str = parti
    try:
        valore = float(val_str)
    except ValueError:
        raise ValueError(f"--param '{raw}': valore '{val_str}' non è un numero valido")
    return ParametroInput(nome=nome, valore=valore)


def parse_env(raw: str) -> EnvelopeInput:
    parti = [p.strip() for p in raw.split(",")]
    if len(parti) != 5:
        raise ValueError(f"--env '{raw}': formato atteso TARGET,A,D,S,R  (es. ENV1,0.01,0.2,0.6,0.5)")
    target, a, d, s, r = parti
    try:
        return EnvelopeInput(
            attack=float(a), decay=float(d),
            sustain=float(s), release=float(r),
            target=target
        )
    except ValueError as err:
        raise ValueError(f"--env '{raw}': {err}")


# ═══════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════

def main():
    parser = crea_parser()
    args = parser.parse_args()

    # Comandi utility — escono subito
    if args.lista_sorgenti:
        stampa_sorgenti()
        sys.exit(0)
    if args.lista_destinazioni:
        stampa_destinazioni()
        sys.exit(0)

    errori = []

    # Wavetable
    wavetable = None
    if args.funzione:
        try:
            fn = parse_funzione(args.funzione)
            wavetable = WavetableInput(funzione=fn, n_frame=args.frame)
        except ValueError as e:
            errori.append(str(e))
    elif args.wav:
        wavetable = WavetableInput(file_wav=args.wav)

    # Modulazioni
    modulazioni = []
    for raw in (args.mod or []):
        try:
            modulazioni.append(parse_mod(raw))
        except ValueError as e:
            errori.append(str(e))

    # Parametri
    parametri = []
    for raw in (args.param or []):
        try:
            parametri.append(parse_param(raw))
        except ValueError as e:
            errori.append(str(e))

    # Envelopes
    envelopes = []
    for raw in (args.env or []):
        try:
            envelopes.append(parse_env(raw))
        except ValueError as e:
            errori.append(str(e))

    # Mostra tutti gli errori insieme
    if errori:
        print(f"\n✗ {len(errori)} errore/i negli argomenti:")
        for e in errori:
            print(f"  - {e}")
        print("\nUsa --help per vedere il formato corretto.")
        sys.exit(1)

    # Imposta cartella output
    os.makedirs(args.output, exist_ok=True)

    # Costruisce PresetInput e avvia pipeline
    preset = PresetInput(
        nome=args.nome,
        base_fxp=args.base,
        wavetable=wavetable,
        modulazioni=modulazioni,
        parametri=parametri,
        envelopes=envelopes,
    )

    preset._output_dir = args.output

    try:
        esegui_pipeline(preset)
    except Exception as e:
        print(f"\n✗ Pipeline fallita: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
