from django.http.multipartparser import MultiPartParser
from io import StringIO, BytesIO


def parse_multipart_data(request):

    body = None
    if isinstance(request.body, (bytes, bytearray)):
        body = BytesIO(request.body)
    elif isinstance(request.body, (bytes, bytearray)):
        body = StringIO(request.body)

    if body:
        return MultiPartParser(
            META=request.META,
            input_data=body,
            upload_handlers=request.upload_handlers,
            encoding=request.encoding
        ).parse()
    else:
        return None
