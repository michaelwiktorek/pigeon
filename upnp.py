# credit to http://mattscodecave.com/posts/using-python-and-upnp-to-forward-a-port.html

from socket import *
import re
import urllib2
import httplib
from urlparse import urlparse
from xml.dom.minidom import parseString
from xml.dom.minidom import Document
from pigeon_constants import Pigeon_Constants as C

class upnp:
    def __init__(self):
        self.ADD_PORT_MAPPING = 'AddPortMapping'
        self.DELETE_PORT_MAPPING = 'DeletePortMapping'
        
        self.SSDP_ADDR = "239.255.255.250"
        self.SSDP_PORT = 1900
        self.SSDP_MX = 2
        self.SSDP_ST = "urn:schemas-upnp-org:device:InternetGatewayDevice:1"

    # TODO handle case: multiple responses
    def find_device(self):
        ssdp_request = "M-SEARCH * HTTP/1.1\r\n" + \
                       "HOST: %s:%d\r\n" % (self.SSDP_ADDR, self.SSDP_PORT) + \
                       "MAN: \"ssdp:discover\"\r\n" + \
                       "MX: %d\r\n" % (self.SSDP_MX, ) + \
                       "ST: %s\r\n" % (self.SSDP_ST, ) + "\r\n"
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.sendto(ssdp_request, (self.SSDP_ADDR, self.SSDP_PORT))
        resp = sock.recv(1024)
        sock.close()
        return resp

    def get_data_url(self, resp):
        parsed = re.findall(r'(?P<name>.*?): (?P<value>.*?)\r\n', resp)
        location = filter(lambda x: x[0].lower() == "location", parsed)
        url = location[0][1]
        return url

    def parse_data_url(self, url):
        return urlparse(url)

    def get_xml(self, url):
        return urllib2.urlopen(url).read()

    def parse_xml(self, xml):
        dom = parseString(xml)
        service_types = dom.getElementsByTagName('serviceType')
        for service in service_types:
            #print service.childNodes[0].data
            if service.childNodes[0].data.find('WANIPConnection') > 0:
                path = service.parentNode.getElementsByTagName('controlURL')[0].childNodes[0].data
                return path

    #  Construct XML document to request router function
    def create_request_xml(self, function, arguments):
        doc = Document()

        envelope = doc.createElementNS('', 's:Envelope')
        envelope.setAttribute('xmlns:s', 'http://schemas.xmlsoap.org/soap/envelope/')
        envelope.setAttribute('s:encodingStyle', 'http://schemas.xmlsoap.org/soap/encoding')

        body = doc.createElementNS('', 's:Body')

        fn = doc.createElementNS('', 'u:' + function)
        fn.setAttribute('xmlns:u', 'urn:schemas-upnp-org:service:WANIPConnection:1')

        argument_list = []
        for k, v in arguments:
            tmp_node = doc.createElement(k)
            tmp_text_node = doc.createTextNode(v)
            tmp_node.appendChild(tmp_text_node)
            argument_list.append(tmp_node)

        for arg in argument_list:
            fn.appendChild(arg)

        body.appendChild(fn)
        envelope.appendChild(body)
        doc.appendChild(envelope)

        pure_xml = doc.toxml()
        return pure_xml

    #  Send XML request to router
    def send_request(self, request_xml, function):
        conn = httplib.HTTPConnection(self.parsed_url.hostname, self.parsed_url.port)
        conn.request('POST',
                     self.request_path,
                     request_xml,
                     {'SOAPAction': '"urn:schemas-upnp-org:service:WANIPConnection:1#' + function + '"',
                      'Content-Type': 'text/xml'}
                     )
        resp = conn.getresponse()
        return resp

    #  Add port mapping
    def router_forward_port(self, ext_port, int_port, ip, protocol):
        arguments = [
            ('NewExternalPort', str(ext_port)),
            ('NewProtocol', protocol),
            ('NewInternalPort', str(int_port)),
            ('NewInternalClient', ip),
            ('NewEnabled', '1'),
            ('NewRemoteHost', ip),   
            ('NewPortMappingDescription', 'Test Description'),
            ('NewLeaseDuration', '0')]
        
        request_xml = self.create_request_xml(self.ADD_PORT_MAPPING, arguments)
        resp = self.send_request(request_xml, self.ADD_PORT_MAPPING)
        return resp

    #  Remove port mapping
    def router_delete_port(self, ext_port, int_port, ip, protocol):
        arguments = [
            ('NewRemoteHost', ip),
            ('NewExternalPort', str(ext_port)),
            ('NewInternalPort', str(int_port)),
            ('NewProtocol', protocol)]
        
        request_xml = self.create_request_xml(self.DELETE_PORT_MAPPING, arguments)
        resp = self.send_request(request_xml, self.DELETE_PORT_MAPPING)
        return resp

    #  Establish UPnP device data 
    def establish_upnp_data(self):
        resp = self.find_device()
        self.url = self.get_data_url(resp)
        self.parsed_url = self.parse_data_url(self.url)
        xml = self.get_xml(self.url)
        self.request_path = self.parse_xml(xml)

    #  print router response
    def print_response(self, resp):
        print resp.status
        print resp.read()
        

if __name__ == "__main__":
    local_ip = gethostbyname(gethostname())
    
    foo = upnp()
    foo.establish_upnp_data()

    resp = foo.router_forward_port(9999, 9999, local_ip, 'TCP')
    foo.print_response(resp)
    resp = foo.router_delete_port(9999, 9999, local_ip, 'TCP')
    foo.print_response(resp)
