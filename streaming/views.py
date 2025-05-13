import os
import mimetypes
from django.views import View
from django.http import FileResponse, HttpResponse, HttpResponseNotModified
from django.utils.http import http_date, parse_http_date_safe
from django.conf import settings

class VideoStreamView(View):
    """Efficient byte-range streaming with production optimizations"""
    
    def get(self, request, filename):
        # Validate and sanitize filename
        safe_path = os.path.join(settings.MEDIA_ROOT, 'videos', os.path.basename(filename))
        
        if not os.path.isfile(safe_path):
            return HttpResponse("File not found", status=404)

        # Get file stats and handle caching
        stat = os.stat(safe_path)
        content_type, _ = mimetypes.guess_type(safe_path)
        
        # Handle 'If-Modified-Since' header
        if 'HTTP_IF_MODIFIED_SINCE' in request.META:
            if_modified_since = request.META['HTTP_IF_MODIFIED_SINCE']
            since_ts = parse_http_date_safe(if_modified_since)
            if since_ts is not None and since_ts >= int(stat.st_mtime):
                return HttpResponseNotModified()

        # Use FileResponse for efficient streaming
        file = open(safe_path, 'rb')
        response = FileResponse(file, content_type=content_type)
        
        # Set essential headers
        response['Content-Length'] = stat.st_size
        response['Accept-Ranges'] = 'bytes'
        response['Last-Modified'] = http_date(stat.st_mtime)
        
        # Handle byte ranges (crucial for seeking)
        range_header = request.headers.get('Range') or request.META.get('HTTP_RANGE')
        if range_header:
            return self.handle_byte_range(file, response, range_header, stat.st_size)
            
        return response

    def handle_byte_range(self, file, response, range_header, file_size):
        """Process Range header according to RFC 7233"""
        try:
            unit, ranges = range_header.strip().split('=')
            if unit != 'bytes':
                return HttpResponse("Invalid range unit", status=400)
            
            start, end = ranges.split('-')
            start = int(start) if start else 0
            end = int(end) if end else file_size - 1

            if start >= file_size or end >= file_size or start > end:
                return HttpResponse("Range not satisfiable", status=416)

            content_length = end - start + 1
            file.seek(start)
            # Return a streaming response for the range
            class RangeFileWrapper:
                def __init__(self, file, length):
                    self.file = file
                    self.remaining = length
                def __iter__(self):
                    return self
                def __next__(self):
                    if self.remaining <= 0:
                        raise StopIteration
                    chunk = self.file.read(min(8192, self.remaining))
                    if not chunk:
                        raise StopIteration
                    self.remaining -= len(chunk)
                    return chunk
            response = FileResponse(RangeFileWrapper(file, content_length),
                                    status=206,
                                    content_type=response['Content-Type'])
            response['Content-Length'] = str(content_length)
            response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
            response['Accept-Ranges'] = 'bytes'
            response['Last-Modified'] = response.get('Last-Modified')
            return response
                
        except Exception as e:
            return HttpResponse(f"Range processing error: {str(e)}", status=400)