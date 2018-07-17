import codecs
import datetime
import flask
import hashlib
import markdown
import os
import smartypants

app = flask.Flask(__name__)
app.config.from_envvar('SETTINGS_FILE')
cache = {}
etags = {}


def most_recent_posts(limit=1):
    all_paths = []
    posts_root = os.path.join(app.root_path, 'posts')
    for root, dirs, files in os.walk(posts_root):
        for fn in files:
            if not fn.endswith('.md'):
                continue
            all_paths.append(os.path.join(root, fn))
    all_paths.sort(reverse=True)
    if limit == 0:
        paths = all_paths
    else:
        paths = all_paths[:limit]
    return [parse_post(path) for path in sorted(paths, reverse=True)]


def get_posts_in_folder(folder):
    paths = []
    for root, dirs, files in os.walk(folder):
        for fn in files:
            if not fn.endswith('.md'):
                continue
            paths.append(os.path.join(root, fn))
    return [parse_post(path) for path in paths]


def sort_posts(posts, sort_key, reverse=False):
    def _sort_key(record):
        return record.get(sort_key)
    return sorted(posts, key=_sort_key, reverse=reverse)


def parse_datetime(date_string):
    fmt = '%Y-%m-%d %H:%M:%S'
    if 'm' in date_string:
        fmt = '%Y-%m-%d %I:%M:%S%p'
    return datetime.datetime.strptime(date_string, fmt)


def get_slug_from_path(path):
    return os.path.basename(path)[:-3]


def get_post_url(_post):
    p = _post['published']
    return '/{}/{:02}/{:02}/{}'.format(p.year, p.month, p.day, _post['slug'])


def first_alpha_char(string):
    if not string:
        return ''
    for char in string:
        if char.isalpha():
            return char
    return string[0]


def parse_post(src_path):
    _post = {}
    with codecs.open(src_path, 'r', 'utf-8') as src:
        raw_title = src.readline().strip()
        smarty_title = smartypants.smartypants(raw_title)
        _post['title'] = flask.Markup(smarty_title)
        _post['title_first_char'] = first_alpha_char(raw_title).upper()
        _ = src.readline().strip()
        while True:
            meta = src.readline().strip()
            if not meta:
                break
            if ':' in meta:
                meta_key, sep, meta_val = meta.partition(':')
                _post[meta_key.lower().strip()] = meta_val.strip()
        mkd = markdown.markdown(src.read())
        _post['body'] = smartypants.smartypants(mkd)
    _post['slug'] = get_slug_from_path(src_path)
    _post['published'] = parse_datetime(_post['published'])
    _post['year'] = _post.get('published').year
    _post['url'] = get_post_url(_post)
    return _post


@app.route('/')
def index():
    if flask.request.path in etags:
        etag = etags.get(flask.request.path)
        if 'if-none-match' in flask.request.headers:
            req_etag = flask.request.headers.get('if-none-match')
            if etag == req_etag:
                return flask.Response(status=304)
    if flask.request.path in cache:
        return cache.get(flask.request.path)
    posts = most_recent_posts(app.config.get('POSTS_ON_FRONT_PAGE'))
    template = flask.render_template('posts.html', posts=posts)
    response = flask.make_response(template)
    etag = hashlib.md5(template.encode('utf-8')).hexdigest()
    etags.setdefault(flask.request.path, etag)
    response.headers['ETag'] = etag
    return cache.setdefault(flask.request.path, response)


@app.route('/alpha')
def alpha_index():
    if flask.request.path in etags:
        etag = etags.get(flask.request.path)
        if 'if-none-match' in flask.request.headers:
            req_etag = flask.request.headers.get('if-none-match')
            if etag == req_etag:
                return flask.Response(status=304)
    if flask.request.path in cache:
        return cache.get(flask.request.path)
    posts = sort_posts(most_recent_posts(limit=0), 'title')
    template = flask.render_template('alpha_index.html', posts=posts)
    response = flask.make_response(template)
    etag = hashlib.md5(template.encode('utf-8')).hexdigest()
    etags.setdefault(flask.request.path, etag)
    response.headers['ETag'] = etag
    return cache.setdefault(flask.request.path, response)


@app.route('/chrono')
def chrono_index():
    if flask.request.path in etags:
        etag = etags.get(flask.request.path)
        if 'if-none-match' in flask.request.headers:
            req_etag = flask.request.headers.get('if-none-match')
            if etag == req_etag:
                return flask.Response(status=304)
    if flask.request.path in cache:
        return cache.get(flask.request.path)
    posts = sort_posts(most_recent_posts(limit=0), 'published', reverse=True)
    template = flask.render_template('chrono_index.html', posts=posts)
    response = flask.make_response(template)
    etag = hashlib.md5(template.encode('utf-8')).hexdigest()
    etags.setdefault(flask.request.path, etag)
    response.headers['ETag'] = etag
    return cache.setdefault(flask.request.path, response)


@app.route('/<int:y>/<int:m>/')
def month_index(y, m):
    if flask.request.path in etags:
        etag = etags.get(flask.request.path)
        if 'if-none-match' in flask.request.headers:
            req_etag = flask.request.headers.get('if-none-match')
            if etag == req_etag:
                return flask.Response(status=304)
    if flask.request.path in cache:
        return cache.get(flask.request.path)
    p = app.root_path
    m_path = '{}/posts/{:04}/{:02}'.format(p, y, m)
    if not os.path.exists(m_path):
        flask.abort(404)
    posts = sort_posts(get_posts_in_folder(m_path), 'published', reverse=True)
    template = flask.render_template('posts.html', posts=posts)
    response = flask.make_response(template)
    etag = hashlib.md5(template.encode('utf-8')).hexdigest()
    etags.setdefault(flask.request.path, etag)
    response.headers['ETag'] = etag
    return cache.setdefault(flask.request.path, response)


@app.route('/<int:y>/<int:m>/<int:d>/<slug>')
def post(y, m, d, slug):
    if flask.request.path in etags:
        etag = etags.get(flask.request.path)
        if 'if-none-match' in flask.request.headers:
            req_etag = flask.request.headers.get('if-none-match')
            if etag == req_etag:
                return flask.Response(status=304)
    if flask.request.path in cache:
        return cache.get(flask.request.path)
    p = app.root_path
    src_path = '{}/posts/{:04}/{:02}/{:02}/{}.md'.format(p, y, m, d, slug)
    _post = parse_post(src_path)
    if _post:
        template = flask.render_template('post.html', post=_post)
        response = flask.make_response(template)
        etag = hashlib.md5(template.encode('utf-8')).hexdigest()
        etags.setdefault(flask.request.path, etag)
        response.headers['ETag'] = etag
        return cache.setdefault(flask.request.path, response)
    flask.abort(404)


@app.route('/rss.xml')
def rss():
    if flask.request.path in etags:
        etag = etags.get(flask.request.path)
        if 'if-none-match' in flask.request.headers:
            req_etag = flask.request.headers.get('if-none-match')
            if etag == req_etag:
                return flask.Response(status=304)
    if flask.request.path in cache:
        return cache.get(flask.request.path)
    posts = most_recent_posts(limit=20)
    template = flask.render_template('rss.xml', posts=posts)
    etag = hashlib.md5(template.encode('utf-8')).hexdigest()
    etags.setdefault(flask.request.path, etag)
    response = flask.make_response(template)
    response.headers['ETag'] = etag
    response.headers['Content-Type'] = 'application/rss+xml'
    return cache.setdefault(flask.request.path, response)


def main():
    app.run(host='0.0.0.0', debug=True)

if __name__ == '__main__':
    main()
