# mostly adapted from a nice tutorial located at
# http://mattscodecave.com/posts/using-python-and-upnp-to-forward-a-port.html

import re
import urllib2
import httplib
from socket          import *
from urlparse        import urlparse
from xml.dom.minidom import parseString
from xml.dom.minidom import Document

class upnp:
    def __init__(self):
        self.ADD_PORT_MAPPING = 'AddPortMapping'
        self.DELETE_PORT_MAPPING = 'DeletePortMapping'
        
        self.SSDP_ADDR = "239.255.255.250"
        self.SSDP_PORT = 1900
        self.SSDP_MX = 2
        self.SSDP_ST = "urn:schemas-upnp-org:device:InternetGatewayDevice:1"

        self.MAX_ATTEMPTS = 2
        self.TIMEOUT = 1

    # TODO handle case: multiple responses
    def find_device(self):
        ssdp_request = "M-SEARCH * HTTP/1.1\r\n" + \
                       "HOST: %s:%d\r\n" % (self.SSDP_ADDR, self.SSDP_PORT) + \
                       "MAN: \"ssdp:discover\"\r\n" + \
                       "MX: %d\r\n" % (self.SSDP_MX, ) + \
                       "ST: %s\r\n" % (self.SSDP_ST, ) + "\r\n"
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.sendto(ssdp_request, (self.SSDP_ADDR, self.SSDP_PORT))
        sock.settimeout(self.TIMEOUT)
        attempts = 0
        resp = False
        while attempts < self.MAX_ATTEMPTS:
            try:
                resp = sock.recv(1024)
                break
            except:
                attempts += 1
                continue
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
            ('NewRemoteHost', ""),   
            ('NewPortMappingDescription', 'Pigeon Port Mapping'),
            ('NewLeaseDuration', '0')]
        
        request_xml = self.create_request_xml(self.ADD_PORT_MAPPING, arguments)
        resp = self.send_request(request_xml, self.ADD_PORT_MAPPING)
        return resp

    #  Remove port mapping
    def router_delete_port(self, ext_port, int_port, ip, protocol):
        arguments = [
            ('NewRemoteHost', ""),
            ('NewExternalPort', str(ext_port)),
            ('NewInternalPort', str(int_port)),
            ('NewProtocol', protocol)]
        
        request_xml = self.create_request_xml(self.DELETE_PORT_MAPPING, arguments)
        resp = self.send_request(request_xml, self.DELETE_PORT_MAPPING)
        return resp

    #  Establish UPnP device data
    #  returns: True if we found a router
    #           False if the router never responded
    def establish_upnp_data(self):
        resp = self.find_device()
        if not resp:
            return False
        self.url = self.get_data_url(resp)
        self.parsed_url = self.parse_data_url(self.url)
        xml = self.get_xml(self.url)
        #print xml
        self.request_path = self.parse_xml(xml)
        return True

    #  print router response
    def print_response(self, resp):
        print resp.status
        print resp.read()

    def udp_tunnel(self, port, ip):
        return self.router_forward_port(port, port, ip, 'UDP')

    def tcp_tunnel(self, port, ip):
        return self.router_forward_port(port, port, ip, 'TCP')

    def udp_end_tunnel(self, port, ip):
        return self.router_delete_port(port, port, ip, 'UDP')

    def tcp_end_tunnel(self, port, ip):
        return self.router_delete_port(port, port, ip, 'TCP')
        

if __name__ == "__main__":
    # some quick test junk
    local_ip = gethostbyname(gethostname())
    
    foo = upnp()
    if not foo.establish_upnp_data():
        print "No response from router. Is UPnP enabled?"
    else:
        print "router said hello"
        #resp = foo.router_forward_port(9999, 9999, local_ip, 'TCP')
        #foo.print_response(resp)
        #resp = foo.router_delete_port(9999, 9999, local_ip, 'TCP')
        #foo.print_response(resp)
