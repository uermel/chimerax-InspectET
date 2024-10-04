# vim: set expandtab shiftwidth=4 softtabstop=4:

from chimerax.core.toolshed import BundleAPI


class _MyAPI(BundleAPI):

    api_version = 1

    @staticmethod
    def start_tool(session, bi, ti):

        if ti.name == "InspectET":
            from . import tool

            return tool.InspectETTool(session, ti.name)

    @staticmethod
    def register_command(bi, ci, logger):
        logger.status(ci.name)
        # Register all InspectET commands
        if "inspectet" in ci.name:
            from .cmd.cmd import register_inspectet

            register_inspectet(logger)


# Create the ``bundle_api`` object that ChimeraX expects.
bundle_api = _MyAPI()
