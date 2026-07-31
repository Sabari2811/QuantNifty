class OverlayManager:

    def __init__(self):

        self.overlays = []

    def register(self, overlay):

        self.overlays.append(overlay)

    def render(self, fig, ctx):

        for overlay in self.overlays:

            overlay.render(

                fig,

                ctx

            )