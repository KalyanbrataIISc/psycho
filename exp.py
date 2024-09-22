import shift as sft

fl = lambda x: sft.sound_shift(x, 'phase', 'left', 'short')
fr = lambda x: sft.sound_shift(x, 'phase', 'right', 'short')
sl = lambda x: sft.sound_shift(x, 'phase', 'left', 'long')
sr = lambda x: sft.sound_shift(x, 'phase', 'right', 'long')

