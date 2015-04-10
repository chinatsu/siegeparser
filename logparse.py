from flask import Flask, request, render_template, redirect, url_for
from werkzeug import secure_filename
from parser import parse
import os, re

UPLOAD_FOLDER = '/srv/http/kawaii.desi/flask/parser/logs'
ALLOWED_EXTENSIONS = set(['txt'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
def getLogfiles():
    fileRegex2 = re.compile('GuildLog_(?P<ldate>\d{8})')
    files = sorted([ f for f in os.listdir(app.config['UPLOAD_FOLDER']) if os.path.isfile(os.path.join(UPLOAD_FOLDER,f)) ], reverse=True)
    logfiles = []
    for file in files:
        yay2 = fileRegex2.match(file)
        dateformat2 = yay2.group('ldate')[:4] + '-' + yay2.group('ldate')[4:-2] + '-' + yay2.group('ldate')[-2:]
        logfiles.append(dateformat2)
    return logfiles

#@app.route('/upload', methods=['GET', 'POST'])
#def upload_file():
#    if request.method == 'POST':
#        file = request.files['file']
#        if file and allowed_file(file.filename):
#            fileRegex = re.compile('GuildLog_(?P<cdate>\d{8})')
#            if fileRegex.match(file.filename):
#                filename = secure_filename(file.filename)
#                yay = fileRegex.match(file.filename)
#                dateformat = yay.group('cdate')[:4] + '-' + yay.group('cdate')[4:-2] + '-' + yay.group('cdate')[-2:]
#                if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
#                    return redirect(url_for('parser',cdate=dateformat))
#                else:
#                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#                    confCheck, confInt = check_confidence(filename)
#                    if confInt == 0:
#                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#                        return redirect(url_for('error', error=str(confInt)))
#                    else:
#                        return redirect(url_for('parser', cdate=dateformat))
#    return '''
#    <!doctype html>
#    <title>Upload new log</title>
#    <h1>Upload new log</h1>
#    <form action="" method=post enctype=multipart/form-data>
#      <p><input type=file name=file>
#         <input type=submit value=Upload>
#    </form>
#    '''

def check_confidence(filename):
    cRegex = re.compile('GuildLog_(?P<cdate2>\d{8})')
    cMatch = cRegex.match(filename)
    cRes, cChar = parse.getResults('GuildLog_' + cMatch.group('cdate2') + '.txt')
    confidence = parse.confidence(cRes, cChar)
    if confidence >= 5:
        return False, confidence
    else:
        return True, confidence

@app.route('/')
def index():
    logfiles = getLogfiles()
    return render_template('parseindex.html', logfiles = logfiles)

@app.route('/recent')
def mostrecent():
    logfiles = getLogfiles()
    return redirect(url_for('parser',cdate=logfiles[0]))

@app.route('/error/<error>')
def error(error):
    return render_template('errorpage.html', error=error)
@app.route('/g/<cdate>')
def parser(cdate):
    ddate = cdate.replace('-','')
    if os.path.isfile('/srv/http/kawaii.desi/flask/parser/logs/GuildLog_' + ddate + '.txt'):
        guilds,characters = parse.getResults('GuildLog_' + ddate + '.txt')
        confInt = parse.confidence(guilds,characters)
        guildjson, playerjson = parse.sortedLists(guilds,characters)
        return render_template('parser.html', guildjson=guildjson, playerjson=playerjson, confInt=str(confInt))

if not app.debug:
    import logging
    file_handler = logging.FileHandler('log.txt')
    file_handler.setLevel(logging.WARNING)
    app.logger.addHandler(file_handler)

if __name__ == '__main__':
    #app.run()
    app.run(debug=True, port=4000, host='0.0.0.0')
