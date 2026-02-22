# Indici delle destinazioni di modulazione in Serum
# Nota: verificare con hex editor sulla propria versione di Serum

DESTINAZIONI: dict[str, int] = {
    "OSC_A_PITCH":      0,
    "OSC_A_PAN":        1,
    "OSC_A_LEVEL":      2,
    "OSC_A_WAVETABLE":  3,
    "OSC_B_PITCH":      4,
    "OSC_B_PAN":        5,
    "OSC_B_LEVEL":      6,
    "OSC_B_WAVETABLE":  7,
    "NOISE_LEVEL":      8,
    "FILTER_CUTOFF":    17,
    "FILTER_RES":       18,
    "FILTER_DRIVE":     19,
    "LFO1_RATE":        30,
    "LFO2_RATE":        31,
    "LFO3_RATE":        32,
    "LFO4_RATE":        33,
    "ENV1_ATTACK":      40,
    "ENV1_DECAY":       41,
    "ENV1_SUSTAIN":     42,
    "ENV1_RELEASE":     43,
    "MASTER_VOL":       51,
    "MASTER_PAN":       52,
}
