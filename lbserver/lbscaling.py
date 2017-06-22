import pika, requests
#from optparse import OptionParser
#import ConfigParser
#http://docs.python-requests.org/en/master/user/quickstart/
#https://stackoverflow.com/questions/25491090/how-to-use-python-to-execute-a-curl-command
#https://curl.trillworks.com/

iptab = {'170.16.0.9':'0','170.16.0.13':'1'} #initial entries same as those checkin in nginx config file
url = 'http://localhost/upstream_conf'



def callback(ch, method, properties, body):
    flag = body[0] #body is the message received, which is in the format of '1xxx.xxx.xxx.xxx'
    address = body[1:] #first digit in the body is flag bit, flag=0, invoke removeip, flag=1, invoke addip
    print("%s" % address)
    if flag == '0':
        removeip(address)
    if flag == '1':
        addip(address)


def addip(address):
    payload = {'upstream':'webserver','add':'','server':address}
    r = requests.get(url,params=payload)
    idnum = r.content[len(r.content)-2] # get the id# for the added ip
    newipid = {address:idnum}
    iptab.update(newipid)
    print("%s" % iptab)

def removeip(address):
    idnum = iptab.get(address) #get the id# for the removed ip
    payload = {'upstream':'webserver','remove':'','id':idnum}
    r = request.get(url,params=payload)
    del iptab[address] #remove the entry from the iptab




if __name__ == "__main__":
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='lb_queue')
    channel.basic_consume(callback,queue='lb_queue',no_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()





