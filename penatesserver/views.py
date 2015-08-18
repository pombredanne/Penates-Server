# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import os
import tempfile
import subprocess

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

from penatesserver.models import Principal, DhcpRecord
from penatesserver.pki.constants import COMPUTER
from penatesserver.pki.service import CertificateEntry, PKI
from penatesserver.powerdns.models import Domain
from penatesserver.utils import hostname_from_principal, principal_from_hostname, file_sha1

__author__ = 'flanker'


def entry_from_hostname(hostname):
    return CertificateEntry(hostname, organizationName=settings.PENATES_ORGANIZATION, organizationalUnitName=_('Computers'),
                            emailAddress=settings.PENATES_EMAIL_ADDRESS, localityName=settings.PENATES_LOCALITY, countryName=settings.PENATES_COUNTRY,
                            stateOrProvinceName=settings.PENATES_STATE, altNames=[], role=COMPUTER)


def index(request):
    template_values = {}
    return render_to_response('penatesserver/index.html', template_values, RequestContext(request))


def get_info(request):
    content = ''
    content += 'METHOD:%s\n' % request.method
    content += 'REMOTE_USER:%s\n' % ('' if request.user.is_anonymous() else request.user.username)
    content += 'REMOTE_ADDR:%s\n' % request.META.get('HTTP_X_FORWARDED_FOR', '')
    content += 'HTTPS?:%s\n' % request.is_secure()
    return HttpResponse(content, status=200, content_type='text/plain')


def get_host_keytab(request, hostname):
    """Register a computer:

        - create Kerberos principal
        - create private key
        - create public SSH key
        - create x509 certificate
        - create PTR DNS record
        - create A or AAAA DNS record
        - create SSHFP DNS record
        - return keytab

    :param request:
    :type request:
    :param hostname:
    :type hostname:
    :return:
    :rtype:
    """
    short_hostname, sep, domain_name = hostname.partition('.')
    domain_name = settings.PENATES_DOMAIN
    long_hostname = '%s.%s' % (short_hostname, domain_name)
    # valid FQDN
    # create Kerberos principal
    principal = principal_from_hostname(long_hostname, settings.PENATES_REALM)
    if list(Principal.objects.filter(name=principal)[0:1]):
        return HttpResponse('', status=401)
    else:
        Principal(name=principal).save()

    # create private key, public key, public certificate, public SSH key
    entry = entry_from_hostname(long_hostname)
    pki = PKI()
    pki.ensure_certificate(entry)
    ssh_fingerprint = file_sha1(entry.ssh_filename)
    # create DNS records
    domain, created = Domain.objects.get_or_create(defaults=Domain.default_domain_values(), name=domain_name)
    remote_addr = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if remote_addr:
        domain.ensure_record(remote_addr, long_hostname, ssh_sha1_fingerprint=ssh_fingerprint)
        domain.update_soa()

    # create keytab
    with tempfile.NamedTemporaryFile() as fd:
        keytab_filename = fd.name
    p = subprocess.Popen(['kadmin', '-p', settings.PENATES_PRINCIPAL, '-k', '-t', settings.PENATES_KEYTAB, '-q', 'ktadd -k %s %s' % (keytab_filename, principal)], stdout=subprocess.PIPE)
    p.communicate()
    with open(keytab_filename, 'rb') as fd:
        keytab_content = bytes(fd.read())
    os.remove(keytab_filename)

    return HttpResponse(keytab_content, status=200, content_type='application/octet-stream')


def set_dhcp(request, mac_address, ip_address):
    hostname = hostname_from_principal(request.user.username)
    name = mac_address.replace(':', '_')
    if DhcpRecord.objects.filter(name=name).count() > 0:
        return HttpResponse('%s is already registered' % mac_address, status=401)
    DhcpRecord(name=name, hw_address='ethernet %s', options=['fixed-address %s' % ip_address, 'host-name %s' % hostname, ]).save()
    return HttpResponse(status=201)


def get_host_certificate(request):
    entry = entry_from_hostname(hostname_from_principal(request.user.username))
    pki = PKI()
    pki.ensure_certificate(entry)
    content = b''
    with open(entry.key_filename, 'rb') as fd:
        content += fd.read()
    with open(entry.crt_filename, 'rb') as fd:
        content += fd.read()
    with open(entry.ca_filename, 'rb') as fd:
        content += fd.read()
    return HttpResponse(content, status=200)


def get_ssh_pub(request):
    entry = entry_from_hostname(hostname_from_principal(request.user.username))
    pki = PKI()
    pki.ensure_certificate(entry)
    with open(entry.ssh_filename, 'rb') as fd:
        content = fd.read()
    return HttpResponse(content, status=200)


def register_service(request, protocol, alias, port, kerberos_service=None):
    raise NotImplementedError


def get_service_keytab(request, protocol, alias, port, kerberos_service):
    raise NotImplementedError


def get_service_certificate(request, protocol, alias, port, kerberos_service=None):
    raise NotImplementedError
