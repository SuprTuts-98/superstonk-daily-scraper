import praw
from praw.models import InlineImage, InlineGif, InlineVideo
import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_gradient_magnitude
from urllib.parse import quote_plus
import pause
from datetime import datetime
from calendar import monthrange
import re

reddit = praw.Reddit(
    client_id='your client id',
    client_secret='your client secret',
    password='your password',
    user_agent='sample text',
    username="your username"
)

def gen_cloud():
    # Originally was going to have it scrape the top 10 posts from the last 24 hours too, but I hit a rate limit from reddits api
    # for post in reddit.subreddit('superstonk').top(time_filter="day", limit=10):
        # submission = reddit.submission(id=post)

        # comments = []

        # submission.comments.replace_more(limit=None)
        # for comment in submission.comments.list():
            # comments.append(comment.body)

        # def convert(lst):
            # return ([i for item in lst for i in item.split()])

        # words = convert(comments)
        # words = [x.replace(',', '') for x in words]
        # words = [x.replace('https', '') for x in words]
        # words = [x.replace('will', '') for x in words]
        # textfile = open("new_text.txt", "a+", encoding="utf-8")
        # for word in words:
            # textfile.write(word + " ")
        # textfile.close()
        
    submission = reddit.subreddit('superstonk').sticky()

    comments = []

    submission.comments.replace_more(limit=None)
    for comment in submission.comments.list():
        comments.append(comment.body)

    def convert(lst):
        return ([i for item in lst for i in item.split()])

    words = convert(comments)
    words = [x.replace(',', '') for x in words]
    words = [x.replace('https', '') for x in words]
    words = [x.replace('will', '') for x in words]
    probably could just store this in a list somehow, but I couldn't figure out how to get the wordcloud to generate from a list
    textfile = open("new_text.txt", "a+", encoding="utf-8")
    for word in words:
        textfile.write(word + " ")
    textfile.close()
    
    
    # borrowed this section
    from wordcloud import WordCloud, ImageColorGenerator
    d = os.path.dirname(__file__) if "__file__" in locals() else os.getcwd()
    text = open(os.path.join(d, 'new_text.txt'), encoding="utf-8").read()
    rocket_color = np.array(Image.open(os.path.join(d, "rocket_mask.png")))
    rocket_color = rocket_color[::3, ::3]
    rocket_mask = rocket_color.copy()
    rocket_mask[rocket_mask.sum(axis=2) == 0] = 255
    edges = np.mean([gaussian_gradient_magnitude(rocket_color[:, :, i] / 255., 2) for i in range(3)], axis=0)
    rocket_mask[edges > .08] = 255
    wc = WordCloud(max_words=2000, mask=rocket_mask, max_font_size=70, random_state=42, relative_scaling=1, width=1414, height=2841, min_font_size=2, min_word_length=2, scale=4)

    wc.generate(text)

    image_colors = ImageColorGenerator(rocket_color)
    wc.recolor(color_func=image_colors)
    wc.to_file("wordcloud.png")   
    f = open('new_text.txt', 'r+')
    f.truncate(0)

def make_submission():
    flair_id = "31ecc882-8cbd-11eb-877e-0e2a5e5fc207"
    image = "path/to/wordcloud.png"
    title = "A word cloud made from all of the comments from yesterdays Daily"
    sub = reddit.subreddit('superstonk')
    sub.submit_image(title, image,flair_id=flair_id)
    
while True:
    # There's definitely a better way to do this, dealing with the dates and all
    now = re.split('-|:|\.| ',str(datetime.now()))
    year = int(now[0])
    month = int(now[1])
    day = int(now[2])
    hour = int(now[3])
    minute = int(now[4])
    sec = int(now[5])
    prev_day = day - 1
    prev_month = month
    if day == 1:
        prev_month = month - 1
        prev_day = calendar.monthrange(year,prev_month)
    pause.until(datetime(year, month, day, 1, 55, 0))
    gen_cloud()
    # Watermarks image with yesterdays date
    im = Image.open("wordcloud.png")
    width, height = im.size
    draw = ImageDraw.Draw(im)
    text = "Made from the {}/{}/{} daily thread".format(year,prev_month,prev_day)
    font = ImageFont.truetype('arialbd.ttf', 100)
    textwidth, textheight = draw.textsize(text,font)
    margin = 90
    x = width - textwidth - margin
    y = height - textheight - margin
    draw.text((x,y), text, font=font)
    im.show()
    im.save('wordcloud.png')
    pause.until(datetime(year, month, day, 6, 0, 0))
    make_submission()