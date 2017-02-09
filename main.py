#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import jinja2
import os

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader= jinja2.FileSystemLoader(template_dir), autoescape=True)


class Handler(webapp2.RequestHandler):
    def write(self, *args, **kwargs):
        self.response.out.write(*args, **kwargs)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kwargs):
        self.write(self.render_str(template, ** kwargs))


class Post(db.Model):
    title = db.StringProperty(required=True)
    body = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)


class MainHandler(Handler):
    def get(self):
        page = self.request.get('page')
        page = page and int(page)
        total = get_posts().count()
        if not page:
            posts = get_posts()
            self.render("main.html", posts=posts, total=total, page=1)
        else:
            posts = get_posts(offset=(5*page - 5))
            self.render("main.html", posts=posts, total=total, page=page)



class NewPostHandler(Handler):
    def get(self):
        self.render("newpost.html")

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            p = Post(title=title, body=body)
            p.put()
            self.redirect("/blog/{}".format(p.key().id()))

        else:
            error = "Please fill in the fields"
            self.render_posting(error=error, title=title, body=body)


class BlogHandler(Handler):
    def get(self, id):
        post = Post.get_by_id(int(id))
        self.render("blog.html", post=post)


def get_posts(limit=5, offset=0):
    posts = db.GqlQuery("SELECT * FROM Post "
                        "ORDER BY created DESC "
                        "LIMIT {} OFFSET {} ".format(limit, offset))
    return posts

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/newpost', NewPostHandler),
    (webapp2.Route('/blog/<id:\d+>', BlogHandler)),
], debug=True)

