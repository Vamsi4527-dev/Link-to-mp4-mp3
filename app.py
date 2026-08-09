# app.py
# Made using Flask+yt-dlp

from flask import Flask, render_template, request, send_file
from yt_dlp import YoutubeDL
import os
import uuid
import subprocess

app = Flask(__name__)

# folder where we will temporarily save the downloaded files
DOWNLOAD_FOLDER="/tmp"

# create the folder if it does not already exist
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)


# This function checks if a link belongs to Instagram
def is_instagram_link(link):
    link=link.lower()
    if "instagram.com/reel" in link or "instagram.com/p/" in link or "instagram.com/tv" in link:
        return True
    return False


# This function checks if a link belongs to Facebook
def is_facebook_link(link):
    link=link.lower()
    if "facebook.com" in link:
        return True
    return False


# This function checks if a link belongs to X
def is_twitter_link(link):
    link=link.lower()
    if "twitter.com" in link or "x.com" in link:
        return True
    return False


# This function makes error messages easier to read on the webpage
def clean_error(error):
    error_text=str(error)

    # Give a nicer message when Instagram needs login cookies
    if "cookies" in error_text.lower() and "instagram" in error_text.lower():
        return "Instagram needs login cookies to access this post. Please add a valid cookies.txt file."

    return error_text


# This function just fetches info about the video (title, thumbnail, etc.)
# without actually downloading it. Used for the "preview" step.
def get_video_info(link):
    options={"quiet":True}

    # if we have a cookies.txt file saved next to app.py, use it
    cookie_file=os.path.join(os.path.dirname(os.path.abspath(__file__)),"cookies.txt")
    if os.path.exists(cookie_file):
        options["cookiefile"]=cookie_file

    with YoutubeDL(options) as ydl:
        info=ydl.extract_info(link,download=False)

    video_info={
        "title":info.get("title","Video"),
        "thumbnail":info.get("thumbnail"),
        "author":info.get("uploader","Unknown"),
        "length":info.get("duration",0)
    }

    return video_info


# This function actually downloads the video (and converts to mp3 if needed)
def download_video(link,file_type):

    # give every download a random unique name so files don't overwrite each other
    unique_name=str(uuid.uuid4())
    save_path=os.path.join(DOWNLOAD_FOLDER,unique_name+".%(ext)s")

    # decide which format we want to download depending on mp3 or mp4
    if file_type=="mp3":
        options={
            "outtmpl":save_path,
            "format":"bestaudio/best",
            "quiet":True
        }
    else:
        options={
            "outtmpl":save_path,
            "format":"bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
            "merge_output_format":"mp4",
            "quiet":True
        }

    # use cookies.txt if it exists (needed for some Instagram links)
    cookie_file=os.path.join(os.path.dirname(os.path.abspath(__file__)),"cookies.txt")
    if os.path.exists(cookie_file):
        options["cookiefile"]=cookie_file

    # download the video using yt-dlp
    with YoutubeDL(options) as ydl:
        info=ydl.extract_info(link,download=True)
        downloaded_file=ydl.prepare_filename(info)

    # if the user wanted mp4, we are already done
    if file_type=="mp4":
        return downloaded_file

    # if the user wanted mp3, we still need to convert using ffmpeg

    mp3_file=os.path.join(DOWNLOAD_FOLDER,unique_name+".mp3")

    # check if there is a local ffmpeg.exe inside the project folder
    project_folder=os.path.dirname(os.path.abspath(__file__))
    local_ffmpeg=os.path.join(project_folder,"ffmpeg-8.0.1-essentials_build","bin","ffmpeg.exe")

    if os.path.exists(local_ffmpeg):
        ffmpeg_path=local_ffmpeg
    else:
        ffmpeg_path="ffmpeg"   # use ffmpeg from system PATH

    # Run ffmpeg to convert the downloaded file into mp3
    # NOTE: each part of the command must be a separate item in the list,
    # otherwise ffmpeg cannot understand the command (this was the bug before!)
    command = [ffmpeg_path, "-i", downloaded_file, "-vn", "-acodec", "libmp3lame", mp3_file, "-y"]
    result = subprocess.run(command, capture_output=True, text=True)

    # check if the conversion actually worked before continuing
    if result.returncode!=0 or not os.path.exists(mp3_file):
        raise Exception("Something went wrong while converting to mp3. Make sure ffmpeg is installed.")

    # delete the original video/audio file since we only need the mp3 now
    if os.path.exists(downloaded_file) and downloaded_file!=mp3_file:
        os.remove(downloaded_file)

    return mp3_file


# ----------------------PAGE ROUTES----------------------

@app.route("/")
def home():
    return render_template("main.html")


@app.route("/instagram")
def instagram_page():
    return render_template("index2.html")


@app.route("/facebook")
def facebook_page():
    return render_template("index3.html")


@app.route("/twitter")
def twitter_page():
    return render_template("index4.html")


# ----------------------INSTAGRAM----------------------

@app.route("/instagram/api",methods=["POST"])
def instagram_preview():
    try:
        link=request.form.get("link_input")
        file_type=request.form.get("file_type")

        if not is_instagram_link(link):
            return render_template("error.html",error_message="Invalid Instagram link")

        info = get_video_info(link)

        return render_template(
            "result2.html",
            title=info["title"],
            thumbnail_url=info["thumbnail"],
            link_input=link,
            ftype=file_type
        )

    except Exception as e:
        return render_template("error.html", error_message=clean_error(e))


@app.route("/instagram/download")
def instagram_download():
    try:
        link = request.args.get("link")
        file_type = request.args.get("type","mp4")

        file_path = download_video(link,file_type)

        return send_file(file_path,as_attachment=True)

    except Exception as e:
        return render_template("error.html",error_message=clean_error(e))


# ----------------------FACEBOOK----------------------

@app.route("/facebook/api",methods=["POST"])
def facebook_preview():
    try:
        link=request.form.get("link_input")
        file_type=request.form.get("file_type")

        if not is_facebook_link(link):
            return render_template("error.html",error_message="Invalid Facebook link")

        info=get_video_info(link)

        return render_template(
            "result3.html",
            title=info["title"],
            thumbnail_url=info["thumbnail"],
            link_input=link,
            ftype=file_type
        )

    except Exception as e:
        return render_template("error.html", error_message=clean_error(e))


@app.route("/facebook/download")
def facebook_download():
    try:
        link=request.args.get("link")
        file_type=request.args.get("type","mp4")

        file_path=download_video(link,file_type)

        return send_file(file_path,as_attachment=True)

    except Exception as e:
        return render_template("error.html",error_message=clean_error(e))


# ----------------------X----------------------

@app.route("/twitter/api",methods=["POST"])
def twitter_preview():
    try:
        link=request.form.get("link_input")
        file_type=request.form.get("file_type")

        if not is_twitter_link(link):
            return render_template("error.html",error_message="Invalid Twitter / X link")

        info=get_video_info(link)

        return render_template(
            "result4.html",
            title=info["title"],
            thumbnail_url=info["thumbnail"],
            link_input=link,
            ftype=file_type
        )

    except Exception as e:
        return render_template("error.html",error_message=clean_error(e))


@app.route("/twitter/download")
def twitter_download():
    try:
        link=request.args.get("link")
        file_type=request.args.get("type","mp4")

        file_path=download_video(link,file_type)

        return send_file(file_path,as_attachment=True)

    except Exception as e:
        return render_template("error.html",error_message=clean_error(e))



if __name__=="__main__":
    app.run(debug=True)
