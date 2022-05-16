# Read-only instance
import praw as praw
import re
import pandas as pd

# Instiantie PRAW
reddit_read_only = praw.Reddit(client_id="SvCJdstpGCed5uhK7XJyIw",  # your client id
                               client_secret="avt5nZXQqLbwyUvyWns6L90I_8M-EQ",  # your client secret
                               user_agent="inforetrieval")  # your user agent

# Getting Top 3 subreddits
subreddit = reddit_read_only.subreddit("TrueFilm")
subreddit1 = reddit_read_only.subreddit("MovieSuggestions")
subreddit2 = reddit_read_only.subreddit("movies")

postsl = []
# Getting Top Posts
posts = subreddit.top(limit=None)
postsl.append(posts)
postsl.append(subreddit1.top(limit=None))
postsl.append(subreddit2.top(limit=None))

# Storing Post Related Information
posts_dict = {"Post Text": [], "Comments": []}
posts_replies = {"Comments": [], "Replies": []}

# Looping Through the post
for posts in postsl:
    for post in posts:
        post = reddit_read_only.submission(id=post.id)
        post.comments.replace_more(limit=0)
        if len(post.comments) < 10:
            continue
        count = 0
        # Looping through the comments in each post
        for commentid, comment in enumerate(post.comments.list()):
            posts_dict["Post Text"].append(re.sub("&.*", " ", post.selftext))
            posts_dict["Comments"].append(re.sub("&.*", " ", comment.body))
            title = post.title.replace("/", " ")
            if len(comment.replies) > 0:
                # Looping through the Replies for each comment
                for replyid, reply in enumerate(comment.replies):
                    posts_replies["Comments"].append(re.sub("&.*", " ", comment.body))
                    posts_replies["Replies"].append(re.sub("&.*", " ", reply.body))
                    if (replyid + 1) % 10 == 0:
                        top_posts = pd.DataFrame(posts_replies)
                        top_posts.to_csv("csv/" + title[0:min(len(title), 50)] + "Replies" + str(replyid + 1) + ".csv",
                                         index=True)
                        posts_replies["Comments"] = []
                        posts_replies["Replies"] = []
                # Storing Replies
                top_posts = pd.DataFrame(posts_replies)
                top_posts.to_csv("csv/" + title[0:min(len(title), 50)] + "Replies" + str(replyid + 1) + ".csv",
                                 index=True)
                posts_replies["Comments"] = []
                posts_replies["Replies"] = []

            # Batching logic to store post comments in the documents
            if (commentid + 1) % 10 == 0:
                top_posts = pd.DataFrame(posts_dict)
                top_posts.to_csv("csv/" + title[0:min(len(title), 50)] + str(commentid + 1) + ".csv", index=True)
                posts_dict["Post Text"] = []
                posts_dict["Comments"] = []

        # Convert the information to csv document
        top_posts.to_csv("csv/" + title[0:min(len(title), 50)] + str(commentid + 1) + ".csv", index=True)
        posts_dict["Post Text"] = []
        posts_dict["Comments"] = []