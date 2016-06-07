#!venv/bin/python

from flask import Flask, render_template, redirect, url_for
from datetime import datetime
import os, time
import subprocess, signal
app = Flask(__name__)

recordPid = 0
recordfile = ""

def getChannelName(channelnum):
    channelName=""
    if (channelnum == "04"):
        channelName="CBS"
    if (channelnum == "07"):
        channelName="ABC"
    if (channelnum == "09"):
        channelName="NBC"
    if (channelnum == "31"):
        channelName="FOX"
    if (channelnum == "59"):
        channelName="ION"
    return channelName

@app.route('/')
def hello_world():
	return 'Hello World!'

def getDirContent( path ): 
    print "getDirContent"
    retval = []
    for path,dirs,files in os.walk( path ):
        for fn in files:
            curline = os.path.join(path,fn)
            curline = fn + "   " + time.ctime(os.path.getmtime(curline))
            print "adding:" + curline
            retval.append(curline)
    return retval

def getRecordings( path ): 
    print "getDirContent"
    retval = []
    for x in sorted([(fn, os.stat(path + fn)) for fn in os.listdir(path)], key = lambda x: x[1].st_ctime, reverse=True):
        print "processing: " + x[0]
        if (os.path.splitext(x[0])[1] == ".mp4"):
            retval.append({"name":x[0], "size":str(x[1].st_size >> 20) + "M"})
    return retval

@app.route('/recordstart/<channelnum>', methods=['GET'])
def record_start(channelnum):
    global recordfile, recordPid
    recordfile = "/mnt/records/" + channelnum + "-" + str(datetime.now()).replace(' ','-').replace(':','_')[:-7]
    print ("######################\nFilename: " + recordfile + "\n#########################")
    recordstr = "ffmpeg -re -i http://50.207.206.171/tv/hls/ch" + channelnum + "/ch" + channelnum +".m3u8"
    recordstr += " -c:v copy -c:a copy -t 6000 " 
    recordstr += recordfile + ".ts"
    print ("Recording:" + recordstr)
    p = subprocess.Popen(recordstr + ' &' , shell=True, stdout=subprocess.PIPE)
    p.stdout.close()
    p.wait()
    # increment for shell=True
    recordPid = p.pid + 1
    return render_template('recording.html', ch=channelnum, name=getChannelName(channelnum), volume=0.1)
    #return redirect(url_for('tv', channelnum=channelnum))
    #return True

@app.route('/recordstop/<channelnum>', methods=['GET'])
def record_stop(channelnum):
    global recordfile, recordPid
    if (recordPid == 0 or recordfile == ""):
        print ("recordPid:" + str(recordPid) + ", recordfile: " + recordfile + "::Undefined variable")
        pass
    else:
        print ("PID: " + str(recordPid))
        os.kill(recordPid, signal.SIGINT)
        convertstr = "ffmpeg -i " + recordfile + ".ts -c:v copy -c:a copy -bsf:a aac_adtstoasc " + recordfile + ".mp4"
        print ("################\nConverting...\n###############")
        convertarray = convertstr.split()
        subprocess.call(convertarray)
        #subprocess.Popen(convertstr, shell=True)
        print ("################\nConversion finished...\n###############")
        #subprocess.call(['rm', '-f', recordfile + '.ts'])
        #subprocess.call(['cp', recordfile + '.mp4', '/mnt/records/'])
    return redirect(url_for('tv', channelnum=channelnum))

@app.route('/recordlist/')
def listRecordings():
    recs = getRecordings("/mnt/records/")
    return render_template('recordings.html', listrecs=recs)

@app.route('/playrecording/<recordingname>')
def play_recording(recordingname):
    return render_template('recordingcontent.html', recordingname=recordingname)

@app.route('/hlscontent/')
def listDirs():
	listCH04 = getDirContent("/mnt/hls/ch04/")
	listCH07 = getDirContent("/mnt/hls/ch07/")
	listCH09 = getDirContent("/mnt/hls/ch09/")
	listCH31 = getDirContent("/mnt/hls/ch31/")
	listCH59 = getDirContent("/mnt/hls/ch59/")
	return render_template('hlscontent.html', CH04=listCH04, CH07=listCH07, CH09=listCH09, CH31=listCH31, CH59=listCH59)

@app.route('/ch04/')
def walk_dir():
	return retval

@app.route('/test/')
@app.route('/test/<name>')
def test(name=None):
	return render_template('testtemplate.html', name=name)

@app.route('/tv/<channelnum>')
def tv(channelnum=None):
    channelName=""
    volume=0.1
    if (channelnum == "04"):
        channelName="CBS"
    if (channelnum == "07"):
        channelName="ABC"
    if (channelnum == "09"):
        channelName="NBC"
    if (channelnum == "31"):
        channelName="FOX"
    if (channelnum == "59"):
        channelName="ION"
    return render_template('tv1.html', ch=channelnum, name=channelName, volume=volume)

if __name__ == '__main__':
    app.debug=True
    app.run(host='0.0.0.0', port=8090)
