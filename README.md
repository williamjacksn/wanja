Wanja is a blog engine.

## Getting started

Copy `settings.cfg.example` to `settings.cfg` and make the necessary changes. Set an environment variable `SETTINGS_FILE` to the path to `settings.cfg`:

    export SETTINGS_FILE=settings.cfg

Launch with `gunicorn wanja:app`.

## Adding content

Store posts in `posts/2014/07/02/post-slug.md`, changing the year, month, day, and file name as appropriate. Such a post will be served at `http://example.com/2014/07/02/post-slug`.

### Post format

The minimum viable post has the following content:

    Post Title
    ==========
    Published: 2014-07-02 11:01:00
    
    Post content.

The first line contains the title of the post. The second line contains an arbitrary separator. It can be anything. Everything after the separator line but before the first empty line is metadata.

Everything after the first empty line is the body of the post in Markdown format.

### Metadata

Metadata is in the form `Name: value`. `Published` is the only required metadata and should be in the date/time format shown above. All metadata will be available for use in templates. For example, if you specify this metadata:

    Tags: this, that, other

then in a template you can refer to `{{ post.tags }}` to get that content.

### Images in posts

Host your images somewhere else.
