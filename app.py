from flask import Flask, render_template, request
from functions import get_all_window_titles, get_window_text, match_title, get_window_process_name
import functions
import os
import json
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers import interval
import argparse

ap = argparse.ArgumentParser()
ap.add_argument('-p', '--port', help='Specify which port should PTE II be running on.')
args = ap.parse_args()

bs = BackgroundScheduler()

app = Flask(__name__)

config = {
    'hwnd': 0,
    'capture_format': r'%title% - %artist%',
    'output_format': r'♫ %title% - %artist%',
    'txt': False,
    'txt_interval': 1,
    'filter': '',
}

print('载入设置文件……', end='')
try:
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.json'), 'r', encoding='utf8') as fp:
        config_from_file = dict(json.load(fp))
    for k, v in config_from_file.items():
        config[k] = v
    print('成功')
except:
    print('目前没有配置文件或已损坏无法读取，跳过。')

print(f'\n请访问 http://127.0.0.1:{args.port or 14514} 打开设置界面')

@app.route('/')
def index():
    hwnd = config['hwnd']
    title = ''
    if hwnd != 0:
        process_name, _ = get_window_process_name(hwnd)
        if process_name in functions.ignore_process_list:
            config['hwnd'] = 0
        else:
            title = get_window_text(hwnd)
    return render_template('index.htm', cfg=config, title=title)

@app.route('/search/', methods = ['GET', 'POST'])
def search():
    ctx = get_all_window_titles()
    if request.method == 'POST':
        keyword = request.form.get('filter', '', type=str)
        if keyword != '':
            ctx = [item for item in ctx if any(keyword.lower() in str(value).lower() for value in item.values())]
            config['filter'] = keyword
    return render_template('titletable.htm', ctx=ctx)

@app.route('/titletext')
def get_title():
    if config['hwnd'] != 0:
        try:
            title = get_window_text(config['hwnd'])[1:-1]
            output = output_title(title)
            return render_template('title.htm', op=output)
        except:
            return '', 404
    return '', 400

@app.route('/title')
def show_title():
    return render_template('showtitle.htm')

@app.route('/sethwnd/<int:hwnd>')
def dev_test(hwnd=None):
    if hwnd:
        try:
            title = get_window_text(hwnd)[1:-1]
        except:
            title = ''
        ctx = {
            'title': title
        }
        config['hwnd'] = hwnd
        return render_template('hwndsettings.htm', hwnd=hwnd, ctx=ctx, cfg=config)
    return '', 404

@app.route('/previewcp', methods = ['POST'])
def preview_capture_pattern():
    capture_pat = request.form.get('cp')
    title = request.form.get('title')
    match_dict = match_title(capture_pat, title)
    config['capture_format'] = capture_pat
    output = output_title(title)

    return render_template('previewcp.htm', match_dict=match_dict, op=output)

@app.route('/previewop', methods = ['POST'])
def preview_output_pattern():
    output_pat = request.form.get('op').lower()
    title = request.form.get('title')
    config['output_format'] = output_pat
    output = output_title(title)

    return render_template('previewop.htm', op=output)

def output_title(title):
    output = config['output_format']
    try:
        for key, value in match_title(config['capture_format'], title).items():
            output = output.replace(f'%{key.lower()}%', value)
    except:
        pass
    # 如果完全没有变化，则不输出内容
    if output == config['output_format']:
        output = ''
    return output

def output_to_txt_file():
    title = get_window_text(config['hwnd'])[1:-1]
    output = output_title(title)
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'music_title.txt'), 'w+', encoding='utf8') as fp:
        fp.write(output)

bs_trigger = interval.IntervalTrigger(seconds=int(config['txt_interval']))
bs.add_job(output_to_txt_file, trigger=bs_trigger, misfire_grace_time=5)

@app.route('/save', methods = ['POST'])
def save_config():
    global bs
    if config['hwnd'] != 0:
        txt = request.form.get('txt', '')
        config['txt'] = True if txt == 'on' else False

        if config['txt']:
            if not bs.running:
                bs.start()
        else:
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'music_title.txt'), 'w+', encoding='utf8') as fp:
                fp.write('')
            if bs.running:
                bs.shutdown()

        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.json'), 'w+', encoding='utf8') as fp:
            json.dump(config, fp, ensure_ascii=False)

    return render_template('save.htm', cfg=config)

if __name__ == '__main__':
    app.run(port=args.port or 14514)