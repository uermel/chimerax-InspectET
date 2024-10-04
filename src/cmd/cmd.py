# vim: set expandtab shiftwidth=4 softtabstop=4:

from ..core.alignment import apply_alignment


def play(session, framesPerView: int = 10, loopNumber: int = 1):
    """Playback a tomographic alignment."""
    if not session.ui.is_gui:
        session.logger.warning("InspectET requires Chimerax GUI.")

    if session.inspectet is None or session.inspectet.current_alignment is None:
        session.logger.warning("No tomographic alignment loaded.")
        return

    ali = session.inspectet.current_alignment
    psaps = session.inspectet.current_alignment.per_section_alignment_parameters

    if loopNumber < 1:
        session.logger.warning("Loop number must be greater than 0.")
        return

    num_views = len(psaps)

    for loop in range(loopNumber):
        for i in range(num_views):
            if loop % 2 == 0:
                idx = i
            else:
                idx = -i

            psap = psaps[idx]
            apply_alignment(session, ali, psap)

            for f in range(framesPerView):
                session.update_loop.draw_new_frame()


def register_inspectet(logger):
    """Register all commands with ChimeraX, and specify expected arguments."""
    from chimerax.core.commands import CmdDesc, IntArg, register

    def register_inspectet_play():
        desc = CmdDesc(
            optional=[("framesPerView", IntArg), ("loopNumber", IntArg)],
            synopsis="Playback the tomographic alignment.",
        )
        register("inspectet play", desc, play)

    register_inspectet_play()
