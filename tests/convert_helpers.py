from xml.etree import ElementTree as ET


class FakeConsole:
    def __init__(self):
        self.messages = []

    def print(self, *args, **_):
        # simple join for ease of assertions
        self.messages.append(" ".join(str(a) for a in args))


def make_fodt(body: str) -> ET.ElementTree:
    xml = (
        """\
<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:loext="urn:org:documentfoundation:names:experimental:office:xmlns:loext:1.0" xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0">
 <office:automatic-styles>
  <style:style style:name="T11" style:family="text">
   <style:text-properties fo:color="#0070c0" loext:opacity="100%" fo:font-family="Calibri" style:font-family-generic="swiss" style:font-pitch="variable" fo:font-size="10.5pt" fo:font-weight="bold" style:font-family-asian="MercuryTextG1-Roman" style:font-family-generic-asian="system" style:font-pitch-asian="variable" style:font-size-asian="10.5pt" style:font-weight-asian="bold" style:font-family-complex="MercuryTextG1-Roman" style:font-family-generic-complex="system" style:font-pitch-complex="variable" style:font-size-complex="10.5pt"/>
  </style:style>
 </office:automatic-styles>
 <office:body>
  <office:text text:use-soft-page-breaks="true">
"""
        + body
        + """
  </office:text>
 </office:body>
</office:document>
"""
    )
    return ET.ElementTree(ET.fromstring(xml))


def make_html(body: str) -> ET.ElementTree:
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        """
    <html xmlns="http://www.w3.org/1999/xhtml">
      <head><style>
          .text-T13{ color:#0070c0; font-size:10.5pt; font-weight:bold; }
      </style></head>
      <body>
    """
        + body
        + """
      </body>
    </html>
    """
    )
    return ET.ElementTree(ET.fromstring(xml))
