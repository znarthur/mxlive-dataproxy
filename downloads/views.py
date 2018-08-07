from models import SecurePath
from django.conf import settings
from django import http
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.static import serve
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import os
import posixpath
import re
import subprocess
import urllib
from django.http import StreamingHttpResponse

CACHE_DIR = getattr(settings, 'DOWNLOAD_CACHE_DIR', '/tmp')
FRONTEND = getattr(settings, 'DOWNLOAD_FRONTEND', 'xsendfile')
USER_ROOT = getattr(settings, 'LDAP_USER_ROOT', '/users')
ARCHIVE_ROOT = getattr(settings, 'ARCHIVE_ROOT', '/archive')
ROOT_RE = re.compile('^{}'.format(USER_ROOT))


def create_cache_dir(key):
    dir_name = os.path.join(CACHE_DIR, key)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    return dir_name


@method_decorator(csrf_exempt, name='dispatch')
class CreatePath(View):

    def post(self, request, *args, **kwargs):
        path = request.POST.get('path')
        obj = SecurePath()
        obj.path = re.sub(ROOT_RE, "/users", path)
        obj.save()
        return JsonResponse({'key': obj.key})


def get_download_path(key):
    """Convenience method to return a path for a key"""

    obj = SecurePath.objects.get(key=key)
    return obj.path


def send_uncompressed_file(request, obj, full_path):
    create_cache_dir(obj.key)
    _, zfile = os.path.split(full_path)
    cached_file = os.path.join(CACHE_DIR, obj.key, zfile.strip('.gz'))
    cmd = 'gunzip {0} {1}'.format(full_path, cached_file)
    try:
        subprocess.check_call(cmd.split())
    except:
        return http.HttpResponseNotFound()
    return send_raw_file(request, cached_file)


def send_raw_file(request, full_path, attachment=False):
    """Send a file using mod_xsendfile or similar functionality.
    Use django's static serve option for development servers"""

    if not os.path.exists(full_path):
        print(full_path)
        full_path = '{}{}'.format(ARCHIVE_ROOT, full_path)

    if not os.path.exists(full_path):
        print(full_path)
        raise Http404

    if FRONTEND == "xsendfile":
        response = HttpResponse()
        response['X-Sendfile'] = full_path
        if attachment:
            response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(full_path)
        # Unset the Content-Type as to allow for the webserver
        # to determine it.
        response['Content-Type'] = ''

    elif FRONTEND == "xaccelredirect":
        response = HttpResponse()
        response['X-Accel-Redirect'] = full_path
        if attachment:
            response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(full_path)
        response['Content-Type'] = ''
        #response = HttpResponse()
    else:
        dirname = os.path.dirname(full_path)
        path = os.path.basename(full_path)
        # "Serving file %s in directory %s through django static serve." % (path, dirname)
        response = serve(request, path, dirname)

    return response


def find_file(request, key, path):
    obj = get_object_or_404(SecurePath, key=key)

    if os.path.exists(get_download_path(obj.key)):
        filename = os.path.join(CACHE_DIR, obj.key, '%s.gif' % path)
        if os.path.exists(filename):
            return send_raw_file(request, filename, attachment=False)

        pngs = []
        for f in os.listdir(get_download_path(obj.key)):
            if f.endswith('.png') and f.startswith(path):
                pngs.append(os.path.join(get_download_path(obj.key), f))
        if len(pngs) == 1:
            return send_raw_file(request, pngs[0], attachment=False)

        create_cache_dir(obj.key)
        command = 'convert -delay 200 -resize 500x {0} {1}'.format(' '.join(pngs), filename)
        try:
            subprocess.check_call(command.split())
        except:
            try:
                subprocess.check_call(command.replace('_test-pic', '-pic').split())
            except:
                return http.HttpResponseNotFound()
        return send_raw_file(request, filename, attachment=False)

    return http.HttpResponseNotFound()


def send_file(request, key, path):
    obj = get_object_or_404(SecurePath, key=key)
    document_root = obj.path
    # Clean up given path to only allow serving files below document_root.
    path = posixpath.normpath(urllib.unquote(path))
    path = path.lstrip('/')
    newpath = ''
    for part in path.split('/'):
        if not part:
            # Strip empty path components.
            continue
        drive, part = os.path.splitdrive(part)
        head, part = os.path.split(part)
        if part in (os.curdir, os.pardir):
            # Strip '.' and '..' in path.
            continue
        newpath = os.path.join(newpath, part).replace('\\', '/')
    if newpath and path != newpath:
        return send_raw_file(request, newpath)
    full_path = os.path.join(document_root, newpath)
    if not os.path.exists(full_path) and os.path.exists("{}.gz".format(full_path)):
        return send_uncompressed_file(request, obj, full_path)
    return send_raw_file(request, full_path)


def send_archive(request, path, key=None):  # Add base parameter and another url
    if key:
        obj = get_object_or_404(SecurePath, key=key)
        archive_dir = obj.path
    else:
        paths = SecurePath.objects.filter(key__in=request.GET.getlist('urls[]')).values_list('path',flat=True)
        archive_dir = os.path.commonprefix(paths)
        archive_dir = archive_dir if archive_dir[-1] == '/' else '/'.join(archive_dir.split('/')[:-1])
        if len([a for a in archive_dir.split(os.sep) if a]) < 3:
            raise http.HttpResponseForbidden

    normpath = os.path.normpath(archive_dir)

    if os.path.exists(archive_dir):
        p = subprocess.Popen(
            ['tar', '-czf', '-', os.path.basename(normpath)],
            cwd=os.path.dirname(normpath),
            stdout=subprocess.PIPE
        )

        response = StreamingHttpResponse(p.stdout, content_type='application/x-gzip')
        response['Content-Disposition'] = 'attachment; filename={0}.tar.gz'.format(path)

        return response
    else:
        raise Http404

