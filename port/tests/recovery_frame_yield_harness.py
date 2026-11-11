"""New frame-yield harness using existing global-access/ABI execution checks."""
from recovery_fade_entry_harness import Native as Base,PORT
class Native(Base):
    def __init__(self):
        super().__init__('recovery_gameplay_frame_yield.s')
