from dataclasses import dataclass


@dataclass(frozen=True)
class HTMLPage:
    """
    Todo - add help
    """

    title: str
    body: str

    def render(self) -> str:
        return f"""<!DOCTYPE html>
                   <html>
                   <head>
                   <title>{self.title}</title>
                   </head>
                   <body>
                   {self.body}
                   </body>
                   </html>"""


class HTMLBuilder:
    """
    A class to dynamically construct a HTML document.
    """

    def __init__(self, title: str):
        """
        Constructor for the HTMLBuilder class
        """

        self.title = title
        self.body_content = []

    def add_heading(self, text: str, level: int = 1) -> None:
        self.body_content.append(f"<h{level}>{text}</h{level}>")

    def add_paragraph(self, text: str) -> None:
        self.body_content.append(f"<p>{text}</p>")

    def render(self) -> str:
        body = "\n".join(self.body_content)
        return HTMLPage(title=self.title, body=body).render()


if __name__ == "__main__":
    builder = HTMLBuilder("Sample Page")
    builder.add_heading("Welcome to My Page", level=1)
    builder.add_paragraph("This is a sample paragraph.")
    builder.add_heading("Subheading", level=2)
    builder.add_paragraph("Another paragraph under the subheading.")

    html_content = builder.render()

    print(html_content)  # Output the rendered HTML content
